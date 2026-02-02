"use client";

import React, { useState } from 'react';
import { Search, Building2, MapPin, Calendar, BarChart3, Globe, ArrowRight, Zap, CheckCircle2, Award } from 'lucide-react';

// --- 데이터 타입 정의 ---
interface AnalysisResult {
  source: string;
  title: string;
  category: string;
  region: string;
  start_date: string;
  end_date: string;
  agency: string;
  target: string;
  url: string;
  match_score?: number; // 매칭 점수 (백엔드에서 계산)
  ai_summary?: string; 
}

export default function Home() {
  // --- 사용자 입력 상태 (프로필) ---
  const [keywords, setKeywords] = useState('');     // 예: AI, 빅데이터
  const [region, setRegion] = useState('전국');     // 예: 서울
  const [foundedYear, setFoundedYear] = useState('2024'); // 예: 2024

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [results, setResults] = useState<AnalysisResult[]>([]);
  const [searchStatus, setSearchStatus] = useState<string>('');

  // 1. 맞춤형 공고 검색 함수
  const handleSearch = async () => {
    setIsAnalyzing(true);
    setSearchStatus('Code-G 엔진이 4개 부처(중기부, 과기부, 식약처, 조달청) 데이터를 분석 중입니다...');
    setResults([]);

    try {
      // 콤마로 구분된 키워드를 배열로 변환
      const keywordList = keywords.split(',').map(k => k.trim()).filter(k => k !== '');

      const response = await fetch('http://127.0.0.1:8000/api/code-g/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          industry: keywordList,
          region: region,
          foundedYear: parseInt(foundedYear) || 0
        }),
      });

      if (!response.ok) throw new Error("서버 응답 오류");

      const data = await response.json();
      
      if (data.length === 0) {
        setSearchStatus('조건에 맞는 공고가 없습니다. 키워드를 변경해보세요.');
      } else {
        setSearchStatus(`분석 완료! 귀사에 가장 적합한 공고 ${data.length}건을 찾았습니다.`);
        setResults(data);
      }

    } catch (error) {
      console.error(error);
      setSearchStatus('서버 연결 실패. (백엔드가 켜져있는지 확인하세요)');
    } finally {
      setIsAnalyzing(false);
    }
  };

  // 2. AI 상세 요약 함수
  const handleSummarize = async (item: AnalysisResult, index: number) => {
    const newResults = [...results];
    newResults[index].ai_summary = "🧠 AI가 공고문을 읽고 요약 중입니다...";
    setResults(newResults);

    try {
      const response = await fetch('http://127.0.0.1:8000/api/code-g/summarize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: item.url, title: item.title })
      });
      const data = await response.json();
      newResults[index].ai_summary = data.summary;
    } catch (e) {
      newResults[index].ai_summary = "요약 정보를 가져오지 못했습니다.";
    }
    setResults(newResults);
  };

  return (
    <main className="min-h-screen bg-slate-50">
      {/* 헤더 */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Zap className="w-6 h-6 text-blue-600" />
            <span className="text-xl font-bold text-slate-900">Code-G <span className="text-sm font-normal text-slate-500">Intelligent Platform</span></span>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        
        {/* --- 섹션 1: 기업 프로필 설정 (입력창) --- */}
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-8 mb-10">
          <h2 className="text-2xl font-bold text-slate-900 mb-6 flex items-center">
            <Building2 className="w-6 h-6 mr-2 text-blue-600"/> 
            우리 기업 프로필 설정
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {/* 1. 관심 키워드 */}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-slate-700 mb-2">관심 분야/업종 (콤마로 구분)</label>
              <input 
                type="text" 
                value={keywords}
                onChange={(e) => setKeywords(e.target.value)}
                placeholder="예: AI, 빅데이터, 헬스케어, 수출"
                // [수정됨] text-black 추가
                className="w-full p-3 text-black border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition-all placeholder:text-slate-400"
              />
            </div>

            {/* 2. 지역 선택 */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">소재지 (지역)</label>
              <select 
                value={region} 
                onChange={(e) => setRegion(e.target.value)}
                // [수정됨] text-black 추가
                className="w-full p-3 text-black border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none bg-white"
              >
                <option value="전국">전국 (전체)</option>
                <option value="서울">서울</option>
                <option value="경기">경기</option>
                <option value="인천">인천</option>
                <option value="대전">대전</option>
                <option value="부산">부산</option>
                <option value="대구">대구</option>
                <option value="광주">광주</option>
                <option value="강원">강원</option>
                {/* 필요시 더 추가 */}
              </select>
            </div>

            {/* 3. 설립연도 */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">설립 연도</label>
              <input 
                type="number" 
                value={foundedYear}
                onChange={(e) => setFoundedYear(e.target.value)}
                placeholder="YYYY"
                // [수정됨] text-black 추가
                className="w-full p-3 text-black border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none placeholder:text-slate-400"
              />
            </div>
          </div>

          <div className="mt-8 flex justify-end">
            <button
              onClick={handleSearch}
              disabled={isAnalyzing}
              className={`px-8 py-3 rounded-xl font-bold text-white text-lg transition-all flex items-center space-x-2 shadow-md
                ${isAnalyzing ? 'bg-slate-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700 hover:shadow-lg hover:-translate-y-1'}`}
            >
              {isAnalyzing ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>매칭 분석 중...</span>
                </>
              ) : (
                <>
                  <Search className="w-5 h-5" />
                  <span>맞춤 공고 찾기</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* --- 상태 메시지 --- */}
        {searchStatus && (
          <div className="mb-8 text-center p-4 bg-blue-50 text-blue-800 rounded-lg font-medium animate-fade-in">
            {searchStatus}
          </div>
        )}

        {/* --- 섹션 2: 분석 결과 리스트 --- */}
        <div className="space-y-6">
          {results.map((item, index) => (
            <div key={index} className={`relative bg-white rounded-xl p-6 shadow-sm border transition-all hover:shadow-md 
              ${(item.match_score || 0) >= 50 ? 'border-blue-200 ring-1 ring-blue-100' : 'border-slate-200'}`}>
              
              {/* 매칭 점수 뱃지 (점수가 있을 때만 표시) */}
              {(item.match_score || 0) > 0 && (
                <div className="absolute top-0 right-0 bg-blue-600 text-white px-4 py-1 rounded-bl-xl rounded-tr-xl font-bold text-sm flex items-center shadow-sm">
                  <Award className="w-4 h-4 mr-1 text-yellow-300" />
                  적합도 {item.match_score}점
                </div>
              )}

              <div className="flex flex-col md:flex-row md:items-start justify-between mb-4 mt-2">
                <div>
                  <div className="flex flex-wrap items-center gap-2 mb-2">
                    {/* 출처 뱃지 */}
                    <span className={`px-2 py-1 rounded text-xs font-bold 
                      ${item.source === '창업진흥원' || item.source === 'K-Startup' ? 'bg-green-100 text-green-700' : 
                        item.source === '조달청' || item.source === '나라장터' ? 'bg-indigo-100 text-indigo-700' : 
                        item.source === '과기정통부' ? 'bg-purple-100 text-purple-700' : 
                        item.source === 'NIPA' ? 'bg-red-100 text-red-700' : 
                        item.source === '중기부' ? 'bg-blue-100 text-blue-700' : 
                        item.source === '식약처' ? 'bg-teal-100 text-teal-700' :
                        'bg-gray-100 text-gray-700'}`}>
                      {item.source}
                    </span>
                    <span className="bg-slate-100 text-slate-600 px-2 py-1 rounded text-xs font-medium">
                      {item.category}
                    </span>
                    <span className="text-slate-500 text-sm flex items-center">
                      <MapPin className="w-3 h-3 mr-1" />
                      {item.region}
                    </span>
                  </div>
                  <h3 className="text-xl font-bold text-slate-900 mb-2 leading-tight hover:text-blue-600 transition-colors">
                    <a href={item.url} target="_blank" rel="noopener noreferrer">{item.title}</a>
                  </h3>
                  <div className="text-sm text-slate-500 space-y-1">
                    <p>🏢 주관: {item.agency} <span className="mx-2">|</span> 🎯 대상: {item.target}</p>
                    <p>📅 기간: {item.start_date} ~ {item.end_date}</p>
                  </div>
                </div>
              </div>

              {/* AI 요약 섹션 */}
              <div className="bg-slate-50 rounded-lg p-4 mb-4 border border-slate-100">
                <div className="flex items-start space-x-3">
                  <CheckCircle2 className={`w-5 h-5 mt-0.5 flex-shrink-0 ${item.ai_summary ? 'text-green-500' : 'text-slate-400'}`} />
                  <div className="flex-1">
                    <h4 className="font-semibold text-slate-900 text-sm mb-1">AI 핵심 요약</h4>
                    <p className="text-sm text-slate-600 leading-relaxed whitespace-pre-line">
                      {item.ai_summary ? item.ai_summary : "버튼을 누르면 공고 내용을 3줄로 요약해 드립니다."}
                    </p>
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between pt-4 border-t border-slate-100">
                <button 
                  onClick={() => handleSummarize(item, index)}
                  className="text-blue-600 text-sm font-medium hover:text-blue-800 flex items-center px-3 py-2 hover:bg-blue-50 rounded-lg transition-colors"
                >
                  <BarChart3 className="w-4 h-4 mr-1" />
                  AI 정밀 분석 실행
                </button>
                <a 
                  href={item.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="flex items-center space-x-1 text-slate-500 hover:text-slate-900 text-sm font-medium transition-colors"
                >
                  <span>원본 공고 이동</span>
                  <ArrowRight className="w-4 h-4" />
                </a>
              </div>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}