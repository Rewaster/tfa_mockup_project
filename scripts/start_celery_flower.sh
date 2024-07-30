#!/bin/bash

set -o errexit
set -o nounset

celery -A fastapi_auth.tasks.celery_conf flower --loglevel=info --broker-api=http://"${MQ_USER}":"${MQ_PASSWORD}"@"${MQ_HOST}":15672/api/vhost
