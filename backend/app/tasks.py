import time
from celery import Celery

# Конфигурация Celery для подключения к Redis
celery = Celery(
    'tasks',
    broker='redis://redis:6379/0',
    backend='redis://redis:6379/0'
)

@celery.task
def my_task(seconds: int):
    """Простая фоновая задача, которая ждет указанное количество секунд."""
    time.sleep(seconds)
    return {"status": "Task completed"}

@celery.task
def fetch_daily_data():
    """Fetch data from a website and persist it to the database."""
    import httpx
    from datetime import datetime
    from .database import SessionLocal
    from .models import FetchedData

    url = "https://example.com"  # TODO: replace with the real data source
    response = httpx.get(url, timeout=30)
    response.raise_for_status()

    db = SessionLocal()
    try:
        db_obj = FetchedData(
            source_url=url,
            content=response.text,
            fetched_at=datetime.utcnow(),
        )
        db.add(db_obj)
        db.commit()
    finally:
        db.close()

from celery.schedules import crontab

# Add periodic task schedule (runs daily at midnight UTC)
celery.conf.beat_schedule = {
    "fetch_daily_data": {
        "task": "app.tasks.fetch_daily_data",
        "schedule": crontab(minute=0, hour=0),
    }
}

# Ensure the persistent beat scheduler can write its schedule file
celery.conf.beat_schedule_filename = "/tmp/celerybeat-schedule"