"""천운에어컨 사이트 자동 점검.

매일 GitHub Actions에서 실행됩니다. 문제가 하나라도 있으면 종료 코드 1로 끝나고,
워크플로가 깃허브 이슈를 만들어 저장소 주인에게 메일 알림이 갑니다.

점검 항목
1. 주요 페이지가 정상(200)으로 열리는지
2. 하단 사업자 주소를 뺀 본문에 지역명이 들어가 있지 않은지
3. 구글·네이버 소유확인 코드가 홈에 남아 있는지
4. 사이트맵에 우리 페이지만 있는지 (템플릿 상품 등 섞이지 않았는지)
5. 페이지가 불러오는 jsDelivr 이미지·영상이 살아 있는지
"""

import re
import sys
import urllib.request
from html.parser import HTMLParser

SITE = "https://cheonun.imweb.me"
PAGES = ["/", "/cleaning", "/install", "/mattress", "/about", "/contact"]
SITEMAP_EXPECTED = {"/home", "/cleaning", "/install", "/mattress", "/about", "/contact"}
VERIFY_METAS = ["google-site-verification", "naver-site-verification"]

# 사이트 본문에 나오면 안 되는 지역명 (하단 사업자 주소는 제외하고 검사)
REGIONS = [
    "서울", "경기", "인천", "부산", "대구", "대전", "광주광역", "울산", "세종",
    "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주",
    "김포", "일산", "고양", "시흥", "부천", "광명", "안산", "파주", "수원", "성남",
    "구래동", "송도", "청라", "검단", "계양", "부평", "연수구", "남동구", "미추홀",
    "강서구", "양천구",
]

UA = {"User-Agent": "Mozilla/5.0 (cheonun-site-check)"}


def fetch(url, method="GET"):
    req = urllib.request.Request(url, headers=UA, method=method)
    with urllib.request.urlopen(req, timeout=30) as r:
        body = r.read() if method == "GET" else b""
        return r.status, body.decode("utf-8", "replace")


class TextExtractor(HTMLParser):
    """script/style/하단(footer) 영역을 뺀 보이는 글자만 모읍니다."""

    def __init__(self):
        super().__init__()
        self.skip = 0
        self.footer_depth = 0
        self.depth = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        self.depth += 1
        a = dict(attrs)
        if tag in ("script", "style", "noscript"):
            self.skip += 1
        if self.footer_depth == 0 and (
            tag == "footer" or a.get("id") in ("doz_footer_wrap", "doz_footer")
        ):
            self.footer_depth = self.depth

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript") and self.skip:
            self.skip -= 1
        if self.footer_depth and self.depth == self.footer_depth:
            self.footer_depth = 0
        self.depth -= 1

    def handle_data(self, data):
        if not self.skip and not self.footer_depth:
            self.parts.append(data)


def visible_text(html):
    p = TextExtractor()
    p.feed(html)
    return " ".join(p.parts)


def main():
    problems = []
    assets = set()
    home_html = ""

    for path in PAGES:
        url = SITE + path
        try:
            status, html = fetch(url)
        except Exception as e:  # noqa: BLE001
            problems.append(f"페이지 접속 실패: {url} ({e})")
            continue
        if status != 200:
            problems.append(f"페이지 오류 {status}: {url}")
            continue
        if path == "/":
            home_html = html

        text = visible_text(html)
        found = sorted({r for r in REGIONS if r in text})
        if found:
            problems.append(f"지역명 발견 {url}: {', '.join(found)}")

        assets.update(re.findall(r"https://cdn\.jsdelivr\.net/gh/garpull0120/cheonun@[^\s\"')]+", html))

    for name in VERIFY_METAS:
        if name not in home_html:
            problems.append(f"홈에 소유확인 코드 없음: {name} (아임웹 SEO > Header Code 상단 확인)")

    try:
        _, sm = fetch(SITE + "/sitemap.xml")
        locs = {re.sub(r"^https?://[^/]+", "", u) for u in re.findall(r"<loc>([^<]+)</loc>", sm)}
        extra = sorted(locs - SITEMAP_EXPECTED)
        missing = sorted(SITEMAP_EXPECTED - locs)
        if extra:
            problems.append(f"사이트맵에 예상 밖 페이지: {', '.join(extra)}")
        if missing:
            problems.append(f"사이트맵에서 빠진 페이지: {', '.join(missing)}")
    except Exception as e:  # noqa: BLE001
        problems.append(f"사이트맵 확인 실패 ({e})")

    for url in sorted(assets):
        try:
            status, _ = fetch(url, method="HEAD")
            if status != 200:
                problems.append(f"이미지·영상 오류 {status}: {url}")
        except Exception as e:  # noqa: BLE001
            problems.append(f"이미지·영상 접속 실패: {url} ({e})")

    print(f"점검한 페이지 {len(PAGES)}개, 이미지·영상 {len(assets)}개")
    if problems:
        print("\n## 문제 발견\n")
        for p in problems:
            print(f"- {p}")
        sys.exit(1)
    print("문제 없음")


if __name__ == "__main__":
    main()
