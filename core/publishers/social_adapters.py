import os
import requests
from typing import Dict, Any, List
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

class FacebookPublisher:
    BASE_URL = "https://graph.facebook.com/v19.0"

    @classmethod
    def publish(
        cls, 
        page_id: str, 
        access_token: str, 
        caption: str, 
        hashtags: List[str], 
        media_url: str, 
        media_type: str,
        title: str = None
    ) -> Dict[str, Any]:
        formatted_message = f"{caption}\n\n{' '.join(['#' + h.lstrip('#') for h in hashtags])}"
        
        if media_type == "VIDEO":
            # Graph API Video Upload qua Hosted URL
            url = f"{cls.BASE_URL}/{page_id}/videos"
            payload = {
                "file_url": media_url,
                "description": formatted_message,
                "title": title or "",
                "access_token": access_token
            }
        else:
            # Graph API Photo Upload
            url = f"{cls.BASE_URL}/{page_id}/photos"
            payload = {
                "url": media_url,
                "caption": formatted_message,
                "access_token": access_token
            }

        response = requests.post(url, data=payload, timeout=60)
        res_data = response.json()

        if response.status_code != 200:
            raise Exception(f"Facebook Graph API Error: {res_data.get('error', {}).get('message', 'Unknown error')}")

        post_id = res_data.get("id")
        return {
            "platform": "FACEBOOK",
            "post_id": post_id,
            "post_url": f"https://www.facebook.com/{post_id}",
            "raw": res_data
        }


class YouTubePublisher:
    @classmethod
    def publish(
        cls, 
        credentials_dict: Dict[str, Any], 
        video_path: str, 
        title: str, 
        description: str, 
        tags: List[str],
        hashtags: List[str]
    ) -> Dict[str, Any]:
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Không tìm thấy file video cục bộ: {video_path}")

        creds = Credentials.from_authorized_user_info(credentials_dict)
        youtube = build("youtube", "v3", credentials=creds)

        full_desc = f"{description}\n\n{' '.join(['#' + h.lstrip('#') for h in hashtags])}"
        
        body = {
            "snippet": {
                "title": title[:100],
                "description": full_desc,
                "tags": tags,
                "categoryId": "22"
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False
            }
        }

        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
        request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
        
        response = None
        while response is None:
            status, response = request.next_chunk()

        video_id = response.get("id")
        return {
            "platform": "YOUTUBE",
            "post_id": video_id,
            "post_url": f"https://www.youtube.com/watch?v={video_id}",
            "raw": response
        }


class TikTokPublisher:
    BASE_URL = "https://open.tiktokapis.com/v2"

    @classmethod
    def publish(
        cls, 
        access_token: str, 
        caption: str, 
        hashtags: List[str], 
        video_url: str
    ) -> Dict[str, Any]:
        """
        TikTok Content Posting API v2 (Direct Post qua URL)
        """
        post_title = f"{caption} {' '.join(['#' + h.lstrip('#') for h in hashtags])}"[:2200]
        url = f"{cls.BASE_URL}/post/publish/video/init/"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "post_info": {
                "title": post_title,
                "privacy_level": "PUBLIC_TO_EVERYONE",
                "disable_duet": False,
                "disable_stitch": False,
                "disable_comment": False
            },
            "source_info": {
                "source": "PULL_FROM_URL",
                "video_url": video_url
            }
        }

        response = requests.post(url, headers=headers, json=payload, timeout=60)
        res_data = response.json()

        if response.status_code != 200 or res_data.get("error", {}).get("code") != "ok":
            raise Exception(f"TikTok API Error: {res_data.get('error', {}).get('message', 'Unknown error')}")

        publish_id = res_data.get("data", {}).get("publish_id")
        return {
            "platform": "TIKTOK",
            "post_id": publish_id,
            # [REQUIRES VERIFICATION] TikTok API v2 Direct Post cần thời gian xử lý video trước khi cấp URL cuối
            "post_url": f"https://www.tiktok.com/@publish_job_{publish_id}",
            "raw": res_data
        }
