from duckduckgo_search import DDGS
import re
from datetime import datetime

# --- [중요] 가짜 데이터(BACKUP_DB) 삭제함 ---

def generate_search_queries(profile):
    """
    사용자 프로필을 기반으로 '올해' 실제 공고를 검색할 쿼리를 만듭니다.
    """
    current_year = datetime.now().year # 실제 현재 연도(2025)를 가져옴
    queries = []
    
    # 산업분야별 검색어 생성
    for ind in profile.industry:
        # 검색어 최적화 (정확도를 위해 사이트 지정)
        clean_ind = ind.split('(')[0] # "인공지능(AI)" -> "인공지능"
        queries.append(f"{current_year}년 {clean_ind} 지원사업 공고 모집")
        
    # 목적별 검색어 추가 (예: 예비창업패키지)
    if "사업화 자금" in profile.goal:
        queries.append(f"{current_year}년 예비창업패키지 초기창업패키지 모집 공고")
    elif "R&D" in profile.goal:
        queries.append(f"{current_year}년 중소기업 기술개발 지원사업 공고")
            
    return queries[:3] # 속도를 위해 최대 3개 쿼리만 실행

def extract_date(text):
    """
    검색 요약글(Snippet)에서 날짜 형식(YYYY-MM-DD 또는 MM.DD)을 찾습니다.
    """
    # 202x-xx-xx 형식 찾기
    match = re.search(r'202\d[-.](0[1-9]|1[0-2])[-.](0[1-9]|[12]\d|3[01])', text)
    if match:
        return match.group(0)
    return None

async def search_duckduckgo(query):
    """
    진짜 인터넷 검색 결과만 반환합니다. (가짜 데이터 없음)
    """
    results = []
    print(f"🕵️ [Real-Search] 검색어: {query}")
    
    try:
        with DDGS() as ddgs:
            # region='kr-kr'로 한국 결과 우선 검색
            ddg_results = list(ddgs.text(query, region='kr-kr', timelimit='w', max_results=5))
            
        for r in ddg_results:
            title = r.get('title', '')
            link = r.get('href', '')
            body = r.get('body', '')
            
            # 본문에서 날짜 추정 (없으면 '상세확인')
            found_date = extract_date(body)
            deadline_str = found_date if found_date else "공고문 확인"
            d_day_str = "D-??" # 정확한 마감일은 상세페이지에만 있어서 물음표 처리

            # 기관명 추정 (제목 앞부분이나 도메인으로 유추)
            agency = "정부공고"
            if "k-startup" in link: agency = "K-Startup"
            elif "nipa" in link: agency = "NIPA"
            elif "kaist" in link: agency = "KAIST"
            
            results.append({
                "title": title,
                "agency": agency, 
                "date": datetime.now().strftime("%Y-%m-%d"), # 검색 시점
                "deadline": deadline_str,
                "d_day": d_day_str,
                "link": link,
                "match_score": 80, # 기본 점수
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
        
    # 중복 제거 (링크 기준)
    unique_results = {v['link']: v for v in all_results}.values()
    final_list = list(unique_results)
    
    return final_list