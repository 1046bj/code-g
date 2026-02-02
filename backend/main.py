from fastapi import FastAPI, Body, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import sqlite3
import os
import random

# [중요] crawler.py에서 함수 가져오기
from crawler import init_db, run_crawler 
from analyzer import analyze_content 

app = FastAPI()
DB_NAME = "kstartup.db"

# --- 보안 설정 ---
origins = ["http://localhost:3000", "http://127.0.0.1:3000", "*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    if not os.path.exists(DB_NAME):
        init_db()

# ==========================================
# 1. 데이터 모델
# ==========================================
class CompanyProfile(BaseModel):
    industry: List[str] = []   
    region: str = ""           
    foundedYear: int = 0       

class AnalyzeRequest(BaseModel):
    url: str
    title: str

# ==========================================
# 2. 매칭 점수 계산기
# ==========================================
def calculate_score(notice, profile):
    score = 0
    title = str(notice.get('title', ''))
    category = str(notice.get('category', ''))
    source = str(notice.get('source', ''))
    region = str(notice.get('region', ''))
    
    # [1] 키워드 매칭 (가장 중요: 50점)
    if profile.industry:
        for keyword in profile.industry:
            if keyword in title or keyword in category:
                score += 50
                if keyword in title:
                    score += 10
                break 

    # [2] 지역 매칭 (20점)
    if "전국" in region or (profile.region and profile.region in region):
        score += 20
        
    # [3] 기관별 가중치 (다양성)
    if source != "K-Startup" and source != "창업진흥원":
        score += 5
        
    return score

# ==========================================
# 3. [핵심] 기관별 균형 배치 (쿼터제) 함수
# ==========================================
def balance_results(results):
    if not results: return []

    # 1. 기관별로 분류
    buckets = {}
    for item in results:
        src = item.get('source', '기타')
        if src not in buckets: buckets[src] = []
        buckets[src].append(item)
    
    # 2. 각 기관 내부 정렬 (점수순)
    for src in buckets:
        buckets[src].sort(key=lambda x: x.get('match_score', 0), reverse=True)
    
    balanced_list = []
    sources = list(buckets.keys())
    
    # 3. 라운드 로빈 (한 기관씩 돌아가며 뽑기)
    # 최대 10라운드까지 돌면서 상위권 섞기
    for _ in range(10): 
        for src in sources:
            if buckets[src]:
                balanced_list.append(buckets[src].pop(0))
    
    # 4. 남은 것들은 점수순으로 뒤에 붙이기
    remaining = []
    for src in sources:
        remaining.extend(buckets[src])
    remaining.sort(key=lambda x: x.get('match_score', 0), reverse=True)
    
    balanced_list.extend(remaining)
    
    return balanced_list

# ==========================================
# 4. API 엔드포인트
# ==========================================
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.post("/api/code-g/analyze")
async def run_analysis(profile: CompanyProfile = Body(...)):
    print(f"🔍 [Code-G] 분석 요청: {profile.industry} / 지역: {profile.region}")
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    # DB 조회
    try:
        cur.execute("SELECT * FROM notices ORDER BY id DESC")
        rows = cur.fetchall()
    except Exception as e:
        print(f"DB Error: {e}")
        return []
    finally:
        conn.close()
    
    all_notices = [dict(row) for row in rows]
    scored_results = []
    
    # 1. 점수 계산
    for notice in all_notices:
        score = calculate_score(notice, profile)
        notice['match_score'] = score
        
        # 검색어가 있으면 점수 있는 것만, 없으면 다 보여줌
        if profile.industry:
            if score > 0:
                scored_results.append(notice)
        else:
            scored_results.append(notice)
            
    # 2. 결과 섞기 (쿼터제)
    if not scored_results:
        return []
        
    final_results = balance_results(scored_results)
    
    return final_results[:100] # 상위 100개 반환

@app.post("/api/code-g/summarize")
async def summarize_notice(req: AnalyzeRequest):
    # analyzer가 비동기인지 동기인지에 따라 처리
    try:
        result = await analyze_content(req.url, req.title)
    except:
        result = analyze_content(req.url, req.title)
    return result

@app.post("/api/code-g/crawl")
def trigger_crawl():
    run_crawler()
    return {"status": "success", "message": "통합 크롤링 완료"}

@app.get("/")
def read_root():
    return {"status": "Code-G Intelligent Server Running"}