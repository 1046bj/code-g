"use client";

import { useState } from "react";
import { Search, Loader2, Building2, Target, Calendar, Banknote, Check, Briefcase, Globe, Database, X, FileText, Lightbulb, AlertCircle } from "lucide-react";

// ... (기존 카테고리 상수들은 동일하게 유지 - 코드 길이상 생략하지 않고 전체 포함)
const INDUSTRY_CATEGORIES = [
  "인공지능(AI)", "빅데이터", "로봇/드론",
  "의료기기/Digital Health", "바이오/신약",
  "미래모빌리티", "친환경/에너지",
  "소부장(소재/부품/장비)", "시스템반도체", "사이버보안",
  "스마트팜/농테크", "블록체인/핀테크", "콘텐츠/미디어",
  "투자/액셀러레이터(AC/VC)", "경영/기술 컨설팅",
  "창업/초기기업(예비/초기)", "딥테크/초격차(DIPS)"
];

const TARGET_SITES_DISPLAY = [
  "기업마당", "K-Startup", "NIPA", "IITP", "한국연구재단", 
  "KHIDI", "SMTech", "IRIS", "나라장터", "KOCCA", "한국벤처투자"
];

const GOAL_CATEGORIES = [
  { id: "RD", label: "R&D 과제 수주", type: "스타트업" },
  { id: "BIZ", label: "사업화 자금 (예창/초창패)", type: "스타트업" },
  { id: "INV", label: "투자유치/IR 지원", type: "스타트업" },
  { id: "GLOBAL_S", label: "글로벌 진출 (수출바우처)", type: "스타트업" },
  { id: "VOUCHER", label: "바우처/인증/특허", type: "스타트업" },
  { id: "HR", label: "인력/고용 지원", type: "공통" },
  { id: "AC_OPS", label: "위탁운영/용역 수주 (AC전용)", type: "기관" },
  { id: "FUND", label: "모태펀드/조합 결성", type: "기관" },
  { id: "GLOBAL_OP", label: "글로벌 프로그램 운영", type: "기관" }
];

