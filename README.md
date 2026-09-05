# 네이버 리뷰 답글 작성 도우미

네이버 스마트플레이스의 고객 리뷰를 읽어 AI 답글 초안을 만들고, 브라우저의 답글 입력란에 채워주는 반자동 업무 도구

운영자가 브라우저와 터미널에서 내용을 확인한 뒤 직접 등록 여부를 결정

2026.07.13~2026.07.15

## 설치

Python 3.10 이상

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env
```

## 설정

`.env`에서 키 값 설정

```env
OPENAI_API_KEY=your_api_key_here
BUSINESS_NAME=샘플 매장
NAVER_REVIEW_URL=https://new.smartplace.naver.com/your-review-management-page
BROWSER_PROFILE_DIR=./browser_profile
MAX_REPLIES=10
AUTO_REGISTER=false
```

`NAVER_REVIEW_URL`에는 본인이 관리 권한을 가진 스마트플레이스 리뷰 관리 페이지 주소만 사용하세요. 최초 실행 시 열린 브라우저에서 로그인이 필요할 수 있으며, 로그인 세션은 `browser_profile/`에 저장됩니다.

## 실행

```bash
python src/review_assistant.py
```

- `y`: 답글 등록
- Enter: 등록하지 않고 다음 리뷰로 이동
- `q`: 현재 실행 종료

`AUTO_REGISTER=true`로 설정하면 운영자별 검토 없이 답글이 등록

