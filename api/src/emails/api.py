from fastapi import APIRouter, Depends, HTTPException
from fastapi_mail import FastMail, MessageSchema, MessageType

from ..auth.dependencies import get_current_user
from .models import EmailSchema

router = APIRouter()


@router.post("/")
async def send_email(payload: EmailSchema, _=Depends(get_current_user)):
    # This route is intended to fail without proper credentials
    try:
        from config import settings
        from fastapi_mail import ConnectionConfig
        conf = ConnectionConfig(
            MAIL_USERNAME=settings.MAIL_USERNAME,
            MAIL_PASSWORD=settings.MAIL_PASSWORD,
            MAIL_FROM=payload.managerEmail or settings.MAIL_USERNAME,
            MAIL_PORT=settings.MAIL_PORT,
            MAIL_SERVER=settings.MAIL_SERVER,
            MAIL_FROM_NAME=payload.managerName or "",
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
        )
        message = MessageSchema(
            subject=payload.subject or "",
            recipients=payload.recipients,
            body=payload.body or "",
            cc=payload.cc or [],
            bcc=payload.bcc or [],
            subtype=MessageType.plain,
        )
        fm = FastMail(conf)
        await fm.send_message(message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return "Sent"
