import os
import json
from typing import Dict, Any, List
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

class OptimizationRecommendation(BaseModel):
    insight_type: str = Field(description="Loại insight: PILLAR_PERFORMANCE, TIMING_OPTIMIZATION, HOOK_STYLE, CTA_EFFECTIVENESS")
    summary: str = Field(description="Tóm tắt ngắn gọn nhận định (dưới 100 từ)")
    detailed_recommendation: str = Field(description="Hành động cụ thể cần áp dụng cho các đợt content tiếp theo")
    confidence_score: float = Field(description="Độ tin cậy của đề xuất (0.0 - 1.0)")

class AnalyticsAnalysisResult(BaseModel):
    best_performing_pillar: str = Field(description="Pillar đạt hiệu suất cao nhất")
    underperforming_pillar: str = Field(description="Pillar cần cải thiện hoặc cắt giảm")
    recommended_posting_hours: List[str] = Field(description="Khung giờ vàng đề xuất cho từng kênh")
    recommendations: List[OptimizationRecommendation]

class AnalyticsEngine:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY không được tìm thấy.")
        self.client = genai.Client(api_key=self.api_key)

    def analyze_performance_and_recommend(
        self, 
        brand_name: str, 
        performance_data: List[Dict[str, Any]]
    ) -> AnalyticsAnalysisResult:
        system_instruction = """
        Bạn là Chief Data Officer kiêm Chuyên gia Tối ưu Chiến dịch Truyền thông Số.
        Nhiệm vụ: Phân tích số liệu thực tế từ mạng xã hội (Views, Likes, Comments, Engagement Rate), so sánh hiệu quả giữa các Content Pillar, khung giờ đăng và phong cách Hook.
        Đưa ra các Đề xuất Tối ưu (Actionable Recommendations) có tính ứng dụng cao, logic và dựa trên dữ liệu.
        """

        prompt = f"""
        [THÔNG TIN THƯƠNG HIỆU]
        - Thương hiệu: {brand_name}

        [DỮ LIỆU HIỆU SUẤT BÀI ĐĂNG (ANALYTICS METRICS)]
        {json.dumps(performance_data, ensure_ascii=False, indent=2)}

        Hãy phân tích và trả về kết quả theo đúng cấu trúc JSON Schema.
        """

        response = self.client.models.generate_content(
            model="gemini-2.5-pro",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=AnalyticsAnalysisResult,
                temperature=0.4,
            )
        )

        return AnalyticsAnalysisResult.model_validate_json(response.text)
