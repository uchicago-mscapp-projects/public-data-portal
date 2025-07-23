## Setting DEBUG

`$Env:DEBUG = $true` # powershell

`export DEBUG = true` # bash/zsh

(Remember to set if being asked for SECRET_KEY)

## Whenever models are changed **by you**

`uv run manage.py makemigrations`
`uv run manage.py migrate`

## Whenever models are changed (by someone else)

after `git pull`...

`uv run manage.py migrate`

## Running the server

`uv run manage.py runserver`

## Creating Superuser

`uv run manage.py createsuperuser`

## Running Ingestion

`uv run manage.py ingest us.cary_nc` (replace us.cary_nc with path after `ingestion.`)

