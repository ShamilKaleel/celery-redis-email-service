import os
from celery import Celery
from dotenv import load_dotenv
import redis

load_dotenv()

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

# Celery configuration
CELERY_WORKER_CONCURRENCY = int(os.getenv("CELERY_WORKER_CONCURRENCY", "4"))
CELERY_TASK_TIME_LIMIT = int(os.getenv("CELERY_TASK_TIME_LIMIT", "300"))
CELERY_RESULT_EXPIRES = int(os.getenv("CELERY_RESULT_EXPIRES", "3600"))

print(f"🔗 Connecting to Redis: {REDIS_URL}")

# Initialize Celery app
app = Celery("email_app")

# Configure Celery
app.conf.update(
    broker_url=REDIS_URL,
    result_backend=REDIS_URL,
    result_expires=CELERY_RESULT_EXPIRES,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    result_accept_content=["json"],
    task_track_started=True,
    task_send_sent_event=True,
    worker_send_task_events=True,
    timezone="UTC",
    enable_utc=True,
    worker_concurrency=CELERY_WORKER_CONCURRENCY,
    worker_prefetch_multiplier=1,
    task_time_limit=CELERY_TASK_TIME_LIMIT,
    task_soft_time_limit=CELERY_TASK_TIME_LIMIT - 60,
    include=["tasks"],
    task_ignore_result=False,
    task_store_eager_result=True,
)


def get_queue_length():
    """Get the length of the Celery queue."""
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
        queue_length = r.llen("celery")
        return queue_length
    except Exception as e:
        print(f"❌ Error checking Redis queue length: {e}")
        return 0


if __name__ == "__main__":
    app.start()