export default function Home() {
  const [profile, setProfile] = useState({
    industry: ["인공지능(AI)", "의료기기/Digital Health"],
    foundedYear: 2023,
    revenue: "10억 미만",
    goal: "R&D 과제 수주",
  });

  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any[]>([]);
  const [error, setError] = useState("");

  // --- [신규] 상세 분석 모달 상태 ---
  const [selectedNotice, setSelectedNotice] = useState<any>(null);
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [summaryData, setSummaryData] = useState<any>(null);

  const toggleIndustry = (category: string) => {
    setProfile(prev => {
      if (prev.industry.includes(category)) {
        return { ...prev, industry: prev.industry.filter(c => c !== category) };
      } else {
        return { ...prev, industry: [...prev.industry, category] };
      }
    });
  };

  const handleAnalyze = async () => {
    setLoading(true);
    setError("");
    setResults([]);
    try {
      if (profile.industry.length === 0) {
        alert("산업 분야를 최소 1개 이상 선택해주세요.");
        setLoading(false); return;
      }
      const res = await fetch(`https://code-g-backend.onrender.com/api/code-g/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(profile),
      });
      if (!res.ok) throw new Error(`서버 응답 오류: ${res.status}`);
      const data = await res.json();
      setResults(data);
    } catch (err) {
      console.error(err); setError("서버 연결 실패");
    } finally {
      setLoading(false);
    }
  };

  // --- [신규] 공고 클릭 시 상세 요약 요청 ---
  const handleNoticeClick = async (notice: any) => {
    setSelectedNotice(notice);
    setSummaryLoading(true);
    setSummaryData(null); // 이전 데이터 초기화

    try {
      const res = await fetch(`https://code-g-backend.onrender.com/api/code-g/summarize`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: notice.link, title: notice.title }),
      });
      
      if (!res.ok) throw new Error("분석 실패");
      const data = await res.json();
      setSummaryData(data);
    } catch (err) {
      console.error(err);
      setSummaryData({ summary: "상세 분석을 가져오는데 실패했습니다.", strategy: "직접 링크를 확인해주세요." });
    } finally {
      setSummaryLoading(false);
    }
  };

  const closeModal = () => {
    setSelectedNotice(null);
    setSummaryData(null);
  };

  return (
    <div className="min-h-screen bg-black text-green-500 font-mono p-4 md:p-8 relative">
      
      {/* 헤더 및 프로필 설정 섹션 (이전과 동일) */}
      <header className="mb-8 border-b border-green-800 pb-4 flex justify-between items-end">
        <div>
          <h1 className="text-4xl font-bold tracking-tighter text-white">Code-G</h1>
          <p className="text-sm text-green-600">Gov.Funding AI Matcher</p>
        </div>
        <div className="text-right">
          <span className="text-xs text-gray-500 block">System Active</span>
        </div>
      </header>

      <main className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8">
        <div className="lg:col-span-4 space-y-6">
          <div className="bg-gray-900/80 border border-green-800 p-6 rounded-lg sticky top-4">
            <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2"><Building2 size={20} /> 프로필 설정</h2>
            {/* ... (프로필 입력 UI 생략 없이 그대로 유지) ... */}
            {/* 코드 길이상 요약: 산업분야, 설립연도, 목적 선택 UI가 여기 들어감 */}
            <div className="space-y-8">
              <div>
                <label className="block text-xs text-green-700 mb-2 font-bold flex items-center gap-2"><Briefcase size={12}/> 관심 분야</label>
                <div className="flex flex-wrap gap-2">
                  {INDUSTRY_CATEGORIES.map((cat) => (
                    <button key={cat} onClick={() => toggleIndustry(cat)} className={`text-[11px] px-3 py-2 rounded-md border transition-all flex items-center gap-1 ${profile.industry.includes(cat) ? "bg-green-900 text-white border-green-500 font-bold" : "bg-black text-gray-500 border-gray-800 hover:border-gray-600"}`}>
                      {profile.industry.includes(cat) && <Check size={10} />} {cat}
                    </button>
                  ))}
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                   <label className="block text-xs text-green-700 mb-1">설립 연도</label>
                   <input type="number" className="w-full bg-black border border-green-900 rounded p-2 text-white text-center" value={profile.foundedYear} onChange={(e) => setProfile({...profile, foundedYear: parseInt(e.target.value)})}/>
                </div>
                <div>
                   <label className="block text-xs text-green-700 mb-1">매출 규모</label>
                   <select className="w-full bg-black border border-green-900 rounded p-2 text-white" value={profile.revenue} onChange={(e) => setProfile({...profile, revenue: e.target.value})}>
                     <option>매출 없음</option><option>10억 미만</option><option>10억 이상</option>
                   </select>
                </div>
              </div>
              <div>
                <label className="block text-xs text-green-700 mb-2">검색 목적</label>
                <div className="grid grid-cols-2 gap-2">
                  {GOAL_CATEGORIES.slice(0, 6).map((opt) => (
                    <label key={opt.id} className={`flex items-center gap-2 text-[11px] p-2 rounded border cursor-pointer ${profile.goal === opt.label ? "border-green-600 bg-green-900/30 text-white" : "border-gray-800 text-gray-500"}`}>
                      <input type="radio" name="goal" className="hidden" checked={profile.goal === opt.label} onChange={() => setProfile({...profile, goal: opt.label})}/>
                      {profile.goal === opt.label && <Check size={10} />} {opt.label}
                    </label>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="lg:col-span-8 space-y-6">
          <button onClick={handleAnalyze} disabled={loading} className="w-full bg-green-700 hover:bg-green-600 text-black font-black text-lg py-5 rounded-lg flex justify-center items-center gap-3 transition-all">
            {loading ? <Loader2 className="animate-spin" /> : <Database />} {loading ? "크롤링 중..." : "Code-G 통합 검색 엔진 가동"}
          </button>

          <div className="space-y-4 mt-8">
            {results.map((item, idx) => (
              <div key={idx} onClick={() => handleNoticeClick(item)} className="group relative border border-green-900/60 bg-gray-900/40 p-6 rounded-lg hover:border-green-500 hover:bg-gray-900/90 transition-all cursor-pointer overflow-hidden">
                
                {/* 상단: 기관명 + D-Day 뱃지 */}
                <div className="flex justify-between items-start mb-3">
                  <div className="flex gap-2 items-center">
                    <span className="bg-green-950 text-green-400 text-[10px] px-2 py-1 rounded border border-green-900 font-bold tracking-wide">
                      {item.agency}
                    </span>
                    {/* D-Day 뱃지 (임박하면 빨간색) */}
                    <span className={`text-[10px] px-2 py-1 rounded font-bold border ${
                      item.d_day.includes("D-5") || item.d_day.includes("D-4") || item.d_day.includes("D-3") || item.d_day.includes("D-2") || item.d_day.includes("D-1") 
                      ? "bg-red-900/50 text-red-400 border-red-800 animate-pulse" 
                      : "bg-blue-900/30 text-blue-400 border-blue-800"
                    }`}>
                      ⏳ {item.d_day}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-500">AI 적합도</span>
                    <span className={`text-xl font-black italic ${item.match_score >= 80 ? 'text-green-400' : 'text-yellow-500'}`}>
                      {item.match_score}
                    </span>
                  </div>
                </div>
                
                <h3 className="text-xl font-bold text-white mb-3 group-hover:text-green-400 transition-colors">
                  {item.title}
                </h3>

                {/* --- [신규] 날짜 정보 표시 줄 --- */}
                <div className="flex items-center gap-4 text-xs text-gray-400 mb-4 bg-black/20 p-2 rounded border border-gray-800">
                  <div className="flex items-center gap-1">
                    <Calendar size={12} className="text-gray-500"/>
                    <span>공고일: {item.date}</span>
                  </div>
                  <div className="w-[1px] h-3 bg-gray-700"></div>
                  <div className="flex items-center gap-1 text-gray-300">
                    <AlertCircle size={12} className="text-green-600"/>
                    <span>마감일: <span className="text-green-400 font-bold">{item.deadline}</span></span>
                  </div>
                </div>
                
                <p className="text-gray-400 text-sm mb-2 leading-relaxed line-clamp-2">
                  {item.summary}
                </p>
                
                <div className="flex justify-end text-xs text-green-600 group-hover:underline">상세 분석 보기 →</div>
              </div>
            ))}
          </div>
        </div>
      </main>

      {/* --- [신규] 상세 분석 모달 --- */}
      {selectedNotice && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4" onClick={closeModal}>
          <div className="bg-gray-900 border border-green-600 w-full max-w-3xl max-h-[90vh] overflow-y-auto rounded-lg shadow-2xl shadow-green-900/50" onClick={(e) => e.stopPropagation()}>
            
            {/* 모달 헤더 */}
            <div className="sticky top-0 bg-gray-900 border-b border-green-800 p-6 flex justify-between items-start z-10">
              <div>
                <span className="bg-green-900 text-green-300 text-xs px-2 py-1 rounded mb-2 inline-block">{selectedNotice.agency}</span>
                <h2 className="text-2xl font-bold text-white leading-tight">{selectedNotice.title}</h2>
              </div>
              <button onClick={closeModal} className="text-gray-500 hover:text-white"><X size={24}/></button>
            </div>

            {/* 모달 내용 */}
            <div className="p-8 space-y-8">
              {summaryLoading ? (
                <div className="flex flex-col items-center justify-center py-20 text-green-500">
                  <Loader2 className="w-12 h-12 animate-spin mb-4" />
                  <p className="text-lg animate-pulse">Code-G AI가 공고문을 분석하고 있습니다...</p>
                  <p className="text-sm text-gray-500 mt-2">핵심 요건, 지원 금액, 전략 추출 중</p>
                </div>
              ) : summaryData ? (
                <>
                  {/* 핵심 요약 카드 */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="bg-black/40 p-4 rounded border border-green-900/50">
                      <h3 className="text-green-400 text-sm font-bold flex items-center gap-2 mb-2"><Target size={16}/> 지원 대상 (Eligibility)</h3>
                      <p className="text-gray-300 text-sm leading-relaxed">{summaryData.eligibility || "상세 공고문 확인 필요"}</p>
                    </div>
                    <div className="bg-black/40 p-4 rounded border border-green-900/50">
                      <h3 className="text-green-400 text-sm font-bold flex items-center gap-2 mb-2"><Banknote size={16}/> 지원 혜택 (Funding)</h3>
                      <p className="text-gray-300 text-sm leading-relaxed">{summaryData.funding || "상세 공고문 확인 필요"}</p>
                    </div>
                  </div>

                  {/* AI 요약 내용 */}
                  <div>
                    <h3 className="text-white text-lg font-bold flex items-center gap-2 mb-3"><FileText size={20}/> 사업 개요</h3>
                    <p className="text-gray-300 leading-relaxed bg-gray-800/30 p-4 rounded border-l-4 border-green-600">
                      {summaryData.summary}
                    </p>
                  </div>

                  {/* 전략 포인트 */}
                  <div>
                    <h3 className="text-white text-lg font-bold flex items-center gap-2 mb-3"><Lightbulb size={20} className="text-yellow-400"/> Code-G 전략 팁</h3>
                    <div className="bg-green-900/10 border border-green-800 p-4 rounded text-gray-300">
                      <p className="flex gap-3">
                        <span className="text-2xl">💡</span>
                        <span>{summaryData.strategy}</span>
                      </p>
                    </div>
                  </div>

                  {/* 하단 링크 */}
                  <div className="border-t border-gray-800 pt-6 flex justify-end">
                    <a href={selectedNotice.link} target="_blank" rel="noopener noreferrer" className="bg-green-700 hover:bg-green-600 text-black font-bold py-3 px-6 rounded flex items-center gap-2">
                      <Globe size={18}/> 공고문 원문 페이지로 이동
                    </a>
                  </div>
                </>
              ) : (
                <div className="text-center text-red-400 py-10">
                  <AlertCircle className="mx-auto mb-2"/>
                  데이터를 불러오지 못했습니다.
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}