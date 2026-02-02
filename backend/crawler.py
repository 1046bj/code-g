import requests
import sqlite3
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from urllib.parse import unquote

# ==========================================
# 1. 설정
# ==========================================
API_KEY_RAW = "d89c618d3ff720dfaa7da509d296a9c8d32f2ec90592ffa1e3c0a73f32dce7f4"
API_KEY_DECODED = unquote(API_KEY_RAW)
DB_NAME = "kstartup.db"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS notices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT, title TEXT, category TEXT, region TEXT,
            start_date TEXT, end_date TEXT, agency TEXT, target TEXT,
            url TEXT UNIQUE, crawled_at DATETIME
        )
    """)
    conn.commit()
    conn.close()

# ==========================================
# 2. [핵심] 스마트 재분류 함수
# ==========================================
def smart_classify(notice):
    """
    K-Startup이나 조달청 데이터 중에서 
    실제 주관기관이 '중기부'나 'NIPA'인 것을 찾아내어 소스를 변경함
    """
    title = notice['title']
    agency = notice['agency']
    
    # 1. 중소벤처기업부(중기부) 식별
    if "중소벤처기업부" in agency or "지방중소벤처기업청" in agency:
        notice['source'] = "중기부"
    
    # 2. NIPA(정보통신산업진흥원) 식별
    elif "정보통신산업진흥원" in agency or "NIPA" in title or "정보통신산업진흥원" in title:
        notice['source'] = "NIPA"
        
    return notice

def normalize_data(source, item):
    notice = {"source": source, "title": "-", "category": "지원사업", "region": "전국", 
              "start_date": "-", "end_date": "-", "agency": "-", "target": "제한없음", "url": "-"}
    try:
        # [1] 창업진흥원 (K-Startup)
        if source == "창업진흥원":
            notice["title"] = item.get('biz_pbanc_nm', '제목없음')
            notice["url"] = item.get('detl_pg_url') or item.get('biz_gdnc_url') or '-'
            notice["start_date"] = item.get('pbanc_rcpt_bgng_dt', '-')
            notice["agency"] = item.get('sprv_inst', '창업진흥원') # 주관기관
            notice["category"] = item.get('supt_biz_clsfc', '창업지원')

        # [2] 조달청 (나라장터)
        elif source == "조달청":
            notice["title"] = item.get('bidNtceNm', '제목없음')
            notice["url"] = item.get('bidNtceDtlUrl', '-')
            notice["start_date"] = item.get('bidNtceDt', '-')[:10]
            notice["agency"] = item.get('dminsttNm', '조달청') # 수요기관
            notice["category"] = "공공입찰"

        # [3] 과기정통부
        elif source == "과기정통부":
            notice["title"] = item.get('subject', '제목없음')
            notice["url"] = item.get('viewUrl', '-')
            notice["start_date"] = item.get('pressDt', '-')
            notice["agency"] = item.get('deptName', '과학기술정보통신부')

        # [4] 식약처
        elif source == "식약처":
            notice["title"] = item.get('PBLANC_NM', '제목없음')
            p_no = item.get('PBLANC_NO')
            notice["url"] = f"https://www.mfds.go.kr/search/search.do?searchTerm={p_no}" if p_no else "-"
            notice["agency"] = "식품의약품안전처"
            notice["start_date"] = item.get('RCEPT_BEGIN_DTE', '-')

        # [5] NIPA (직접 수집용 - 보조)
        elif source == "NIPA":
            notice["title"] = item.get('제목') or item.get('공고명') or '제목없음'
            notice["url"] = item.get('링크') or 'https://www.nipa.kr'
            notice["agency"] = "정보통신산업진흥원"

    except: pass
    
    if notice['title'] == '-' or notice['title'] == '제목없음': return None
    
    # [중요] 스마트 재분류 실행
    notice = smart_classify(notice)
    
    return notice

# ==========================================
# 3. 기관별 수집 (안정적인 4대장 위주)
# ==========================================

def get_kstartup():
    print("📡 [1/4] 창업진흥원 (K-Startup) 수집...")
    # K-Startup에는 중기부, NIPA, 과기부 공고가 모두 모여있습니다.
    url = "https://apis.data.go.kr/B552735/kisedKstartupService01/getAnnouncementInformation01"
    params = {"serviceKey": API_KEY_RAW, "page": "1", "perPage": "1000", "returnType": "json", "rcrt_prgs_yn": "Y"}
    try:
        res = requests.get(url, params=params, headers=HEADERS, timeout=10)
        items = res.json().get('data', [])
        return [normalize_data("창업진흥원", i) for i in items]
    except: return []

def get_nara():
    print("📡 [2/4] 조달청 (나라장터) 수집...")
    # 나라장터에도 NIPA 용역 입찰이 올라옵니다.
    url = "http://apis.data.go.kr/1230000/ad/BidPublicInfoService/getBidPblancListInfoServcPPSSrch"
    now = datetime.now()
    ago = now - timedelta(days=14)
    params = {"serviceKey": API_KEY_RAW, "numOfRows": "800", "pageNo": "1", "type": "json",
              "inqryDiv": "1", "inqryBgnDt": ago.strftime("%Y%m%d")+"0000", "inqryEndDt": now.strftime("%Y%m%d")+"2359"}
    try:
        res = requests.get(url, params=params, headers=HEADERS, timeout=10)
        items = res.json().get('response', {}).get('body', {}).get('items', [])
        return [normalize_data("조달청", i) for i in items]
    except: return []

def get_msit():
    print("📡 [3/4] 과기정통부 수집...")
    url = "http://apis.data.go.kr/1721000/msitannouncementinfo/businessAnnouncMentList"
    params = {"serviceKey": API_KEY_RAW, "numOfRows": "100", "pageNo": "1"}
    try:
        res = requests.get(url, params=params, headers=HEADERS, timeout=10)
        root = ET.fromstring(res.content)
        items = [{child.tag: child.text for child in item} for item in root.findall('.//item')]
        return [normalize_data("과기정통부", i) for i in items]
    except: return []

def get_mfds():
    print("📡 [4/4] 식약처 수집...")
    url = "https://apis.data.go.kr/1471057/RNDBSNSPBLANC01/getRndbsnspblanc01"
    params = {"serviceKey": API_KEY_DECODED, "pageNo": "1", "numOfRows": "200", "type": "xml"}
    try:
        res = requests.get(url, params=params, headers=HEADERS, timeout=30)
        root = ET.fromstring(res.content)
        items = [{child.tag: child.text for child in item} for item in root.findall('.//item')]
        return [normalize_data("식약처", i) for i in items]
    except: return []

# ==========================================
# 4. 실행 및 저장
# ==========================================
def save_to_db(data_list):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    new_cnt = 0
    for d in data_list:
        if not d: continue
        try:
            cur.execute("""
                INSERT OR IGNORE INTO notices 
                (source, title, category, region, start_date, end_date, agency, target, url, crawled_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                d['source'], d['title'], d['category'], d['region'],
                d['start_date'], d['end_date'], d['agency'], d['target'],
                d['url'], datetime.now()
            ))
            if cur.rowcount > 0: new_cnt += 1
        except: pass
    conn.commit()
    conn.close()
    return new_cnt

