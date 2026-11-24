"""site/reviews/reviews.json -> 15 후기 위젯의 카드 목록을 다시 만듭니다.
제외 규칙: 본문에 이전 상호(갈풀)나 지역명이 나오는 후기는 넣지 않음. 닉네임 속 지역명은 허용. 닉네임은 앞쪽 절반만 보이게."""
import json, re, html, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
W = ROOT / "site/widgets/15_고객후기_슬라이드_주소입력.html"
BAN = ["갈풀", "인천", "송림", "제물포", "미추홀", "남동", "부평", "연수", "계양", "송도", "청라", "부천", "김포", "시흥", "고양", "일산"]
def mask(n):
    if "*" in n: return n
    k = max(1, len(n) // 2); return n[:k] + "*" * (len(n) - k)
data = json.loads((ROOT / "site/reviews/reviews.json").read_text(encoding="utf-8"))
keep = [r for r in data if not any(b in r["text"] for b in BAN)]
cards = []
for r in keep:
    y, m = r["date"].split("-")[:2]
    body = html.escape(r["text"].strip()).replace("\n", "<br>")
    cards.append(f'      <li class="cw-rv"><div class="cw-rv__top"><span class="cw-rv__star" aria-label="별점 5점">★★★★★</span><span class="cw-rv__date">{y}.{m}</span></div>\n'
                 f'        <p class="cw-rv__txt">{body}</p>\n'
                 f'        <p class="cw-rv__who">{html.escape(mask(r["nick"]))} 님</p></li>')
s = W.read_text(encoding="utf-8")
s = re.sub(r'(<ul class="cw-rvs"[^>]*>\n).*?(\n    </ul>)', lambda m: m.group(1) + "\n".join(cards) + m.group(2), s, flags=re.S)
W.write_text(s, encoding="utf-8")
print(f"{len(keep)}개 넣음 / {len(data)-len(keep)}개 제외")
