# backend/app/worker.py
from app.core.celery_app import celery_app

@celery_app.task(acks_late=True)
def test_celery(word: str) -> str:
    return f"test task return {word}"