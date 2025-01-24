import os
from utils import *

# TODO

CODESPACE_NAME = os.environ.get("CODESPACE_NAME", "")
GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY", "")
REPOSITORY_NAME = os.environ.get("RepositoryName", "")

MONACO_VERSION="v2.15.2"
JMETER_VERSION="5.6.3"
RUNME_CLI_VERSION = "3.10.2"


# Build DT environment URLs
DT_TENANT_APPS, DT_TENANT_LIVE = build_dt_urls(dt_env_id=DT_ENVIRONMENT_ID, dt_env_type=DT_ENVIRONMENT_TYPE)

# Create cluster
logger.info("Creating new cluster")
run_command(["kind", "create", "cluster", "--config", ".devcontainer/kind-cluster.yaml", "--wait", STANDARD_TIMEOUT])
run_command(["kubectl", "create", "namespace", "crossplane-system"])
run_command(["kubectl", "-n", "crossplane-system", "create", "secret", "generic", "dt-details", f"--from-literal=DYNATRACE_ENV_URL={DT_TENANT_LIVE}", f"--from-literal=DYNATRACE_API_TOKEN={DT_API_TOKEN}"])

# Install Crossplane
run_command(["helm", "repo", "add", "crossplane-stable", "https://charts.crossplane.io/stable"])
run_command(["helm", "repo", "update"])
run_command(["helm", "install", "crossplane", "--namespace", "crossplane-system", "--wait", "crossplane-stable/crossplane", "--values", "crossplane-values.yaml"])

run_command(["kubectl", "apply", "-f", "terraform-config.yaml"])
run_command(["sleep", "5"]) # small sleep while objects are created in k8s
run_command(["kubectl", "-n", "crossplane-system", "wait", "pod", "--for", "condition=Ready", "-l", "pkg.crossplane.io/provider=provider-terraform"])
run_command(["kubectl", "-n", "crossplane-system", "wait", "--for", "condition=established", "--timeout=60s", "crd/providerconfigs.tf.upbound.io"])
run_command(["kubectl", "apply", "-f", "terraform-provider-config.yaml"])


# replace placeholder with actual repo
do_file_replace(pattern="workspace-remote.yaml", find_string="GITHUB_REPOSITORY_PLACEHOLDER", replace_string=GITHUB_REPOSITORY)

# Create workspace (this tells crossplane to start monitoring this Git repo)
run_command(["kubectl", "apply", "-f", "workspace-remote.yaml"])


if CODESPACE_NAME.startswith("dttest-"):
    # Set default repository for gh CLI
    # Required for the e2e test harness
    # If it needs to interact with GitHub (eg. create an issue for a failed e2e test)
    run_command(["gh", "repo", "set-default", GITHUB_REPOSITORY])

    # Now set up a label, used if / when the e2e test fails
    # This may already be set (when demos are re-executed in repos)
    # so catch error and always return true
    # Otherwise the entire post-start.sh script could fail
    # We can do this as we know we have permission to this repo
    # (because we're the owner and testing it)
    run_command(["gh", "label", "create", "e2e test failed", "--force"])
    run_command(["pip", "install", "-r", f"/workspaces/{REPOSITORY_NAME}/.devcontainer/testing/requirements.txt", "--break-system-packages"])
    run_command(["python",  f"/workspaces/{REPOSITORY_NAME}/.devcontainer/testing/testharness.py"])

    # Testing finished. Destroy the codespace
    run_command(["gh", "codespace", "delete", "--codespace", CODESPACE_NAME, "--force"])
else:
    send_startup_ping(demo_name="demo-crossplane")