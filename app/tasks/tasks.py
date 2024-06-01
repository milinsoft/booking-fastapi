from pathlib import Path
from smtplib import SMTP_SSL

from PIL import Image
from pydantic import EmailStr

from app.config import settings
from app.tasks.celery import celery
from app.tasks.email_templates import create_booking_confirmation_template


@celery.task
def process_pic(path: str) -> None:
    output_dir = "app/static/images/resized"
    img_path = Path(path).absolute()
    img = Image.open(path)
    img_1000_500 = img.resize((1000, 500))
    img_200_100 = img.resize((2000, 100))
    img_1000_500.save(f"{output_dir}_1000_500_{img_path.name}")
    img_200_100.save(f"{output_dir}_200_100_{img_path.name}")


@celery.task
def send_booking_confirmation_email(booking: dict, email_to: EmailStr):
    email = create_booking_confirmation_template(booking, email_to)

    with SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(email)
