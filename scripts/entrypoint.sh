#!/bin/bash
echo "ENTRYPOINT $IMAGE_NAME"

# alembic
alembic upgrade head

uvicorn fastapi_auth.main:app --host "${FASTAPI_HOST}" --port "${FASTAPI_PORT}"
