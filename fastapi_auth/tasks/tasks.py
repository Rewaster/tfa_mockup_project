import json

from celery import states

from fastapi_auth.api import common_logger
from fastapi_auth.tasks.celery_conf import celery
from fastapi_auth.tasks.celery_conf import gmail_client


@celery.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5},
)
def send_email_task(self, email: str) -> dict:
    """A Celery task that sends e-mails to a specified address"""
    self.update_state(state=states.PENDING, meta={"state": "Sending email.."})
    common_logger.debug("Sending email..")
    email = json.loads(email)
    gmail_client.send(to=email["to_"], subject=email["subject_"], contents=email["text_"])
    common_logger.debug("\nEmail sent:\n")
    self.update_state(state=states.PENDING, meta={"state": "..Email sent"})
    common_logger.debug(email)
    return email
