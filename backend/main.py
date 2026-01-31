from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from crawler import get_notices
from analyzer import analyze_content  # <--- [중요] 방금 만든 파일 연결

app = FastAPI()

# --- 보안 설정 ---
origins = ["http://localhost:3000", "http://127.0.0.1:3000", "*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 데이터 모델 ---
class CompanyProfile(BaseModel):
    industry: List[str]
    foundedYear: int
    revenue: str
    goal: str

class AnalyzeRequest(BaseModel):
    url: str
    title: str

# --- 1. 검색 API ---
@app.post("/api/code-g/analyze")
async def run_analysis(profile: CompanyProfile = Body(...)):
    print(f"🔍 [Code-G] 검색 요청: {profile.industry}")
    notices = await get_notices(profile)
    return notices

# --- 2. 상세 요약 API (신규 기능) ---
@app.post("/api/code-g/summarize")
async def summarize_notice(req: AnalyzeRequest):
    print(f"🧠 [Code-G] 요약 요청: {req.title}")
    result = await analyze_content(req.url, req.title)
    return result

@app.get("/")
def read_root():
    return {"status": "Code-G Server is Running!"}