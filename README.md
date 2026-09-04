# 네이버 리뷰 답글 작성 도우미

네이버 스마트플레이스의 고객 리뷰를 읽어 AI 답글 초안을 만들고, 브라우저의 답글 입력란에 채워주는 반자동 업무 도구입니다. 실제 소상공인 의뢰로 제작한 프로그램을 특정 업체와 고객을 식별할 수 없도록 일반화한 포트폴리오 버전입니다.

기본 설정에서는 답글을 자동 등록하지 않습니다. 운영자가 브라우저와 터미널에서 내용을 확인한 뒤 직접 등록 여부를 결정합니다.

## 주요 기능

- Playwright로 리뷰 목록을 불러오고 답글 작성 화면 제어
- OpenAI API로 리뷰 맥락에 맞는 답글 초안 생성
- 등록 전 운영자 검토 절차
- 처리한 리뷰와 답글 초안을 로컬 Excel 파일로 저장
- 업체명, 관리 URL, 모델과 말투를 환경변수로 설정
- 자동 등록 사용 시 추가 확인 문구 요구

## 설치

Python 3.10 이상을 권장합니다.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env
```

Windows PowerShell에서는 가상환경 활성화 명령으로 `.venv\Scripts\Activate.ps1`을 사용합니다.

## 설정

`.env`에서 다음 값을 실제 환경에 맞게 변경합니다.

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

프로그램이 답글 초안을 입력하면 터미널에서 다음 중 하나를 선택합니다.

- `y`: 답글 등록
- Enter: 등록하지 않고 다음 리뷰로 이동
- `q`: 현재 실행 종료

처리 결과는 기본적으로 `output/review_replies.xlsx`에 저장됩니다. 이 파일에는 고객이 작성한 내용이 포함될 수 있으므로 공개 저장소에 커밋하지 마세요.

## 자동 등록 주의사항

`AUTO_REGISTER=true`로 설정하면 운영자별 검토 없이 답글이 등록될 수 있습니다. 실행 시에도 `REGISTER`라는 확인 문구를 입력해야 동작하지만, 실제 운영에서는 `false` 사용을 권장합니다.

## 개인정보와 보안

- `.env`, `browser_profile/`, `output/`은 `.gitignore`에 포함되어 있습니다.
- API 키, 쿠키, 로그인 세션, 실제 고객 리뷰가 커밋되지 않았는지 푸시 전에 다시 확인하세요.
- 고객 리뷰에 포함된 이름, 연락처 등 개인정보를 별도로 수집하거나 공개하지 마세요.
- 예제 저장소에는 실제 업체명, 플레이스 식별자, 고객 리뷰와 답글을 포함하지 마세요.

## 한계와 운영 책임

네이버 화면 구조가 바뀌면 CSS 선택자를 수정해야 할 수 있습니다. 생성형 AI의 답변은 부정확하거나 부적절할 수 있으므로 등록 전에 반드시 사람이 검토해야 합니다. 본인이 관리 권한을 가진 계정에서만 사용하고, 자동화 대상 서비스의 최신 이용약관과 정책을 확인하세요.

## 공개 전 체크리스트

- [ ] `.env`가 Git 추적 대상이 아닌지 확인
- [ ] 브라우저 프로필과 쿠키가 포함되지 않았는지 확인
- [ ] 실제 업체 URL이나 식별자가 남아 있지 않은지 확인
- [ ] 실제 고객 리뷰와 결과 Excel 파일이 없는지 확인
- [ ] 의뢰인과 코드 공개 범위를 합의했는지 확인

## 라이선스

의뢰 작업에서 파생된 코드이므로 공개 라이선스는 포함하지 않았습니다. 재사용을 허용하려면 의뢰인과 공개 범위를 먼저 확인한 뒤 적절한 라이선스를 추가하세요.

