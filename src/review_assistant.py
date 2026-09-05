"""실제 매장용 리뷰 답글 자동화 코드를 익명화한 포트폴리오 버전."""

from playwright.sync_api import sync_playwright
from openai import OpenAI
from dotenv import load_dotenv
import pandas as pd
import os

load_dotenv()

# ===========================
# CONFIG
# ===========================
MAX_REPLY = int(os.getenv("MAX_REPLIES", "100"))
AUTO_REGISTER = os.getenv("AUTO_REGISTER", "false").lower() == "true"
REVIEW_URL = os.environ["NAVER_REVIEW_URL"]
PROFILE_DIR = os.getenv("BROWSER_PROFILE_DIR", "./browser_profile")
BUSINESS_NAME = os.getenv("BUSINESS_NAME", "샘플 키즈카페")
MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
OUTPUT_FILE = os.getenv("OUTPUT_FILE", "./output/review_replies.xlsx")

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def clean_review_text(text: str) -> str:
    """네이버 리뷰 텍스트에서 불필요한 문구 제거"""
    return text.replace("더보기", "").replace("접기", "").strip()


def generate_reply(review: str) -> str:
    """GPT로 리뷰 답글 생성"""
    prompt = f"""
너는 {BUSINESS_NAME}를 실제 운영하는 점장이다.

항상 부모님에게 친절하고 따뜻한 말투를 사용한다.

- 답글은 5~7문장 정도로 충분히 정성스럽게 작성한다.

- 짧게 끝내지 말고, 리뷰 내용에 대한 공감과 감사가 충분히 느껴지게 작성한다.

- 이모지는 2~5개 정도 자연스럽게 사용한다.

- 문장마다 줄바꿈을 적절히 넣어 읽기 편하게 작성한다.
리뷰:
{review}

답글만 출력해라.

### 예시
리뷰
테마가 다양해서 아이가 재미있어 합니다
날이 추운데 실내에서 부모들도 편히 쉴 수 있어 좋았어요.
아이가 선생님과 함께 체험하니 좋아하네요~

답글
안녕하세요! {BUSINESS_NAME}입니다~
다양한 테마를 아이가 즐겁게 체험했다니 저희도 정말 기쁘네요 ☺️
추운 날씨에도 아이와 부모님 모두 편안한 시간을 보내셨다니 다행입니다.
앞으로도 재미있는 체험을 준비하고 안전하고 즐거운 공간을 만들겠습니다 🥰💕
소중한 리뷰 감사드리며 다음에 또 뵙겠습니다!

===========================
### 예시
리뷰
처음 방문했는데 테마가 재미있고 아이도 신나게 놀았어요!
체험을 마치고 받은 작은 선물도 좋아했고 간식과 음료도 맛있었습니다.

답글
안녕하세요~ {BUSINESS_NAME}입니다!
첫 방문이 만족스러우셨다니 정말 감사합니다 🥰
아이가 테마와 체험을 신나게 즐겼다니 저희도 무척 기쁘네요.
간식과 음료까지 맛있게 드셨다니 더욱 뿌듯합니다 ☺️
앞으로도 아이들이 재미있고 안전하게 놀 수 있는 공간이 되도록 노력하겠습니다.
소중한 리뷰 감사드리며 다음 방문도 기다리고 있겠습니다 💕
"""

    res = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=0.8,
        messages=[
            {
                "role": "system",
                "content": f"너는 {BUSINESS_NAME}를 실제 운영하는 점장이다. "
                "부모님께 친근하고 따뜻하게 말하며, 사람이 직접 쓴 것처럼 자연스럽게 답글을 작성한다.",
            },
            {"role": "user", "content": prompt},
        ],
    )
    return res.choices[0].message.content.strip()


def scroll_all_reviews(page) -> None:
    """리뷰 목록을 끝까지 스크롤해서 로딩"""
    prev = 0
    stable = 0

    while True:
        page.mouse.wheel(0, 3000)
        page.wait_for_timeout(1000)
        now = page.locator("li[class*='Review_pui_review']").count()
        print(f"Loaded : {now}")

        if now == prev:
            stable += 1
        else:
            stable = 0
        if stable >= 3:
            break
        prev = now