def run_crawler():
    print("\n🚀 [Code-G] 통합 수집 & 스마트 분류 엔진 가동")
    init_db()
    
    all_data = []
    
    # 1. 대량 데이터 수집
    k_data = get_kstartup()
    nara_data = get_nara()
    msit_data = get_msit()
    mfds_data = get_mfds()
    
    all_data.extend(k_data)
    all_data.extend(nara_data)
    all_data.extend(msit_data)
    all_data.extend(mfds_data)
    
    if all_data:
        saved = save_to_db(all_data)
        
        # 2. 결과 분석 (재분류된 결과 확인)
        sources = {}
        for d in all_data:
            if not d: continue
            src = d['source']
            sources[src] = sources.get(src, 0) + 1
            
        print(f"\n✅ 최종 수집 완료: 총 {len(all_data)}개 (신규 {saved}개)")
        print("-" * 40)
        print(f"📊 [스마트 분류 결과]")
        print(f"   - 중기부 (K-Startup 추출 포함): {sources.get('중기부', 0)}개")
        print(f"   - NIPA (주관기관 추출):       {sources.get('NIPA', 0)}개")
        print(f"   - 과기정통부:                 {sources.get('과기정통부', 0)}개")
        print(f"   - 식약처:                     {sources.get('식약처', 0)}개")
        print(f"   - 창업진흥원:                 {sources.get('창업진흥원', 0)}개")
        print(f"   - 조달청:                     {sources.get('조달청', 0)}개")
        print("-" * 40)
        
    else:
        print("\n❌ 데이터 없음")

if __name__ == "__main__":
    run_crawler()