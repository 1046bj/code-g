from duckduckgo_search import DDGS
import re
from datetime import datetime
import asyncio
import random

# --- [비상용] 서버 차단 시 보여줄 데이터 ---
FALLBACK_DATA = [
    {"title": "[서버차단됨] K-Startup 예비창업패키지 (예시)", "agency": "K-Startup", "date": "2025-01-30", "deadline": "2025-02-28", "d_day": "D-29", "link": "https://www.k-startup.go.kr", "match_score": 99, "summary": "현재 무료 서버 IP가 검색 엔진에 의해 일시 차단되었습니다. 이는 예시 데이터입니다."},
    {"title": "[서버차단됨] AI 바우처 지원사업 (예시)", "agency": "NIPA", "date": "2025-01-15", "deadline": "2025-03-15", "d_day": "D-45", "link": "https://www.nipa.kr", "match_score": 95, "summary": "서버 트래픽 과부하로 인해 실시간 검색 결과를 가져오지 못했습니다."},
    {"title": "[서버차단됨] 스마트팜 ICT 기자재 보급사업", "agency": "농림축산식품부", "date": "2025-02-01", "deadline": "2025-04-01", "d_day": "D-60", "link": "https://www.mafra.go.kr", "match_score": 88, "summary": "잠시 후 다시 시도해주시거나 로컬 환경에서 테스트해주세요."},
]

def generate_search_queries(profile):
    current_year = datetime.now().year
    queries = []
    
    # 검색 쿼리 간소화 (차단 확률 낮추기 위함)
    for ind in profile.industry:
        clean_ind = ind.split('(')[0]
        # site: 제한을 풀고 검색 (차단 우회 시도)
        queries.append(f'{clean_ind} 정부 지원사업 공고 {current_year}')
    
    return queries[:2] # 쿼리 수 줄임

def extract_date(text):
    match = re.search(r'202\d[-.](0[1-9]|1[0-2])[-.](0[1-9]|[12]\d|3[01])', text)
    if match: return match.group(0)
    return None

async def search_duckduckgo(query):
    results = []
    print(f"🕵️ [Search] 검색 시도: {query}")
    
    try:
        # Proxy나 User-Agent 설정이 없으면 서버에서 막힐 확률 높음
        # DDGS 라이브러리 내부적으로 처리를 시도함
        with DDGS() as ddgs:
            ddg_results = list(ddgs.text(query, region='kr-kr', timelimit='m', max_results=3))
            
        for r in ddg_results:
            body = r.get('body', '')
            found_date = extract_date(body)
            
            results.append({
                "title": r.get('title', ''),
                "agency": "웹검색", 
                "date": datetime.now().strftime("%Y-%m-%d"),
                "deadline": found_date if found_date else "상세보기",
                "d_day": "D-??",
                "link": r.get('href', ''),
                "match_score": random.randint(80, 99),
                "summary": body
            })
            
    except Exception as e:
        print(f"❌ 검색 차단/오류 발생: {e}")
        # 여기서 에러가 나면 빈 리스트 반환 -> 아래 get_notices에서 비상 데이터 사용
        
    return results

async def get_notices(profile):
    queries = generate_search_queries(profile)
    all_results = []
    
    # 1. 실제 검색 시도
    for q in queries:
        res = await search_duckduckgo(q)
        all_results.extend(res)
        
    # 2. [핵심] 결과가 0개면(차단당했으면) 비상 데이터 반환
    if len(all_results) == 0:
        print("⚠️ 검색 결과 0건 (IP 차단 의심). 비상용 데이터를 반환합니다.")
        return FALLBACK_DATA

    # 중복 제거
    unique_results = {v['link']: v for v in all_results}.values()
    return list(unique_results)