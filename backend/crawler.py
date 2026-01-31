from duckduckgo_search import DDGS
import re
from datetime import datetime
import asyncio

# --- [설정] 대한민국 핵심 정부지원/공고 사이트 리스트 (15곳) ---
TARGET_SITES_MAP = {
    "k-startup.go.kr": "K-Startup",
    "bizinfo.go.kr": "기업마당",
    "g2b.go.kr": "나라장터", 
    "kvic.or.kr": "한국벤처투자",
    "smtech.go.kr": "SMTech",
    "nrf.re.kr": "한국연구재단",
    "iris.go.kr": "IRIS",
    "nipa.kr": "NIPA",
    "iitp.kr": "IITP",
    "keit.re.kr": "KEIT",
    "kocca.kr": "콘텐츠진흥원",
    "khidi.or.kr": "보건산업진흥원",
    "nia.or.kr": "NIA",
    "tp.or.kr": "테크노파크",
    "venture.or.kr": "벤처기업협회"
}

def generate_search_queries(profile):
    current_year = datetime.now().year
    queries = []
    
    # --- 1차: 핵심 사이트 그룹핑 검색 ---
    # 그룹을 너무 잘게 쪼개지 말고, 가장 중요한 '종합'과 '기술'로만 나눕니다.
    
    sites_biz = [
        "site:k-startup.go.kr", "site:bizinfo.go.kr", "site:g2b.go.kr", 
        "site:smtech.go.kr", "site:nipa.kr", "site:nrf.re.kr"
    ]
    # 쿼리 길이 제한을 피하기 위해 핵심 6곳만 우선 타겟팅
    query_sites = "(" + " OR ".join(sites_biz) + ")"

    for ind in profile.industry:
        clean_ind = ind.split('(')[0]
        # 따옴표("")를 제거하여 검색 유연성 확보 (ex: "인공지능" -> 인공지능)
        queries.append(f'{query_sites} {clean_ind} 지원사업 공고 {current_year}')

    # 목적별 검색
    if "사업화" in profile.goal:
        queries.append(f'site:k-startup.go.kr 예비창업패키지 초기창업패키지 {current_year}')
    
    return queries[:3]

def get_fallback_queries(profile):
    """
    [비상용] 1차 검색 결과가 없을 때 사용할 '광역 검색' 쿼리
    특정 사이트 제한을 풀되, 위키/블로그 등 노이즈를 제외함
    """
    current_year = datetime.now().year
    queries = []
    
    # 제외어 설정 (위키, 나무위키, 블로그 등)
    exclude = "-site:wikipedia.org -site:namu.wiki -site:tistory.com -site:blog.naver.com"
    
    for ind in profile.industry:
        clean_ind = ind.split('(')[0]
        # 사이트 제한 없이 '정부지원' 키워드로 검색
        queries.append(f'{clean_ind} 정부 지원사업 공고 {current_year} {exclude}')
        
    return queries[:2]

def extract_date(text):
    match = re.search(r'202\d[-.](0[1-9]|1[0-2])[-.](0[1-9]|[12]\d|3[01])', text)
    if match: return match.group(0)
    return None

def detect_agency(link):
    for domain, name in TARGET_SITES_MAP.items():
        if domain in link: return name
    return "정부공고" # 사이트 리스트에 없으면 일반 정부공고로 표시

async def search_duckduckgo(query, is_fallback=False):
    results = []
    print(f"🕵️ [{'Fallback' if is_fallback else 'Target'}-Search] 검색어: {query}")
    
    try:
        with DDGS() as ddgs:
            # 검색 결과가 없으면 바로 리턴
            ddg_results = list(ddgs.text(query, region='kr-kr', timelimit='m', max_results=5))
            
        for r in ddg_results:
            link = r.get('href', '')
            agency = detect_agency(link)
            found_date = extract_date(r.get('body', ''))
            
            # Fallback 모드일 때, 너무 엉뚱한 사이트(쇼핑몰 등)가 걸릴 수 있으므로 
            # 제목에 '공고'나 '모집'이 없으면 거르는 필터를 추가할 수도 있음.
            
            results.append({
                "title": r.get('title', '').split(" - ")[0], 
                "agency": agency, 
                "date": datetime.now().strftime("%Y-%m-%d"),
                "deadline": found_date if found_date else "공고문 참조",
                "d_day": "D-??",
                "link": link,
                "match_score": 70 if is_fallback else 90, # Fallback 결과는 점수를 좀 낮게 줌
                "summary": r.get('body', '')
            })
            
    except Exception as e:
        print(f"❌ 검색 오류: {e}")
        
    return results

async def get_notices(profile):
    # 1. 정밀 타겟팅 검색 실행
    queries = generate_search_queries(profile)
    all_results = []
    
    for q in queries:
        res = await search_duckduckgo(q, is_fallback=False)
        all_results.extend(res)
        
    # 2. [안전장치] 만약 결과가 너무 적으면(2개 미만), 광역 검색(Fallback) 실행
    if len(all_results) < 2:
        print("⚠️ 결과 부족! 안전장치(Fallback) 검색을 가동합니다.")
        fallback_queries = get_fallback_queries(profile)
        for q in fallback_queries:
            res = await search_duckduckgo(q, is_fallback=True)
            all_results.extend(res)

    # 중복 제거
    unique_results = {v['link']: v for v in all_results}.values()
    final_list = list(unique_results)
    
    # 결과가 있어도 에러가 안 나게 빈 리스트라도 반환
    return final_list