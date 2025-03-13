```{"name": "change tag description"}
sed -i 's/"this is an autotag rule created by crossplane"/"this is an autotag rule created by crossplane ABC123"/' /workspaces/$RepositoryName/config_as_code/main.tf
git add /workspaces/$RepositoryName/config_as_code/main.tf
git commit -m "update auto-tag rule"
git push
```

```{"name": "wait for crossplane to sync"}
sleep 60
```

```{"name": "reset tag description"}
sed -i 's/"this is an autotag rule created by crossplane ABC123"/"this is an autotag rule created by crossplane"/' /workspaces/$RepositoryName/config_as_code/main.tf
git add /workspaces/$RepositoryName/config_as_code/main.tf
git commit -m "reset auto-tag rule"
git push
```