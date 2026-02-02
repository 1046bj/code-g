import requests
from bs4 import BeautifulSoup
import time

# =========================================================
# 안전한 분석기 (에러 방지 기능 포함)
# =========================================================
def analyze_content(url, title):
    print(f"⚡ [Analyzer] 분석 시작: {title}")
    print(f"    🔗 URL: {url}")
    
    # 1. URL이 없으면 바로 종료
    if not url or url == '-':
        return {"summary": "❌ 분석할 URL 정보가 없습니다."}

    try:
        # 2. 웹페이지 내용 긁어오기 (크롤링)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=5)
        
        # 3. 텍스트만 추출
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 스크립트, 스타일 태그 제거 (깔끔하게)
        for script in soup(["script", "style"]):
            script.decompose()
            
        text = soup.get_text()
        
        # 공백 정리
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # 4. 요약 만들기 (AI 없이도 동작하도록)
        # 본문 앞부분 300자를 가져와서 요약처럼 보여줌
        summary_text = clean_text[:400]
        
        if len(summary_text) < 50:
            final_summary = "🔒 보안으로 보호된 사이트이거나 내용이 이미지로 되어 있어 텍스트를 가져올 수 없습니다. 원본 링크를 확인해주세요."
        else:
            final_summary = f"🔍 [자동 추출 요약]\n\n{summary_text}...\n\n(더 자세한 내용은 원본 공고를 참고하세요)"

        print("✅ 분석 완료!")
        return {"summary": final_summary}

    except Exception as e:
        print(f"💥 분석 중 에러 발생: {e}")
        return {"summary": f"⚠️ 분석 실패: 웹사이트 접속이 차단되었거나 주소가 올바르지 않습니다. ({str(e)})"}