import streamlit as st

st.set_page_config(
    page_title="TeMead - AI Content Automation Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🚀 TeMead - Nền Tảng Tự Động Hóa Content Đa Nền Tảng")
st.markdown("### *Giải pháp AI toàn diện: Google Drive ➔ Đối chiếu ➔ AI Phân Tích ➔ Lập Lịch ➔ Đăng Bài ➔ Tối Ưu Hiệu Quả*")

st.divider()

col1, col2, col3 = st.columns(3)
with col1:
    st.info("### 1. Ingestion & Validation\n- Quét thư viện Google Drive\n- Tự động map `001.mp4` ↔ `001` Title\n- Phát hiện lỗi dữ liệu 100%")

with col2:
    st.success("### 2. Multi-Platform AI\n- Thiết lập Content DNA\n- Tạo nội dung riêng FB/TikTok/YT\n- Chấm điểm Content Score")

with col3:
    st.warning("### 3. Execution & Insights\n- Thuật toán chống trùng Pillar\n- Xuất Master Excel chuẩn\n- Queue đăng bài và AI Insights")

st.divider()

st.subheader("📌 Hướng Dẫn Quy Trình Vận Hành (Standard Workflow):")
st.markdown("""
1. **Bước 1:** Vào menu bên trái chọn **`2_📂_Google_Drive`** để nhập Folder ID và chạy đối chiếu dữ liệu.
2. **Bước 2:** Chuyển sang **`3_🤖_AI_Content`** để cấu hình Brand Brain và sinh toàn bộ kịch bản, tiêu đề SEO, caption.
3. **Bước 3:** Vào **`4_📅_Calendar`** để xem phân bổ lịch đăng, duyệt bài (hoặc tự động duyệt nếu Score $\ge 8.5$) và tải file Excel.
4. **Bước 4:** Vào **`5_📤_Publisher`** để chuyển trạng thái bài duyệt vào Redis/Celery queue sẵn sàng xuất bản.
5. **Bước 5:** Theo dõi hiệu quả và nhận chỉ số tối ưu tại **`6_📈_Analytics`**.
""")
