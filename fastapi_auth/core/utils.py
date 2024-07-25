import json
from dataclasses import asdict
from dataclasses import dataclass

from celery.result import AsyncResult
from pydantic import EmailStr

from fastapi_auth.models.device import Device
from fastapi_auth.models.users import User
from fastapi_auth.tasks.tasks import send_email_task


@dataclass(slots=True, frozen=True)
class Email:
    """A class to store email information to be sent"""

    to_: list[EmailStr]
    subject_: str
    text_: str

    def to_json(self):
        """Convert the class to a JSON-formatted string"""
        return json.dumps(asdict(self))

    def __repr__(self) -> str:
        return f"Email (to: {self.to_}), " f"(subject: {self.subject_}), " f"(text: {self.text_})"


def send_mail_backup_tokens(user: User, device: Device) -> AsyncResult:
    """Send a list of consumable backup tokens via email"""
    backup_tokens = " ".join([backup_token.token for backup_token in device.backup_tokens])
    email_obj = Email(
        to_=[user.email],
        subject_="Your backup tokens for FastAPI auth server",
        text_=f"Backup tokens : {backup_tokens}",
    )
    print(f"Sending email task to celery, email:\n\n***\n{email_obj.text_}\n***\n")
    task = send_email_task.apply_async(kwargs={"email": email_obj.to_json()})
    return task


def send_mail_totp_token(user: User, token: str) -> AsyncResult:
    """Send a TOTP token via email"""
    email_obj = Email(
        to_=[user.email],
        subject_="Your TOTP access tokens for FastAPI auth server",
        text_=f"Access TOTP token : {token}",
    )
    print(f"Sending email task to celery, email:\n\n***\n{email_obj.text_}\n***\n")
    task = send_email_task.apply_async(kwargs={"email": email_obj.to_json()})
    return task
