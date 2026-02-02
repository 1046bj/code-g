import requests
from urllib.parse import unquote

# ==========================================
# 1. 선생님의 인증키 설정
# ==========================================
# 방금 주신 키를 그대로 넣었습니다.
API_KEY_RAW = "d89c618d3ff720dfaa7da509d296a9c8d32f2ec90592ffa1e3c0a73f32dce7f4"

# 코드 내부에서 알아서 변환하므로 신경 쓰지 않으셔도 됩니다.
API_KEY_DECODED = unquote(API_KEY_RAW)

def test_connection(agency_name, url, params, headers=None, description=""):
    print(f"👉 [{agency_name}] {description} 시도...")
    print(f"   URL: {url}")
    
    try:
        # 10초 타임아웃 설정
        res = requests.get(url, params=params, headers=headers, timeout=10)
        
        # 상태 코드 확인
        print(f"   [상태코드] {res.status_code}")
        
        # 응답 내용 (핵심!)
        content = res.text[:300].replace('\n', ' ') # 너무 길면 자름
        print(f"   [응답내용] {content}")
        
        # 진단 로직
        if "SERVICE_KEY_IS_NOT_REGISTERED" in content or "SERVICE KEY IS NOT REGISTERED" in content:
            print("   🚨 결과: [인증키 미등록] - 포털에서 활용신청이 아직 승인 안 됐거나, 다른 API를 신청하신 것 같습니다.")
        elif "Invalid Service Key" in content:
             print("   🚨 결과: [인증키 형식 오류] - 서버가 이 키 형식을 싫어합니다.")
        elif "LIMITED_NUMBER_OF_SERVICE_REQUESTS" in content:
            print("   ⚠️ 결과: [트래픽 초과] - 일일 사용량을 다 쓰셨습니다.")
        elif "<item>" in content or '"data":' in content or '"currentCount":' in content:
            print("   ✅ 결과: [성공!] - 이 주소와 설정이 정답입니다.")
        else:
            print("   ❓ 결과: 알 수 없는 응답 (위 내용을 복사해 주세요)")
            
    except Exception as e:
        print(f"   ❌ 시스템 에러: {e}")
    
    print("-" * 50)

# ==========================================
# 2. 진단 시작
# ==========================================
print("\n🚀 [Code-G] 인증키 정밀 진단 시작\n")

# [1] NIPA (정보통신산업진흥원) - 가장 유력한 3가지 방법 테스트
# 전략 A: 선생님이 주신 가이드 (Header 인증)
test_connection("NIPA", 
                "https://api.odcloud.kr/api/15077093/v1/file-data-list", 
                {"page": 1, "perPage": 10, "returnType": "JSON"},
                headers={"Authorization": f"Infuser {API_KEY_RAW}"},
                description="방식1: Header + Raw Key")

# 전략 B: Query 파라미터 (Decoding Key)
test_connection("NIPA", 
                "https://api.odcloud.kr/api/15077093/v1/file-data-list", 
                {"serviceKey": API_KEY_DECODED, "page": 1, "perPage": 10, "returnType": "JSON"},
                description="방식2: Query + Decoded Key")

# [2] 중기부 (중소벤처기업부) - 버전별 테스트
# 전략 A: V2 통합공고 (최신 표준)
test_connection("중기부", 
                "https://apis.data.go.kr/1421000/mssBizService_v2/getSmbizPblancList", 
                {"serviceKey": API_KEY_DECODED, "numOfRows": 10, "pageNo": 1},
                description="방식1: V2 API (통합공고)")

# 전략 B: 기업마당 (구버전)
test_connection("중기부", 
                "http://apis.data.go.kr/1352000/ODMS_PROJECT/callOpenApiInfo", 
                {"serviceKey": API_KEY_DECODED, "numOfRows": 10, "pageNo": 1, "apiType": "XML"},
                description="방식2: 기업마당 API")

# 전략 C: V2 일반공고
test_connection("중기부", 
                "https://apis.data.go.kr/1421000/mssBizService_v2/getPblancList", 
                {"serviceKey": API_KEY_DECODED, "numOfRows": 10, "pageNo": 1},
                description="방식3: V2 API (일반공고)")