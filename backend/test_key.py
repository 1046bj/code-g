import requests
import urllib.parse

# ========================================================
# 1. 여기에 [==]로 끝나는 진짜 Decoding 키를 넣어주세요!
# ========================================================
REAL_KEY = "d89c618d3ff720dfaa7da509d296a9c8d32f2ec90592ffa1e3c0a73f32dce7f4" 

# 올바른 주소 (중소벤처기업부 - 선생님이 알려주신 End Point)
URL = "https://apis.data.go.kr/1421000/mssBizService_v2/getMssBizList"

def check_key():
    print(f"🔑 키 확인 중: {REAL_KEY[:10]}... (뒤 생략)")
    print(f"📡 요청 주소: {URL}")

    # 파라미터 조합
    params = {
        "serviceKey": REAL_KEY, # requests가 알아서 인코딩해줍니다 (Decoding키 권장)
        "pageNo": "1",
        "numOfRows": "10",
        "returnType": "json",
        "yr": "2026"  # 중기부 API는 연도(yr) 파라미터가 필수입니다!
    }

    try:
        res = requests.get(URL, params=params, timeout=10)
        print(f"📊 응답 코드: {res.status_code}")
        
        if res.status_code == 200:
            print("✅ [성공!] 데이터가 정상적으로 왔습니다.")
            print(f"내용 미리보기: {res.text[:200]}")
            return True
        else:
            print("❌ [실패] 오류 메시지를 확인하세요.")
            print(f"내용: {res.text}")
            return False
            
    except Exception as e:
        print(f"💥 에러 발생: {e}")
        return False

if __name__ == "__main__":
    if "d89c" in REAL_KEY:
        print("⚠️ 경고: 아직도 'd89c...' 키를 사용 중이십니다.")
        print("   공공데이터포털에서 [Decoding] 키(특수문자 포함)를 다시 찾아주세요!")
    else:
        check_key()