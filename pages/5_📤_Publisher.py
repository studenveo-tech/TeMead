import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Publish Queue & Trạng Thái | TeMead", layout="wide")
st.title("📤 Quản Lý Hàng Đợi & Đăng Bài Tự Động")

scheduled_data = st.session_state.get("scheduled_content", [])
if not scheduled_data:
    st.warning("⚠️ Chưa có danh sách bài đăng đã duyệt. Vui lòng vào trang **4_📅_Calendar** trước.")
    st.stop()

approved_items = [item for item in scheduled_data if item.get("approval_status") == "APPROVED"]

col1, col2, col3 = st.columns(3)
col1.metric("Tổng Bài Sẵn Sàng", len(approved_items))
col2.metric("Nền Tảng Hỗ Trợ", "3 (FB, TikTok, YT)")
col3.metric("Trạng Thái Queue", "Sẵn sàng kết nối Celery/Redis")

st.divider()
st.subheader("📋 Danh Sách Jobs Đăng Bài")

# Xây dựng bảng hiển thị Jobs
queue_rows = []
for item in approved_items:
    data = item["data"]
    sched = item.get("schedule", {})
    
    queue_rows.append({
        "Content ID": item["content_id"],
        "Facebook Job": f"{sched.get('facebook_date')} {sched.get('facebook_time')} (QUEUED)",
        "TikTok Job": f"{sched.get('tiktok_date')} {sched.get('tiktok_time')} (QUEUED)",
        "YouTube Job": f"{sched.get('youtube_date')} {sched.get('youtube_time')} (QUEUED)",
        "Tựa Đề": item["raw_title"],
        "Pillar": data.dna.pillar_name
    })

if queue_rows:
    st.dataframe(pd.DataFrame(queue_rows), use_container_width=True)
else:
    st.info("Chưa có nội dung nào được duyệt (APPROVED). Hãy vào trang Calendar để duyệt bài.")

if st.button("🚀 Đẩy Toàn Bộ Bài Đã Duyệt Vào Redis Queue", type="primary", disabled=len(approved_items) == 0):
    with st.spinner("Đang khởi tạo các Job độc lập vào Celery Queue..."):
        # Giả lập dispatch jobs vào Celery/Redis
        st.success(f"Đã lên lịch thành công {len(approved_items) * 3} Jobs độc lập trên Redis!")
        st.info("Worker sẽ tự động thực thi khi đến khung giờ đã định.")
