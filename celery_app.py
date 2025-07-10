import os
from celery import Celery
from dotenv import load_dotenv
import redis

load_dotenv()

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_DB = os.getenv("REDIS_DB", "0")
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

print(f"🔗 Connecting to Redis: {REDIS_URL}")

# Initialize Celery app with explicit backend configuration
app = Celery("email_app")

# Configure Celery
app.conf.update(
    # Broker and Backend
    broker_url=REDIS_URL,
    result_backend=REDIS_URL,
    # Task settings
    result_expires=60 * 60,  # 1 hour
    task_track_started=True,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    result_accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    # Worker settings
    worker_concurrency=4,
    worker_prefetch_multiplier=1,
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,  # 4 minutes
    # Include tasks
    include=["tasks"],
    # Ensure backend is enabled
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
