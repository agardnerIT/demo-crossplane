```{ "name": "change tag description" }
sed -i 's/"this is an autotag rule created by crossplane"/"this is an autotag rule created by crossplane ABC123"/' /workspaces/$RepositoryName/config_as_code/main.tf
git add /workspaces/$RepositoryName/config_as_code/main.tf
git commit -m "change tag description"
git push
```

```{ "name": "wait for crossplane to sync" }
sleep 120
```

```{ "name": "reset tag description" }
sed -i 's/"this is an autotag rule created by crossplane ABC123"/"this is an autotag rule created by crossplane"/' /workspaces/$RepositoryName/config_as_code/main.tf
git add /workspaces/$RepositoryName/config_as_code/main.tf
git commit -m "reset tag description"
git push
```

```py { "name": "toggle terraform code" }
import os
folder_name = os.environ.get("RepositoryName", "")

lines = []

# Open file to read existing content
with open(f"/workspaces/{folder_name}/config_as_code/main.tf", mode="r") as terraform_file:
    lines = terraform_file.readlines()
    number_of_lines = len(lines)
    first_line_stripped = lines[0].strip()
    last_line_stripped = lines[number_of_lines-1].strip()

    # If terraform code is valid, comment out
    if first_line_stripped.startswith("resource"):
        lines.insert(0, "/*\n")
        lines.append("*/")
    # Else if terraform code is currently commented out, re-enable it
    elif first_line_stripped == "/*" and last_line_stripped == "*/":
        lines.pop(number_of_lines-1)
        lines.pop(0)

# Re-open file to write new lines
with open(f"/workspaces/{folder_name}/config_as_code/main.tf", mode="w") as terraform_file:    
    terraform_file.writelines(lines)
```

```sh { "name": "commit toggled code" }
git add /workspaces/$RepositoryName/config_as_code/main.tf
git commit -m "toggle terraform code"
git push
```

```{ "name": "remove comments from tag" }
sed -i '1d;$d' /workspaces/$RepositoryName/config_as_code/main.tf
git add /workspaces/$RepositoryName/config_as_code/main.tf
git commit -m "remove comments from tag - make ready for sync"
git push
```
