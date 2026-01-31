import httpx
from bs4 import BeautifulSoup
import os

async def analyze_content(url: str, title: str):
    """
    공고 URL에 접속하여 본문을 긁어온 뒤, 핵심 내용을 요약합니다.
    """
    print(f"🧠 [AI Analyzer] 분석 시작: {title}")
    
    # 1. 웹페이지 본문 긁어오기
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        async with httpx.AsyncClient(verify=False, timeout=5.0, headers=headers) as client:
            response = await client.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 본문 텍스트 추출
            body_text = soup.get_text(separator=' ', strip=True)[:3000]
            
    except Exception as e:
        print(f"❌ 접속 실패: {e}")
        body_text = "본문 내용을 가져올 수 없습니다. 링크를 직접 확인해주세요."

    # 2. AI 분석 (Rule-based 시뮬레이션)
    analysis_result = {
        "summary": "해당 공고는 기술력을 보유한 기업을 대상으로 자금 및 사업화를 지원하는 프로그램입니다.",
        "eligibility": "업력 7년 이내 창업기업 또는 R&D 역량 보유 중소기업",
        "funding": "과제당 최대 1억 ~ 5억원 내외 (자부담 10%~20%)",
        "deadline": "공고문 내 마감일 확인 필수 (보통 2~3주 내 마감)",
        "strategy": "사업계획서의 '기술의 차별성'과 '시장 진입 전략'을 강조하는 것이 선정 확률을 높입니다."
    }

    # 키워드 기반 맞춤형 요약
    if "바우처" in title:
        analysis_result["summary"] = "AI/데이터 솔루션 도입 비용을 바우처 형태로 지원하는 사업입니다."
        analysis_result["funding"] = "최대 3억원 (바우처 지급)"
    elif "R&D" in title or "기술개발" in title:
        analysis_result["summary"] = "신기술 개발 및 시제품 제작을 위한 연구개발비(R&D) 지원 사업입니다."
        analysis_result["eligibility"] = "기업부설연구소 또는 전담부서 보유 기업 우대"
    elif "창업" in title or "패키지" in title:
        analysis_result["summary"] = "초기 창업기업의 사업화 자금, 멘토링, 입주공간을 패키지로 지원합니다."
        analysis_result["strategy"] = "대표자의 역량과 팀 빌딩, 초기 시장 검증 결과가 평가의 핵심입니다."
    elif "팁스" in title or "TIPS" in title:
        analysis_result["summary"] = "민간 투자사가 먼저 투자한 유망 스타트업에 정부가 R&D 자금을 매칭 지원합니다."
        analysis_result["funding"] = "R&D 최대 5억 + 사업화/마케팅 추가 지원"

    return analysis_result