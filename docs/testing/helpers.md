```{ "name": "change tag description" }
sed -i 's/"this is an autotag rule created by crossplane"/"this is an autotag rule created by crossplane ABC123"/' /workspaces/$RepositoryName/config_as_code/main.tf
git add /workspaces/$RepositoryName/config_as_code/main.tf
git commit -m "change tag description"
git push
```

```{ "name": "wait for crossplane to sync" }
sleep 60
```

```{ "name": "reset tag description" }
sed -i 's/"this is an autotag rule created by crossplane ABC123"/"this is an autotag rule created by crossplane"/' /workspaces/$RepositoryName/config_as_code/main.tf
git add /workspaces/$RepositoryName/config_as_code/main.tf
git commit -m "reset tag description"
git push
```

```{ "name": "remove comments from tag" }
sed -i '1d;$d' /workspaces/$RepositoryName/config_as_code/main.tf
git add /workspaces/$RepositoryName/config_as_code/main.tf
git commit -m "remove comments from tag - make ready for sync"
git push
```
