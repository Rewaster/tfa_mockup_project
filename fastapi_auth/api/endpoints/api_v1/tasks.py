from celery.result import AsyncResult
from fastapi import APIRouter

from fastapi_auth.core.utils import Email
from fastapi_auth.tasks.tasks import send_email_task

tasks_router = APIRouter()


@tasks_router.get("/test-celery", description="An endpoint to test celery send mail function")
async def test_celery(email_addr: str):
    """
    Test celery
    """
    email_obj = Email(
        to_=[email_addr],
        subject_="Test sending an email via Celery",
        text_="This is a test message from FastAPI auth service.",
    )
    task = send_email_task.apply_async(kwargs={"email": email_obj.to_json()})
    task_id = task.task_id
    return {"task_id": task_id}


@tasks_router.get("/task_status", description="An endpoint to retrieve task status")
async def task_status(task_id):
    """Check the existing task status"""
    task = AsyncResult(task_id)
    if isinstance(task.result, Exception):
        task_result = str(task.result)
    else:
        task_result = task.result

    response = {
        "state": task.state,
        "result": task_result,
    }

    return response
