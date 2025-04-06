# backend/app/core/celery_app.py
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "worker",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"
)

celery_app.conf.task_routes = {
    "app.worker.test_celery": "main-queue",
}