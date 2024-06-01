from celery import Celery

from app.config import settings

celery = Celery(
    "tasks",
    broker=f"redis://{settings.REDIS_HOST_URL}:{settings.REDIS_PORT}",
    include=["app.tasks.tasks"],
    broker_connection_retry_on_startup=True,
)  # file path to store tasks
