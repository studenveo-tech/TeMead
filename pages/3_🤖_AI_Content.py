import streamlit as st
import pandas as pd
from core.engine.gemini_engine import GeminiContentEngine

st.set_page_config(page_title="AI Content Engine | TeMead", layout="wide")
st.title("🤖 AI Content Engine - Đa Nền Tảng")

# Kiểm tra dữ liệu từ bước Quét Drive
validated_content = st.session_state.get("validated_content", [])
if not validated_content:
    st.warning("⚠️ Chưa có dữ liệu media hợp lệ. Vui lòng vào trang **2_📂_Google_Drive** để quét thư mục trước.")
    st.stop()

# 1. Cấu hình Brand Brain mẫu (hoặc tải từ Settings)
with st.expander("⚙️ Cấu hình Brand Brain (Văn phong thương hiệu)", expanded=False):
    col1, col2 = st.columns(2)
    brand_name = col1.text_input("Tên thương hiệu:", value="Thiên Tín Media")
    voice_tone = col2.text_input("Tone giọng:", value="Chuyên nghiệp, chuyên gia, hiện đại, uy tín")
    target_audience = col1.text_area("Đối tượng mục tiêu:", value="Chủ doanh nghiệp, Marketer, Khách hàng 25-45 tuổi")
    products = col2.text_area("Sản phẩm / Dịch vụ:", value="Truyền thông số, Sản xuất video, Marketing trọn gói")
    keywords = col1.text_input("Từ khóa ưu tiên (cách nhau bởi dấu phẩy):", value="truyền thông, marketing số, video chuyên nghiệp")
    forbidden_words = col2.text_input("Từ cấm tuyệt đối:", value="cam kết 100%, lừa đảo, số 1 việt nam")
    default_cta = st.text_input("CTA mặc định:", value="Inbox ngay để nhận tư vấn chiến lược miễn phí!")

brand_profile = {
    "name": brand_name,
    "voice_tone": voice_tone,
    "target_audience": target_audience,
    "products": products,
    "keywords": [k.strip() for k in keywords.split(",") if k.strip()],
    "forbidden_words": [w.strip() for w in forbidden_words.split(",") if w.strip()],
    "default_cta": default_cta
}

st.subheader(f"📦 Danh sách nội dung chờ xử lý: {len(validated_content)} mục")

if st.button("🚀 Bắt đầu Tạo Toàn Bộ Nội Dung với Gemini", type="primary"):
    progress_bar = st.progress(0)
    status_text = st.empty()
    generated_results = []

    try:
        engine = GeminiContentEngine()
        for idx, item in enumerate(validated_content):
            status_text.text(f"Đang phân tích và tạo nội dung cho ID: {item['content_id']} ({item['title']})...")
            
            res = engine.generate_content(
                content_id=item["content_id"],
                raw_title=item["title"],
                brand_profile=brand_profile,
                media_type=item["media"]["file_type"]
            )

            generated_results.append({
                "content_id": item["content_id"],
                "raw_title": item["title"],
                "media_name": item["media"]["file_name"],
                "drive_url": item["media"]["drive_url"],
                "media_type": item["media"]["file_type"],
                "data": res
            })

            progress_bar.progress((idx + 1) / len(validated_content))

        st.session_state["generated_content"] = generated_results
        status_text.text("✅ Hoàn tất tạo nội dung!")
        st.success(f"Đã tạo thành công {len(generated_results)} gói nội dung đa nền tảng!")

    except Exception as e:
        st.error(f"Lỗi trong quá trình chạy AI: {str(e)}")

# 2. Hiển thị và Xem trước Kết quả
if "generated_content" in st.session_state:
    st.divider()
    st.subheader("📑 Xem trước và Đánh giá Nội dung")
    
    results = st.session_state["generated_content"]
    selected_cid = st.selectbox("Chọn Content ID để xem chi tiết:", [r["content_id"] for r in results])
    
    selected_item = next(r for r in results if r["content_id"] == selected_cid)
    data = selected_item["data"]

    # Hiển thị Content Score & DNA
    col_score, col_dna = st.columns([1, 2])
    with col_score:
        st.metric(
            label="Overall Score", 
            value=f"{data.score.overall_score}/10", 
            delta="Đạt chuẩn duyệt" if data.score.overall_score >= 8.5 else "Cần tối ưu"
        )
        st.write(f"**Pillar:** `{data.dna.pillar_name}`")
        st.write(f"**Hook Score:** {data.score.hook}/10")
        st.write(f"**SEO Score:** {data.score.seo}/10")
        st.write(f"**Brand Fit:** {data.score.brand_fit}/10")
        
        if data.score.improvement_suggestions:
            st.info("💡 **Gợi ý:** " + "; ".join(data.score.improvement_suggestions))

    with col_dna:
        st.markdown("**🧬 Content DNA:**")
        st.write(f"- **Chủ đề:** {data.dna.topic}")
        st.write(f"- **Khán giả:** {data.dna.target_audience}")
        st.write(f"- **Nỗi đau:** {data.dna.pain_point}")
        st.write(f"- **Thông điệp chính:** {data.dna.main_message}")
        st.write(f"- **Từ khóa:** {', '.join(data.dna.keywords)}")

    # Hiển thị Tabs Nội dung Đa nền tảng
    tab_fb, tab_tt, tab_yt = st.tabs(["📘 Facebook", "🎵 TikTok", "▶️ YouTube"])

    with tab_fb:
        st.text_input("Facebook Hook:", value=data.facebook.title_hook, key=f"fb_hook_{selected_cid}")
        st.text_area("Facebook Caption:", value=data.facebook.caption, height=180, key=f"fb_cap_{selected_cid}")
        st.text_input("Hashtags:", value=" ".join(data.facebook.hashtags), key=f"fb_tags_{selected_cid}")
        st.text_input("CTA:", value=data.facebook.cta, key=f"fb_cta_{selected_cid}")

    with tab_tt:
        st.text_area("TikTok Hook & Caption:", value=data.tiktok.hook_caption, height=120, key=f"tt_cap_{selected_cid}")
        st.text_input("Hashtags:", value=" ".join(data.tiktok.hashtags), key=f"tt_tags_{selected_cid}")
        st.text_input("CTA:", value=data.tiktok.cta, key=f"tt_cta_{selected_cid}")

    with tab_yt:
        st.text_input("YouTube SEO Title (CTR Optimized):", value=data.youtube.seo_title, key=f"yt_title_{selected_cid}")
        st.text_area("YouTube Description:", value=data.youtube.description, height=160, key=f"yt_desc_{selected_cid}")
        st.text_input("YouTube Tags:", value=", ".join(data.youtube.tags), key=f"yt_tags_{selected_cid}")
        st.text_area("Chapters & Timestamps:", value=data.youtube.chapters, height=80, key=f"yt_chap_{selected_cid}")
        st.text_input("FAQ:", value=data.youtube.faq, key=f"yt_faq_{selected_cid}")
