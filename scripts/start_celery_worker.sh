#!/bin/bash

set -o errexit
set -o nounset

celery -A fastapi_auth.tasks.celery_conf worker --loglevel=info
