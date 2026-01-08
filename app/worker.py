# Import tasks to ensure they are registered
from app.tasks import email  # noqa

from app.core.celery_app import celery_app

if __name__ == "__main__":
    celery_app.start()
