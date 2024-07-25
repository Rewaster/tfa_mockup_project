import yagmail
from celery import Celery

from fastapi_auth.core.config import settings

celery = Celery("my_celery", config_source=settings, namespace="CELERY")

gmail_client = yagmail.SMTP(settings.TEST_EMAIL_SENDER, settings.TEST_EMAIL_APP_PASSWORD)
