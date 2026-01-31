from duckduckgo_search import DDGS
import re
from datetime import datetime
import asyncio

# --- [설정] 대한민국 핵심 정부지원/공고 사이트 리스트 (15곳) ---
TARGET_SITES_MAP = {
    # 1. 종합/창업/조달
    "k-startup.go.kr": "K-Startup",
    "bizinfo.go.kr": "기업마당",
    "g2b.go.kr": "나라장터(입찰/공고)",  # [신규] 조달청
    "kvic.or.kr": "한국벤처투자(모태펀드)", # [강조] VC 출자사업

    # 2. R&D/기술/연구
    "smtech.go.kr": "SMTech(중기부R&D)",
    "nrf.re.kr": "한국연구재단(기초연구)", # [신규] 연구과제
    "iris.go.kr": "IRIS(범부처R&D)",
    "nipa.kr": "NIPA(AI/SW)",
    "iitp.kr": "IITP(ICT)",
    "keit.re.kr": "KEIT(산업기술)",

    # 3. 분야별 특화
    "kocca.kr": "콘텐츠진흥원",
    "khidi.or.kr": "보건산업진흥원",
    "nia.or.kr": "NIA(데이터/지능)",
    "tp.or.kr": "테크노파크(지역거점)",
    "venture.or.kr": "벤처기업협회"
}

def generate_search_queries(profile):
    """
    사이트 성격에 따라 그룹을 나누어 검색 효율을 높입니다.
    """
    current_year = datetime.now().year
    queries = []
    
    # --- 검색 그룹 정의 (URL 길이가 너무 길어지지 않게 분리) ---
    
    # Group A: 사업화, 창업자금, 조달, 투자 (돈이 급한 곳)
    sites_biz = [
        "site:k-startup.go.kr", "site:bizinfo.go.kr", 
        "site:g2b.go.kr", "site:kvic.or.kr", "site:venture.or.kr"
    ]
    query_biz = "(" + " OR ".join(sites_biz) + ")"

    # Group B: R&D, 기술개발, 연구과제 (기술 중심)
    sites_rnd = [
        "site:smtech.go.kr", "site:nrf.re.kr", "site:iris.go.kr",
        "site:nipa.kr", "site:iitp.kr", "site:keit.re.kr"
    ]
    query_rnd = "(" + " OR ".join(sites_rnd) + ")"
    
    # Group C: 특화 분야 (콘텐츠, 바이오 등 - 산업분야에 따라 선택적으로 사용 가능하나 여기선 포괄 검색)
    sites_spec = [
        "site:kocca.kr", "site:khidi.or.kr", "site:nia.or.kr", "site:tp.or.kr"
    ]
    query_spec = "(" + " OR ".join(sites_spec) + ")"

    # --- 쿼리 생성 ---
    for ind in profile.industry:
        clean_ind = ind.split('(')[0] # "인공지능"
        
        # 1. 사업화/자금 그룹에서 검색 (나라장터, 벤처투자 포함)
        queries.append(f'{query_biz} "{clean_ind}" 지원사업 공고 {current_year}')
        
        # 2. R&D 그룹에서 검색 (연구재단 포함)
        queries.append(f'{query_rnd} "{clean_ind}" 연구개발 과제 공고 {current_year}')
        
        # 3. 특화 그룹에서도 한번 훑기
        queries.append(f'{query_spec} "{clean_ind}" 지원사업 {current_year}')

    # 목적별 정밀 타겟팅
    if "조달" in profile.goal or "판로" in profile.goal:
        queries.append(f'site:g2b.go.kr "{clean_ind}" 입찰 공고 {current_year}')
    
    if "투자" in profile.goal:
        queries.append(f'site:kvic.or.kr 모태펀드 출자사업 공고 {current_year}')

    # 쿼리가 너무 많으면 느려지므로 상위 5개로 제한
    return queries[:5]

def extract_date(text):
    match = re.search(r'202\d[-.](0[1-9]|1[0-2])[-.](0[1-9]|[12]\d|3[01])', text)
    if match:
        return match.group(0)
    return None

def detect_agency(link):
    for domain, name in TARGET_SITES_MAP.items():
        if domain in link:
            return name
    return "정부공고"

async def search_duckduckgo(query):
    results = []
    print(f"🕵️ [Full-Coverage] 검색어: {query}")
    
    try:
        with DDGS() as ddgs:
            # 검색 범위 확장
            ddg_results = list(ddgs.text(query, region='kr-kr', timelimit='m', max_results=4))
            
        for r in ddg_results:
            link = r.get('href', '')
            title = r.get('title', '')
            body = r.get('body', '')
            
            agency = detect_agency(link)
            found_date = extract_date(body)
            
            results.append({
                "title": title.split(" - ")[0], 
                "agency": agency, 
                "date": datetime.now().strftime("%Y-%m-%d"),
                "deadline": found_date if found_date else "공고문 참조",
                "d_day": "D-??",
                "link": link,
                "match_score": 85 if agency != "정부공고" else 70, 
                "summary": body
            })
            
    except Exception as e:
        print(f"❌ 검색 오류: {e}")
        
    return results

async def get_notices(profile):
    queries = generate_search_queries(profile)
    all_results = []
    
    for q in queries:
        res = await search_duckduckgo(q)
        all_results.extend(res)
        
    unique_results = {v['link']: v for v in all_results}.values()
    final_list = list(unique_results)
    
    return final_list