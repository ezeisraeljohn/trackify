#!/bin/bash

if [ "$SERVICE" = "web" ]; then
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000
elif [ "$SERVICE" = "worker" ]; then
    exec celery -A app.celery_app.celery_app worker --loglevel=info
elif [ "$SERVICE" = "beat" ]; then
    exec celery -A app.celery_app.celery_app beat --loglevel=info
else
    echo "Unknown SERVICE type: $SERVICE"
    exit 1
fi
