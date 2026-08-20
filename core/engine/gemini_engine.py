import json
import os
from typing import Dict, Any, List
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

# Định nghĩa cấu trúc Schema đầu ra chuẩn xác
class ContentDNAModel(BaseModel):
    topic: str = Field(description="Chủ đề chính xác của nội dung")
    target_audience: str = Field(description="Đối tượng người xem mục tiêu")
    pain_point: str = Field(description="Nỗi đau hoặc vấn đề người xem gặp phải")
    main_message: str = Field(description="Thông điệp cốt lõi cần truyền tải")
    keywords: List[str] = Field(description="Danh sách từ khóa liên quan")
    cta: str = Field(description="Lời kêu gọi hành động")
    tone: str = Field(description="Giọng văn phù hợp với thương hiệu")
    objective: str = Field(description="Mục tiêu: Awareness / Engagement / Conversion")
    pillar_name: str = Field(description="Phân loại Pillar: KIẾN THỨC, SẢN PHẨM, SO SÁNH, GIẢI ĐÁP, CASE STUDY, KHUYẾN MÃI, THƯƠNG HIỆU, GIẢI TRÍ")

class FacebookContentModel(BaseModel):
    title_hook: str = Field(description="Hook mở đầu gây chú ý 3 dòng đầu")
    caption: str = Field(description="Nội dung caption đầy đủ, ngắt dòng thoáng")
    hashtags: List[str] = Field(description="Danh sách thẻ hashtag")
    cta: str = Field(description="CTA hướng dẫn tương tác hoặc nhắn tin")

class TikTokContentModel(BaseModel):
    hook_caption: str = Field(description="Caption ngắn gọn, giật tít thu hút cho video ngắn")
    hashtags: List[str] = Field(description="Danh sách thẻ hashtag xu hướng và ngành")
    cta: str = Field(description="CTA kêu gọi thả tim / bình luận / chia sẻ")

class YouTubeContentModel(BaseModel):
    seo_title: str = Field(description="Tiêu đề chuẩn SEO, tối ưu CTR dưới 100 ký tự")
    description: str = Field(description="Mô tả chi tiết chuẩn Semantic Search")
    keywords: List[str] = Field(description="Từ khóa chính của video")
    tags: List[str] = Field(description="Tags cho YouTube Studio")
    hashtags: List[str] = Field(description="Danh sách hashtag YouTube")
    chapters: str = Field(description="Đề xuất các mốc thời gian Timeline / Chapters nếu có")
    faq: str = Field(description="1-2 câu hỏi thường gặp liên quan đến chủ đề")
    cta: str = Field(description="CTA Đăng ký kênh / để lại bình luận")

class ScoreBreakdownModel(BaseModel):
    hook: float = Field(description="Điểm sức hút Hook mở đầu (0-10)")
    content_value: float = Field(description="Điểm giá trị thông tin cung cấp (0-10)")
    retention_potential: float = Field(description="Khả năng giữ chân người xem (0-10)")
    cta: float = Field(description="Độ hiệu quả của CTA (0-10)")
    seo: float = Field(description="Điểm tối ưu hóa SEO tìm kiếm (0-10)")
    brand_fit: float = Field(description="Độ khớp với giọng văn thương hiệu (0-10)")
    originality: float = Field(description="Tính sáng tạo, độc đáo (0-10)")
    overall_score: float = Field(description="Điểm tổng thể trung bình (0-10)")
    improvement_suggestions: List[str] = Field(description="Gợi ý cải thiện nếu có")

class GeneratedContentSchema(BaseModel):
    dna: ContentDNAModel
    facebook: FacebookContentModel
    tiktok: TikTokContentModel
    youtube: YouTubeContentModel
    score: ScoreBreakdownModel


class GeminiContentEngine:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY không được tìm thấy.")
        self.client = genai.Client(api_key=self.api_key)

    def generate_content(
        self, 
        content_id: str, 
        raw_title: str, 
        brand_profile: Dict[str, Any], 
        media_type: str
    ) -> GeneratedContentSchema:
        system_instruction = """
        Bạn là Senior Creative Director & Multi-Platform AI Automation Specialist.
        Nhiệm vụ: Chuyển đổi Content Topic thô thành một gói phân phối nội dung hoàn chỉnh cho Facebook, TikTok, YouTube.
        
        QUY TẮC BẮT BUỘC:
        1. Tuyệt đối KHÔNG lấy nguyên văn tựa đề thô làm tiêu đề cho mọi nền tảng.
        2. Tuân thủ Brand Voice, Target Audience và KHÔNG vi phạm các từ cấm (Forbidden Words).
        3. Facebook: Storytelling, Hook 3 dòng đầu, chia đoạn thoáng, CTA tự nhiên.
        4. TikTok: Hook giật tít, kích thích thảo luận, súc tích, hợp video ngắn.
        5. YouTube: Tối ưu SEO Title kích thích CTR, Description giàu ngữ nghĩa, đầy đủ Tags, Chapters, FAQ.
        6. Chấm điểm khách quan theo thang điểm 10.
        """

        prompt = f"""
        [BRAND PROFILE]
        - Tên thương hiệu: {brand_profile.get('name', 'Thương hiệu')}
        - Giọng văn: {brand_profile.get('voice_tone', 'Chuyên nghiệp, tin cậy')}
        - Khách hàng mục tiêu: {brand_profile.get('target_audience', 'Đại chúng')}
        - Sản phẩm/Dịch vụ: {brand_profile.get('products', 'Dịch vụ')}
        - Từ khóa ưu tiên: {', '.join(brand_profile.get('keywords', []))}
        - Từ cấm tuyệt đối: {', '.join(brand_profile.get('forbidden_words', []))}
        - Lời kêu gọi mặc định: {brand_profile.get('default_cta', 'Liên hệ ngay')}

        [DỮ LIỆU ĐẦU VÀO]
        - Content ID: {content_id}
        - Tiêu đề thô (Topic): {raw_title}
        - Định dạng Media: {media_type}

        Hãy phân tích và tạo toàn bộ nội dung theo JSON Schema yêu cầu.
        """

        response = self.client.models.generate_content(
            model="gemini-2.5-pro",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=GeneratedContentSchema,
                temperature=0.7,
            )
        )

        return GeneratedContentSchema.model_validate_json(response.text)
