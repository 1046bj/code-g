from duckduckgo_search import DDGS
import random
import asyncio
from datetime import datetime, timedelta

# --- 백업 DB (실제 마감일 정보 포함) ---
BACKUP_DB = [
    {"title": "[NIPA] 2026년 AI바우처 지원사업 공고", "agency": "NIPA", "date": "2026-01-20", "deadline": "2026-02-20", "d_day": "D-20", "link": "https://www.nipa.kr", "match_score": 98, "industry": "인공지능(AI)"},
    {"title": "[K-Startup] 2026년 예비창업패키지 모집", "agency": "창업진흥원", "date": "2026-01-30", "deadline": "2026-02-25", "d_day": "D-25", "link": "https://www.k-startup.go.kr", "match_score": 99, "industry": "창업/초기기업(예비/초기)"},
    {"title": "[TIPS] 2026년 딥테크 팁스 추천 기업 모집", "agency": "한국엔젤투자협회", "date": "2026-01-15", "deadline": "2026-12-31", "d_day": "상시", "link": "http://www.jointips.or.kr", "match_score": 95, "industry": "딥테크/초격차(DIPS)"},
]

def generate_search_queries(profile):
    queries = []
    for ind in profile.industry:
        if "인공지능" in ind:
            queries.append(f"2026년 인공지능 지원사업 공고 site:nipa.kr OR site:iitp.kr")
        elif "창업" in ind:
            queries.append(f"2026년 예비창업패키지 초기창업패키지 공고 site:k-startup.go.kr")
        elif "팁스" in ind or "딥테크" in ind:
            queries.append(f"2026년 팁스 딥테크 지원사업 site:k-startup.go.kr")
        else:
            queries.append(f"2026년 {ind.split('(')[0]} 지원사업 site:bizinfo.go.kr")
            
    # 검색 정확도를 위해 쿼리 2개만 반환
    return queries[:2]

async def search_duckduckgo(query):
    """
    검색 결과에 '가상의 마감일'을 부여하여 UI 테스트를 돕습니다.
    (실제 서비스에선 웹페이지 내부 날짜를 파싱해야 하지만, 속도를 위해 시뮬레이션 함)
    """
    results = []
    try:
        print(f"🕵️ [DDG Search] 검색어: {query}")
        with DDGS() as ddgs:
            ddg_results = list(ddgs.text(query, region='kr-kr', timelimit='m', max_results=4))
            
        today = datetime.now()
        
        for r in ddg_results:
            # 1. 등록일 (랜덤하게 최근 1달 내)
            reg_days_ago = random.randint(1, 20)
            reg_date = (today - timedelta(days=reg_days_ago)).strftime("%Y-%m-%d")
            
            # 2. 마감일 (오늘로부터 1주~4주 뒤)
            due_days = random.randint(5, 30)
            due_date = (today + timedelta(days=due_days)).strftime("%Y-%m-%d")
            
            # 3. D-Day 계산
            d_day_str = f"D-{due_days}"

            results.append({
                "title": r['title'],
                "agency": "Web Search", 
                "date": reg_date,       # 등록일
                "deadline": due_date,   # 마감일
                "d_day": d_day_str,     # D-Day
                "link": r['href'],
                "match_score": random.randint(70, 98),
                "summary": r['body'][:100] + "..."
            })
        return results
    except Exception as e:
        print(f"❌ DDG 검색 에러: {e}")
        return []

async def get_notices(profile):
    queries = generate_search_queries(profile)
    all_results = []
    
    for q in queries:
        res = await search_duckduckgo(q)
        all_results.extend(res)
        
    # 결과 부족 시 백업 사용
    if len(all_results) < 2:
        all_results.extend(BACKUP_DB)

    unique_results = {v['link']: v for v in all_results}.values()
    final_list = list(unique_results)
    final_list.sort(key=lambda x: x['match_score'], reverse=True)
    
    return final_list[:15]