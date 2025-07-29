# Contributing

This guide documents our development practices & serves as a reference for common commands.

## Prerequisites

This guide assumes you have `git` and `uv` configured, and have checked out a copy of the project.

## Git Branching

For development we are using a simple feature-branch workflow:

### Starting a branch

For each ticket you are working on, create a new branch.

Give the branch a meaningful name, and be sure to start on `main`. The recommended flow is:

```shell
$ git switch main         # back to main
$ git pull origin main    # be sure main is up to date
$ git switch -c new-branch
```

### Using the branch

Once you're on the branch, use git as you usually would, making commits as you make progress.

`git add main.css`

`git commit -m "updated CSS for blue theme"`

`git push -u origin color-theme-change`

(the -u portion may be required once, then you can use `git push` as usual)

### Linting

We are using [pre-commit](https://pre-commit.com) to keep the code tidy as we go you can use it in one of two ways:

1. `uvx pre-commit install` will ensure that the pre-commit checks run *before* every commit you make, this can be a bit annoying at first, but will ensure you never commit non-linting code.

2. You can instead run `uvx pre-commit run -a` to check all files, this is also useful to clean up a PR.

For Python, `ruff` can fix many things, but sometimes you'll need to manually edit & recommit files to fix more complex linting issues.

(`uvx` is installed with `uv` and meant for running dev tools like this separate from any given project config, let me know if you have issues running it)

### Create PR

When you are ready for someone else to review your work create a PR here:

<https://github.com/uchicago-mscapp-projects/public-data-portal/pulls>

Describe what you've changed, and mention any areas you'd like people to pay special attention to.

### Code Review

Reviewers will review (see **Code Review** below) and leave feedback.

Respond to any requests for changes either by making the change or discussing on the ticket.

If you receive the go-ahead to merge, please **merge your own work** by pressing the green button on the PR page.

Once the work is merged, you may **delete the branch**, github will prompt you to do this.

Note: Unless you click past 1-2 big red buttons, it is very unlikely you'll lose work. Deleting an unmerged branch is intentionally difficult.

### Performing Code Review

1. Read through the code once to get a general understanding of what it does.
  - If you see bugs or anything very surprising/confusing comment as you go, but for now focus on a quick understanding of the change.

2. Take a second pass through now that you understand the code,
  - What isn't clear?
  - Are there any "code smells" (duplicated code, unused code, non-idiomatic code, etc.)

Leave your comments, be constructive with your feedback, and remember the goal is that we all have a better understanding of the problem, not that the code is *exactly* as you'd like it.

For now, if there are significant issues that you think should be addressed, mark as **Changes Requested**, otherwise you can mark as OK to merge.

## Working on the Project

### Setting DEBUG

While working on the project, you'll want to ensure that the DEBUG environment variable is set.

(If you get errors about `SECRET_KEY`, this is the cause.)

`$Env:DEBUG = $true` # powershell

`export DEBUG = true` # bash/zsh

### Important Django Commands

#### Running the server

`uv run manage.py runserver`

#### Whenever models are changed **by you**

`uv run manage.py makemigrations`
`uv run manage.py migrate`

#### Whenever models are changed (by someone else)

after `git pull`...

`uv run manage.py migrate`

#### Creating Superuser

`uv run manage.py createsuperuser`

#### Running Ingestion

`uv run manage.py ingest us.cary_nc` (replace us.cary_nc with path after `ingestion.`)

