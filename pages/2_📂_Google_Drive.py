import streamlit as st
import pandas as pd
from core.ingestion.drive_scanner import DriveScannerService

st.set_page_config(page_title="Google Drive Scanner | TeMead", layout="wide")
st.title("📂 Đồng bộ & Đối chiếu Thư viện Google Drive")

st.markdown("""
Nhập ID thư mục Google Drive để hệ thống tự động:
1. Quét toàn bộ tệp Media (Video/Hình ảnh) và file danh sách tiêu đề (`.xlsx`).
2. Tự động liên kết qua **Content ID** (Ví dụ: `001.mp4` ↔ `001`).
3. Kiểm tra tính toàn vẹn và phát hiện lỗi dữ liệu.
""")

folder_id = st.text_input("Nhập Google Drive Folder ID:", placeholder="Ví dụ: 1A2b3C4d5E6f7G8h9I0j...")

if st.button("🚀 Bắt đầu Quét & Đối chiếu", type="primary"):
    if not folder_id.strip():
        st.error("Vui lòng nhập Folder ID trước khi quét.")
    else:
        with st.spinner("Đang tải dữ liệu từ Google Drive và xác thực..."):
            try:
                # Lấy credentials đã xác thực từ session_state
                mock_credentials = st.session_state.get("google_creds", {})
                
                # Khởi tạo scanner service
                scanner = DriveScannerService(credentials=mock_credentials)
                summary, validated_data = scanner.scan_folder(folder_id.strip())

                # Hiển thị Metric Thống kê
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Tổng Media Quét Được", summary["total_media"])
                col2.metric("Tổng Tiêu Đề Trong Excel", summary["total_titles"])
                col3.metric("Nội Dung Hợp Lệ (Khớp 100%)", summary["valid_count"])
                col4.metric("Lỗi / Thiếu Khớp", len(summary["missing_titles"]) + len(summary["missing_media"]))

                st.subheader("📋 Bảng Báo Cáo Đối Chiếu Toàn Vẹn")
                st.dataframe(summary["report_df"], use_container_width=True)

                if summary["valid_count"] > 0:
                    st.success(f"Đã chuẩn bị sẵn {summary['valid_count']} nội dung hợp lệ cho AI Content Engine.")
                    st.session_state["validated_content"] = validated_data

            except Exception as e:
                st.error(f"Lỗi trong quá trình xử lý: {str(e)}")
