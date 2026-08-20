import io
import re
import pandas as pd
from typing import Dict, Any, Tuple, List
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2.credentials import Credentials

class DriveScannerService:
    ID_PATTERN = re.compile(r"^([A-Za-z0-9_-]+)$")
    MEDIA_EXTENSIONS = {".mp4", ".mov", ".avi", ".jpg", ".jpeg", ".png", ".webp"}

    def __init__(self, credentials: Dict[str, Any]):
        creds = Credentials.from_authorized_user_info(credentials)
        self.service = build("drive", "v3", credentials=creds)

    def scan_folder(self, folder_id: str) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        all_files = []
        page_token = None

        # 1. Quét danh sách file từ Drive
        while True:
            response = self.service.files().list(
                q=f"'{folder_id}' in parents and trashed = false",
                fields="nextPageToken, files(id, name, mimeType, size, webViewLink)",
                pageToken=page_token,
                pageSize=100
            ).execute()

            all_files.extend(response.get("files", []))
            page_token = response.get("nextPageToken")
            if not page_token:
                break

        media_map: Dict[str, Dict[str, Any]] = {}
        title_file = None
        invalid_format_ids = []
        duplicate_media_ids = []

        # 2. Phân loại media và định vị file Excel tiêu đề
        for f in all_files:
            file_name = f.get("name", "")
            if file_name.endswith((".xlsx", ".xls")) or "tieu_de" in file_name.lower():
                title_file = f
                continue

            for ext in self.MEDIA_EXTENSIONS:
                if file_name.lower().endswith(ext):
                    raw_id = file_name[:file_name.rfind(".")].strip()
                    if not self.ID_PATTERN.match(raw_id):
                        invalid_format_ids.append(file_name)
                        continue

                    if raw_id in media_map:
                        duplicate_media_ids.append(raw_id)
                    else:
                        media_map[raw_id] = {
                            "drive_file_id": f["id"],
                            "file_name": file_name,
                            "drive_url": f.get("webViewLink", ""),
                            "file_type": "VIDEO" if ext in {".mp4", ".mov", ".avi"} else "IMAGE",
                            "extension": ext.replace(".", ""),
                            "file_size_bytes": int(f.get("size", 0))
                        }
                    break

        if not title_file:
            raise ValueError("Không tìm thấy file Excel danh sách tiêu đề trong thư mục Drive.")

        # 3. Tải và đọc file Excel tiêu đề vào Memory
        request = self.service.files().get_media(fileId=title_file["id"])
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()

        fh.seek(0)
        df_titles = pd.read_excel(fh)
        title_map: Dict[str, str] = {}

        for _, row in df_titles.iterrows():
            col1 = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ""
            col2 = str(row.iloc[1]).strip() if len(row) > 1 and pd.notna(row.iloc[1]) else ""

            if col1 and col2:
                title_map[col1] = col2
            elif col1 and "|" in col1:
                parts = col1.split("|", 1)
                title_map[parts[0].strip()] = parts[1].strip()

        # 4. Đối chiếu chéo ID giữa Media và Excel Title
        all_ids = set(media_map.keys()).union(set(title_map.keys()))
        validated_items = []
        missing_titles = []
        missing_media = []
        report_rows = []

        for cid in sorted(all_ids):
            media = media_map.get(cid)
            title = title_map.get(cid)

            status_icon = "✓"
            err = None

            if media and not title:
                status_icon = "✗"
                err = "Thiếu tiêu đề trong Excel"
                missing_titles.append(cid)
            elif not media and title:
                status_icon = "✗"
                err = "Thiếu tệp Media trên Drive"
                missing_media.append(cid)
            elif media and title:
                validated_items.append({
                    "content_id": cid,
                    "title": title,
                    "media": media
                })

            report_rows.append({
                "Status": status_icon,
                "Content ID": cid,
                "Media File": media["file_name"] if media else "N/A",
                "Raw Title": title if title else "N/A",
                "Error": err if err else "Hợp lệ"
            })

        summary = {
            "total_media": len(media_map),
            "total_titles": len(title_map),
            "valid_count": len(validated_items),
            "missing_titles": missing_titles,
            "missing_media": missing_media,
            "duplicate_ids": duplicate_media_ids,
            "invalid_format_ids": invalid_format_ids,
            "report_df": pd.DataFrame(report_rows)
        }

        return summary, validated_items
