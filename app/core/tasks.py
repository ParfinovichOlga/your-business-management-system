from django.core.mail import send_mail
from celery import shared_task
from django.conf import settings
from typing import List


@shared_task
def send_information_email(subject: str, message, recipients_email: List):
    send_mail(
        subject=subject,
        from_email=settings.EMAIL_HOST_USER,
        message=message,
        recipient_list=recipients_email,
        fail_silently=False
    )
