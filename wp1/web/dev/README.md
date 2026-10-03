# Development overlay

The API server has a built-in development overlay, currently used for manual
update endpoints. The endpoints defined in `wp1.web.dev.projects` are used
with priority, instead of the production endpoints, **only if the environment
(`WP1_ENV`) is development, which is the default**. This is to allow for
easier manual and CI testing of the manual update page.

If you wish to test the manual update job with a real Wikipedia replica
database and RQ jobs, you will have to disable this overlay. The easiest way
would be to change the following line in `wp1.web.app`:

```
  if ENV == environment.Environment.DEVELOPMENT:
    # In development, override some project endpoints, mostly manual
    # update, to provide an easier env for developing the frontend.
    print('DEVELOPMENT: overlaying dev_projects blueprint. '
          'Some endpoints will be replaced with development versions')
    app.register_blueprint(dev_projects, url_prefix='/v1/projects')
```

to something like:

```
  if false:  # false while manually testing
    # In development, override some project endpoints, mostly manual
    ...
```
