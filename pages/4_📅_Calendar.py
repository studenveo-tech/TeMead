import streamlit as st
from datetime import datetime, date
import pandas as pd
from core.scheduler.scheduler_engine import ContentScheduler, ExcelReportEngine

st.set_page_config(page_title="Lập Lịch & Phê Duyệt | TeMead", layout="wide")
st.title("📅 Quản Lý Lịch Đăng & Phê Duyệt Nội Dung")

generated_content = st.session_state.get("generated_content", [])
if not generated_content:
    st.warning("⚠️ Chưa có nội dung được tạo. Vui lòng hoàn tất ở trang **3_🤖_AI_Content** trước.")
    st.stop()

# 1. Cấu hình Tham số Lập lịch
with st.sidebar:
    st.header("⚙️ Cấu hình Khung Giờ")
    start_date = st.date_input("Ngày bắt đầu:", value=date.today())
    posts_per_day = st.number_input("Số bài đăng/ngày:", min_value=1, max_value=5, value=2)
    
    fb_slots = st.text_input("Giờ Facebook (cách bởi dấu phẩy):", value="11:30, 19:30")
    tt_slots = st.text_input("Giờ TikTok:", value="12:00, 20:00")
    yt_slots = st.text_input("Giờ YouTube:", value="20:00")

    time_slots = {
        "FACEBOOK": [s.strip() for s in fb_slots.split(",") if s.strip()],
        "TIKTOK": [s.strip() for s in tt_slots.split(",") if s.strip()],
        "YOUTUBE": [s.strip() for s in yt_slots.split(",") if s.strip()]
    }

# 2. Xử lý xếp lịch tự động
if "scheduled_content" not in st.session_state or st.button("🔄 Tái Lập Lịch Chống Trùng Pillar"):
    scheduled = ContentScheduler.distribute_schedule(
        contents=generated_content,
        start_date=datetime.combine(start_date, datetime.min.time()),
        posts_per_day=posts_per_day,
        time_slots=time_slots
    )
    st.session_state["scheduled_content"] = scheduled
    st.success("Đã hoàn tất sắp xếp lịch đăng chống trùng Content Pillar!")

scheduled_data = st.session_state["scheduled_content"]

# 3. Phê duyệt nhanh & Thống kê
st.subheader("📊 Trạng Thái Phê Duyệt (Approval Matrix)")
col1, col2, col3 = st.columns(3)

approved_count = sum(1 for item in scheduled_data if item.get("approval_status") == "APPROVED")
pending_count = len(scheduled_data) - approved_count

col1.metric("Tổng Nội Dung Đã Lập Lịch", len(scheduled_data))
col2.metric("Tự Động Duyệt (Score ≥ 8.5)", approved_count)
col3.metric("Chờ Duyệt Thủ Công", pending_count)

# 4. Bảng duyệt chi tiết
st.markdown("### 📋 Danh Sách Phê Duyệt Chi Tiết")
for item in scheduled_data:
    data = item["data"]
    sched = item.get("schedule", {})
    
    with st.expander(f"[{item['content_id']}] {item['raw_title']} | Pillar: {data.dna.pillar_name} | Điểm: {data.score.overall_score}"):
        col_info, col_action = st.columns([3, 1])
        with col_info:
            st.write(f"📅 **Lịch FB:** {sched.get('facebook_date')} {sched.get('facebook_time')} | **TikTok:** {sched.get('tiktok_date')} {sched.get('tiktok_time')} | **YouTube:** {sched.get('youtube_date')} {sched.get('youtube_time')}")
            st.write(f"📘 **Hook Facebook:** {data.facebook.title_hook}")
            st.write(f"🎵 **Hook TikTok:** {data.tiktok.hook_caption}")
            st.write(f"▶️ **SEO Title YouTube:** {data.youtube.seo_title}")

        with col_action:
            status = st.selectbox(
                "Trạng thái duyệt:",
                ["APPROVED", "PENDING", "REJECTED"],
                index=0 if item.get("approval_status") == "APPROVED" else 1,
                key=f"appr_{item['content_id']}"
            )
            item["approval_status"] = status

# 5. Xuất báo cáo Excel
st.divider()
st.subheader("📥 Xuất File Excel Quản Lý")

excel_bytes = ExcelReportEngine.generate_excel(scheduled_data)

st.download_button(
    label="📊 Tải Xuống File Master Content Excel (.xlsx)",
    data=excel_bytes,
    file_name=f"TeMead_Content_Plan_{date.today().strftime('%Y%m%d')}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    type="primary"
)
