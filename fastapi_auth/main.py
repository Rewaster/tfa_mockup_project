import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from fastapi_auth.api.endpoints.router import router
from fastapi_auth.core.config import settings
from fastapi_auth.db.session import SessionLocal
from fastapi_auth.tasks.celery_conf import celery

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)


# routers
app.include_router(router=router, prefix=settings.API_V1_STR)


@app.on_event("startup")
async def app_startup():
    """Start the FastAPI server and check all that all of the connections are OK"""
    # CHECK DB
    try:
        db = SessionLocal()
        await db.execute("SELECT 1")
        print("Database is connected")
    except Exception:
        raise RuntimeError("Problems reaching db")
    finally:
        await db.close()

    # CHECK CELERY BROKER
    try:
        celery.broker_connection().ensure_connection(max_retries=3)
    except Exception as ex:
        raise RuntimeError(f"Failed to connect to celery broker, {str(ex)}")
    print("Celery broker is running")

    # CHECK CELERY WORKER
    insp = celery.control.inspect()
    availability = insp.ping()
    if not availability:
        raise RuntimeError("Celery worker is not running")
    print("Celery worker is running")


# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/")
async def main():
    """A routing function to return placeholder info on the root page"""
    return "App is running"


if __name__ == "__main__":
    uvicorn.run(
        "fastapi_auth.main:app",
        host=settings.FASTAPI_HOST,
        port=settings.FASTAPI_PORT,
        reload=True,
        use_colors=True,
    )
