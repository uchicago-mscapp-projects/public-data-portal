# Public Data Portal

See [Contributing](docs/contributing.md)

---

## About the Repository

### File System Layout

- `apps/` - Create your app(s) in this directory.
- `apps/accounts/` - An app that defines our custom user model, compatible with `allauth` and `django.contrib.admin`.
- `config/` - This directory is the Django "project". It contains settings files as well as your root `urls.py`.
- `static/` - This directory is where you will place your static CSS, images, and JS. Those files will be served via `whitenoise`.
- `static/root/` - This directory will be served as-is at the root of your application. It is useful for files like `robots.txt` that need to be in a particular place.
- `static/root/robots.txt` - A default robots.txt is provided that excludes troublesome AI bots. (via https://github.com/ai-robots-txt/ai.robots.txt/blob/main/robots.txt)
)
- `templates/` - Django is configured to search this directory for your templates. You can also put templates within `<appdir>/templates/` for any given app, but this layout keeps them all together.
- `templates/account/` - For your convinience, the default auth templates provided by `django-allauth`. Replace or modify these.

Additionally, there are two directories that you will see after running your application. These are `.gitignore`d.

- `_staticfiles` - Where Django will store the combined static files for serving. Do not modify files in this directory directly, instead modify the copies in `static`.
- `_logs` - The default destination of the log files, can be modified in `config/settings.py`.

### Tool Choices

- `ruff` - Ensure code quality.
- `uv` - Manage packages.
- `pre-commit` - Enforce repository standards.
- `just` - Run common tasks.

### Django Plugins/Apps

#### django-environ

Configure Django projects using environment variables, per [The Twelve-Factor App](https://www.12factor.net).

<https://django-environ.readthedocs.io/en/latest/>

#### whitenoise

Efficiently serve static files alongside your application.

<https://whitenoise.readthedocs.io/en/latest/>

#### django-typer

Allows writing Django management commands using `typer`.

<https://django-typer.readthedocs.io/en/stable/>

#### pytest-django

Allows writing Django tests using simplified `pytest`-style tests. Provides fixtures & other test helpers.

<https://pytest-django.readthedocs.io/en/latest/>

#### django-debug-toolbar

Provides an in-browser interface for inspecting Django views.

<https://django-debug-toolbar.readthedocs.io/en/latest/>

#### django-structlog

This library integrates [structured logging](https://www.structlog.org/en/stable/) with Django.

#### django-allauth

Augment's django's built in `auth` with commonly-needed views for signup, email confirmation, etc.
