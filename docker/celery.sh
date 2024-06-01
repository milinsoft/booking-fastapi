#!/bin/bash


if [[ "${1}" == "celery" ]]; then
    celery --app=app.tasks.celery:celery worker -l INFO --uid nobody
elif [[ "${1}" == "flower" ]]; then
    celery --app=app.tasks.celery:celery flower --uid nobody
fi
