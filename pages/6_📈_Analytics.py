import streamlit as st
import pandas as pd
from core.engine.analytics_engine import AnalyticsEngine

st.set_page_config(page_title="Báo Cáo Hiệu Suất & AI Insights | TeMead", layout="wide")
st.title("📈 Phân Tích Hiệu Suất & AI Khuyến Nghị Chiến Lược")

# Dữ liệu mẫu đo lường thực tế từ các bài đã xuất bản
sample_metrics = [
    {"content_id": "001", "pillar": "KIẾN THỨC", "platform": "FACEBOOK", "views": 85000, "likes": 4200, "comments": 310, "shares": 520, "time": "11:30"},
    {"content_id": "001", "pillar": "KIẾN THỨC", "platform": "TIKTOK", "views": 210000, "likes": 18500, "comments": 940, "shares": 1200, "time": "12:00"},
    {"content_id": "001", "pillar": "KIẾN THỨC", "platform": "YOUTUBE", "views": 45000, "likes": 2100, "comments": 180, "shares": 95, "time": "20:00"},
    {"content_id": "002", "pillar": "SẢN PHẨM", "platform": "FACEBOOK", "views": 18000, "likes": 650, "comments": 45, "shares": 30, "time": "19:30"},
    {"content_id": "002", "pillar": "SẢN PHẨM", "platform": "TIKTOK", "views": 32000, "likes": 1200, "comments": 80, "shares": 50, "time": "20:00"},
    {"content_id": "003", "pillar": "GIẢI ĐÁP", "platform": "TIKTOK", "views": 175000, "likes": 14200, "comments": 820, "shares": 980, "time": "12:00"},
    {"content_id": "003", "pillar": "GIẢI ĐÁP", "platform": "FACEBOOK", "views": 62000, "likes": 3100, "comments": 240, "shares": 310, "time": "11:30"},
]

df_metrics = pd.DataFrame(sample_metrics)

# 1. Tổng quan các chỉ số đo lường
col1, col2, col3, col4 = st.columns(4)
col1.metric("Tổng Lượt Xem (Total Views)", f"{df_metrics['views'].sum():,}")
col2.metric("Tổng Tương Tác (Likes & Reactions)", f"{df_metrics['likes'].sum():,}")
col3.metric("Bình Luận (Comments)", f"{df_metrics['comments'].sum():,}")
col4.metric("Lượt Chia Sẻ (Shares)", f"{df_metrics['shares'].sum():,}")

st.divider()

# 2. Biểu đồ so sánh giữa các Content Pillar
col_chart1, col_chart2 = st.columns(2)
with col_chart1:
    st.subheader("📊 Lượt Xem Theo Từng Content Pillar")
    pillar_views = df_metrics.groupby("pillar")["views"].sum().reset_index()
    st.bar_chart(pillar_views.set_index("pillar"))

with col_chart2:
    st.subheader("🌐 Phân Bổ Tương Tác Theo Nền Tảng")
    platform_views = df_metrics.groupby("platform")["views"].sum().reset_index()
    st.bar_chart(platform_views.set_index("platform"))

st.divider()

# 3. Kích hoạt AI Optimization Insights
st.subheader("🤖 AI Learning & Đề Xuất Chiến Lược Tối Ưu")

if st.button("🧠 Phân Tích Số Liệu & Sinh Đề Xuất với Gemini", type="primary"):
    with st.spinner("AI đang tính toán độ trễ tương tác và phân tích mẫu nội dung..."):
        try:
            engine = AnalyticsEngine()
            analysis_result = engine.analyze_performance_and_recommend(
                brand_name="Thiên Tín Media",
                performance_data=sample_metrics
            )

            c1, c2 = st.columns(2)
            c1.success(f"🏆 **Pillar hiệu quả nhất:** `{analysis_result.best_performing_pillar}`")
            c2.warning(f"⚠️ **Pillar cần cải thiện:** `{analysis_result.underperforming_pillar}`")

            st.write(f"⏰ **Khung giờ vàng đề xuất:** {', '.join(analysis_result.recommended_posting_hours)}")

            st.markdown("### 💡 Danh Sách Khuyến Nghị Cụ Thể:")
            for rec in analysis_result.recommendations:
                with st.expander(f"📌 [{rec.insight_type}] {rec.summary} (Độ tin cậy: {int(rec.confidence_score * 100)}%)"):
                    st.write(rec.detailed_recommendation)

        except Exception as e:
            st.error(f"Lỗi phân tích AI: {str(e)}")
