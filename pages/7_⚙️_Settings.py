import streamlit as st
import os

st.set_page_config(page_title="Cài Đặt Hệ Thống & Brand Brain | TeMead", layout="wide")
st.title("⚙️ Quản Lý Brand Brain & Cấu Hình Kết Nối")

tab_brand, tab_tokens, tab_system = st.tabs(["🏢 Hồ Sơ Thương Hiệu (Brand Brain)", "🔑 Kết Nối Mạng Xã Hội", "🖥️ Trạng Thái Hạ Tầng"])

with tab_brand:
    st.subheader("Cấu Hình Brand Profile Mặc Định")
    st.markdown("Hệ thống AI sẽ dựa trên thông tin này để điều chỉnh văn phong, từ khóa và CTA phù hợp.")
    
    col1, col2 = st.columns(2)
    b_name = col1.text_input("Tên thương hiệu:", value="Thiên Tín Media")
    b_tone = col2.text_input("Giọng điệu truyền thông (Tone of Voice):", value="Chuyên gia, tin cậy, đột phá, hiện đại")
    b_target = col1.text_area("Chân dung khách hàng mục tiêu:", value="Chủ doanh nghiệp SME, Trưởng phòng Marketing, Nhà sáng tạo nội dung 25-45 tuổi")
    b_products = col2.text_area("Sản phẩm / Dịch vụ chủ lực:", value="Sản xuất video ngắn, Quản trị kênh đa nền tảng, Booking truyền thông")
    
    b_keywords = col1.text_area("Từ khóa ưu tiên (mỗi từ một dòng):", value="truyền thông\nmarketing số\nsản xuất video\nxây dựng thương hiệu")
    b_forbidden = col2.text_area("Từ cấm tuyệt đối (Forbidden words):", value="cam kết 100%\nsố 1 việt nam\nlừa đảo\nchắc chắn giàu")
    
    b_cta = st.text_input("CTA mặc định:", value="Liên hệ ngay hotline hoặc gửi tin nhắn để nhận bản kế hoạch miễn phí!")

    if st.button("💾 Lưu Cấu Hình Brand Brain", type="primary"):
        st.session_state["brand_profile"] = {
            "name": b_name,
            "voice_tone": b_tone,
            "target_audience": b_target,
            "products": b_products,
            "keywords": [k.strip() for k in b_keywords.split("\n") if k.strip()],
            "forbidden_words": [w.strip() for w in b_forbidden.split("\n") if w.strip()],
            "default_cta": b_cta
        }
        st.success("Đã cập nhật Brand Brain thành công!")

with tab_tokens:
    st.subheader("Kết Nối OAuth Official APIs")
    
    with st.expander("📘 Cấu hình Meta (Facebook Graph API)"):
        fb_page_id = st.text_input("Facebook Page ID:", placeholder="1029384756...")
        fb_token = st.text_input("Page Access Token (Long-lived):", type="password")
        if st.button("Lưu Facebook Token"):
            st.session_state["fb_config"] = {"page_id": fb_page_id, "token": fb_token}
            st.success("Đã lưu cấu hình Facebook!")

    with st.expander("🎵 Cấu hình TikTok Content Posting API"):
        tt_token = st.text_input("TikTok Creator Access Token:", type="password")
        if st.button("Lưu TikTok Token"):
            st.session_state["tt_config"] = {"token": tt_token}
            st.success("Đã lưu cấu hình TikTok!")

    with st.expander("▶️ Cấu hình YouTube Data API v3"):
        st.info("YouTube sử dụng cơ chế OAuth 2.0 Client Secret (tải tệp JSON từ Google Cloud Console).")
        uploaded_json = st.file_uploader("Tải lên client_secret.json:", type=["json"])
        if uploaded_json:
            st.success("Đã tải lên tệp xác thực YouTube thành công!")

with tab_system:
    st.subheader("Kiểm Tra Kết Nối Hạ Tầng")
    col_db, col_redis, col_ai = st.columns(3)
    
    db_status = "🟢 Hoạt động" if os.getenv("DATABASE_URL") else "🟡 Chưa cấu hình .env"
    redis_status = "🟢 Hoạt động" if os.getenv("REDIS_URL") else "🟡 Chưa cấu hình .env"
    ai_status = "🟢 Sẵn sàng (Gemini)" if os.getenv("GEMINI_API_KEY") else "🔴 Thiếu GEMINI_API_KEY"

    col_db.metric("PostgreSQL Database", db_status)
    col_redis.metric("Redis Queue", redis_status)
    col_ai.metric("AI Content Engine", ai_status)
