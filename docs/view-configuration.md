## See Tags in Dynatrace

`config_as_code/main.tf` contains a single auto-tag rule called `created-by-crossplane`.

That auto tag should now exist in your Dynatrace environment.

In Dynatrace:

* Press `ctrl + k`. Search for `settings`
* Go to `Settings > Tags > Automatically applied tags`

![auto tag rule](images/dt-auto-tag-screen.png)

## Make a Change

In the codespace:

* Open `config_as_code/main.tf`
* Change the `description from:

```
description = "this is an autotag rule created by crossplane"
```

to

```
description = "this is an autotag rule created by crossplane ABC123"
```

* Save that configuration back to your Git repository:

``` { "name": "git add terraform"}
git add config_as_code/main.tf
git commit -m "update auto-tag rule"
git push
```

Wait 1 minute (recall that Crossplane is configured to sync once per minute).

Refresh the Dynatrace UI.

Open the auto-tag rule and you should see the changes reflected.

![auto tag changed](images/dt-auto-tag-changed.png)

<div class="grid cards" markdown>
- [Click Here to Continue :octicons-arrow-right-24:](observability/index.md)
</div>