def save_rows_to_excel(rows, filename: str = OUTPUT_FILE) -> None:
    """수집한 리뷰와 GPT 답글을 엑셀로 저장"""
    if rows:
        output_dir = os.path.dirname(filename)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        pd.DataFrame(rows).to_excel(filename, index=False)
        print(f"\nExcel 저장 완료 : {filename}")
    else:
        print("\n저장할 리뷰 데이터가 없습니다.")


def main() -> None:
    rows = []

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=False,
        )
        page = browser.new_page()
        page.goto(REVIEW_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(5000)

        print("Loading reviews...")
        scroll_all_reviews(page)
        reply_buttons = page.locator('button[data-area-code="rv.replywrite"]')
        total = min(reply_buttons.count(), MAX_REPLY)

        print(f"\n답글 작성 가능 리뷰 수 : {reply_buttons.count()}")
        print(f"이번 실행에서 처리할 리뷰 수 : {total}\n")

        for idx in range(total):
            print(f"\n[{idx + 1}/{total}] 리뷰 처리 시작")
            btn = reply_buttons.nth(idx)
            card = btn.locator("xpath=ancestor::li[1]")

            try:
                review = clean_review_text(
                    card.locator('a[data-pui-click-code="text"]').first.inner_text()
                )
            except Exception as e:
                print(f"리뷰 텍스트를 가져오지 못했습니다. 건너뜁니다. 오류: {e}")
                continue

            author = ""
            try:
                author = card.locator("strong").first.inner_text()
            except Exception:
                pass

            date = ""
            try:
                date = card.locator("text=작성일").locator("xpath=..").inner_text()
            except Exception:
                pass

            print("=" * 80)
            print("고객 리뷰\n")
            print(review)

            try:
                reply = generate_reply(review)
            except Exception as e:
                print(f"GPT 답글 생성 실패. 건너뜁니다. 오류: {e}")
                continue

            print("\n" + "=" * 80)
            print("GPT 답글\n")
            print(reply)
            print("=" * 80)
            rows.append({
                "작성자": author,
                "작성일": date,
                "고객 리뷰": review,
                "GPT 답글": reply,
            })

            try:
                btn.click()
                page.wait_for_timeout(800)
                page.locator("#replyWrite").fill(reply)
                page.wait_for_timeout(500)
                print("\n브라우저에 답글이 입력되었습니다.")
            except Exception as e:
                print(f"답글 입력 실패. 건너뜁니다. 오류: {e}")
                continue

            if AUTO_REGISTER:
                try:
                    page.locator('button[data-area-code="rv.replydone"]').click()
                    page.wait_for_timeout(1500)
                    print("등록 완료!")
                except Exception as e:
                    print(f"자동 등록 실패. 오류: {e}")
                continue

            while True:
                ans = input("\n등록하시겠습니까? (y/N/q) : ").strip().lower()
                if ans == "y":
                    try:
                        page.locator('button[data-area-code="rv.replydone"]').click()
                        page.wait_for_timeout(1500)
                        print("등록 완료!")
                    except Exception as e:
                        print(f"등록 실패. 오류: {e}")
                    break
                elif ans in ("", "n"):
                    print("등록하지 않고 다음 리뷰로 넘어갑니다.")
                    try:
                        page.locator('button[data-area-code="rv.replyclose"]').click()
                        page.wait_for_timeout(500)
                    except Exception:
                        pass
                    break
                elif ans == "q":
                    print("프로그램을 종료합니다.")
                    save_rows_to_excel(rows)
                    browser.close()
                    return
                else:
                    print("y / n / q 중 하나를 입력해주세요.")

        save_rows_to_excel(rows)
        input("\nEnter를 누르면 종료합니다.")
        browser.close()


if __name__ == "__main__":
    main()
