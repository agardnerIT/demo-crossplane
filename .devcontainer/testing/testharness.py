import subprocess
import os, threading
from helpers import *

DT_API_TOKEN_TESTING = os.getenv("DT_API_TOKEN_TESTING","")

# Use the main token
# To create short lived tokens
# To run the test harness
# Use these short-lived tokens during the test harness.
DT_TENANT_APPS, DT_TENANT_LIVE = build_dt_urls(dt_env_id=DT_ENVIRONMENT_ID, dt_env_type=DT_ENVIRONMENT_TYPE)
DT_API_TOKEN_TO_USE = create_dt_api_token(token_name="[devrel e2e testing] DT_CROSSPLANE_E2E_TEST_TOKEN", scopes=["settings.read", "settings.write", "metrics.ingest"], dt_rw_api_token=DT_API_TOKEN_TESTING, dt_tenant_live=DT_TENANT_LIVE)
store_env_var(key="DT_API_TOKEN", value=DT_API_TOKEN_TO_USE)

run_command(["kubectl", "-n", "crossplane-system", "create", "secret", "generic", "dt-details", f"--from-literal=DYNATRACE_ENV_URL={DT_TENANT_LIVE}", f"--from-literal=DYNATRACE_API_TOKEN={DT_API_TOKEN_TO_USE}"])

# Install Crossplane
run_command(["helm", "install", "crossplane", "--namespace", "crossplane-system", "--wait", "crossplane-stable/crossplane", "--values", "crossplane-values.yaml"])
run_command(["sleep", "5"]) # small sleep while objects are created in k8s
run_command(["kubectl", "apply", "-f", "terraform-config.yaml"])
run_command(["sleep", "5"]) # small sleep while objects are created in k8s
    
# Create workspace (this tells crossplane to start monitoring this Git repo)
run_command(["kubectl", "apply", "-f", "workspace-remote.yaml"])
    
run_command(["kubectl", "-n", "crossplane-system", "wait", "pod", "--for", "condition=Ready", "-l", "pkg.crossplane.io/provider=provider-terraform"])
run_command(["kubectl", "-n", "crossplane-system", "wait", "--for", "condition=established", "--timeout=60s", "crd/providerconfigs.tf.upbound.io"])
run_command(["kubectl", "apply", "-f", "terraform-provider-config.yaml"])

steps = get_steps(f"/workspaces/{REPOSITORY_NAME}/.devcontainer/testing/steps.txt")
INSTALL_PLAYWRIGHT_BROWSERS = False

def run_command_in_background(step):
    command = ["runme", "run", step]
    with open("nohup.out", "w") as f:
        subprocess.Popen(["nohup"] + command, stdout=f, stderr=f)

# Installing Browsers for Playwright is a time consuming task
# So only install if we need to
# That means if running in non-dev mode (dev mode assumes the person already has everything installed)
# AND the steps file actually contains a playwright test (no point otherwise!)
if DEV_MODE == "FALSE":
    for step in steps:
        if "test_" in step:
            INSTALL_PLAYWRIGHT_BROWSERS = True

if INSTALL_PLAYWRIGHT_BROWSERS:
    subprocess.run(["playwright", "install", "chromium-headless-shell", "--only-shell", "--with-deps"])

for step in steps:
    step = step.strip()

    if step.startswith("//") or step.startswith("#"):
        print(f"[{step}] Ignore this step. It is commented out.")
        continue
    
    if "test_" in step:
        print(f"[{step}] This step is a Playwright test.")
        if DEV_MODE == "FALSE": # Standard mode. Run test headlessly
            output = subprocess.run(["pytest", "--capture=no", f"{TESTING_BASE_DIR}/{step}"], capture_output=True, text=True)
        else: # Interactive mode (when a maintainer is improving testing. Spin up the browser visually.
            output = subprocess.run(["pytest", "--capture=no", "--headed", f"{TESTING_BASE_DIR}/{step}"], capture_output=True, text=True)

        if output.returncode != 0 and DEV_MODE == "FALSE":
            logger.error(f"Must create an issue: {step} {output}")
            create_github_issue(output, step_name=step)
        else:
            print(output)
    else:
        output = subprocess.run(["runme", "run", step], capture_output=True, text=True)
        print(f"[{step}] | {output.returncode} | {output.stdout}")
        if output.returncode != 0 and DEV_MODE == "FALSE":
            logger.error(f"Must create an issue: {step} {output}")
            create_github_issue(output, step_name=step)
        else:
            print(output)
