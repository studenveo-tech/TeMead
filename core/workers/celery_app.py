import os
from celery import Celery
from dotenv import load_dotenv
from core.publishers.social_adapters import FacebookPublisher, YouTubePublisher, TikTokPublisher

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

app = Celery("temead_publisher", broker=REDIS_URL, backend=REDIS_URL)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Ho_Chi_Minh",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1
)

@app.task(bind=True, max_retries=3, default_retry_delay=60)
def publish_facebook_job(self, page_id: str, access_token: str, payload: dict):
    try:
        return FacebookPublisher.publish(
            page_id=page_id,
            access_token=access_token,
            caption=payload["caption"],
            hashtags=payload["hashtags"],
            media_url=payload["media_url"],
            media_type=payload["media_type"],
            title=payload.get("title")
        )
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

@app.task(bind=True, max_retries=3, default_retry_delay=60)
def publish_tiktok_job(self, access_token: str, payload: dict):
    try:
        return TikTokPublisher.publish(
            access_token=access_token,
            caption=payload["caption"],
            hashtags=payload["hashtags"],
            video_url=payload["video_url"]
        )
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

@app.task(bind=True, max_retries=3, default_retry_delay=120)
def publish_youtube_job(self, credentials_dict: dict, video_path: str, payload: dict):
    try:
        return YouTubePublisher.publish(
            credentials_dict=credentials_dict,
            video_path=video_path,
            title=payload["title"],
            description=payload["description"],
            tags=payload["tags"],
            hashtags=payload["hashtags"]
        )
    except Exception as exc:
        raise self.retry(exc=exc, countdown=120 * (2 ** self.request.retries))
