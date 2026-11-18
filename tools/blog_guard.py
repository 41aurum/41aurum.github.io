# 아우름41 가이드 블로그 자동 검수·밥줄 감시 (총괄 지휘부, 2026-11-18)
# 사용: python3 blog_guard.py  → 글마다 규칙 판정표(마크다운) 출력
import re, sys, urllib.request

BASE = "https://aurum41.tistory.com"

def get(u):
    try:
        return urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"}), timeout=20).read().decode("utf-8", "ignore")
    except Exception as e:
        return ""

def lang(t):
    return "EN" if "🇬🇧" in t else "JA" if "🇯🇵" in t else "KO"

AFF = r"link\.coupang|coupa\.ng|klook\.(?:com|to)|yeogi|goodchoice|agoda|trip\.com|booking\.com"
DISC = {"KO": r"쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다",
        "EN": r"commission|affiliate", "JA": r"アフィリエイト|手数料"}

rows = []
for i in range(1, 200):
    h = get(f"{BASE}/{i}")
    m = re.search(r"<title>([^<]*)", h)
    if not h or not m or m.group(1).strip() == "TISTORY":
        if i > 15 and not h:
            break
        continue
    t = m.group(1)
    L = lang(t)
    body = h
    aff = len(re.findall(AFF, body))
    disc = len(re.findall(DISC[L], body))
    coupang = len(re.findall(r"link\.coupang|coupa\.ng", body))
    checks = {
        "제휴링크": aff,
        "제휴표기(위·아래 2회↑)": "OK" if (aff == 0 or disc >= 2) else f"부족 {disc}",
        "쿠팡 문구 정확(KO)": ("OK" if (L != "KO" or coupang == 0 or re.search(DISC['KO'], body)) else "문구 불일치"),
        "언어 버튼": "OK" if re.search(r"English|日本語|한국어", body) else "없음",
        "3줄요약·방문기준일": "OK" if re.search(r"방문 기준일|Visited on|訪問日", body) else "없음",
        "이어지는 글": "OK" if re.search(r"이어지는 글|Next post|次の記事", body) else "없음",
        "이미지 alt 빈칸": len(re.findall(r'<img(?![^>]*alt="[^"]+")[^>]*>', body)),
        "'모텔' 표기": "위반" if "모텔" in body else "OK",
        "'추정' 표기": "위반" if "추정" in body else "OK",
        # 옛 'Summary in 🌏English/日本語/中文' 바: 스킨 lang()이 #pg-intl을 보고 만들어 넣음 → 꺼져 있어야 함.
        # 주의: 별관(/2·/8·/9)의 확정 버튼줄(🇰🇷 한국어 원문/🇬🇧 English/🇯🇵 日本語)도 class="pg-lang"을 쓰므로
        # 'pg-lang 개수'가 아니라 'Summary in 바 생성 코드·마크업'을 0개로 본다.
        "옛 Summary 바(pg-lang) 0개": ("OK" if (len(re.findall(r'class="pg-lang"[^>]*>\s*<span class="pg-lang-t">Summary in', body)) == 0
                                        and not re.search(r"function lang\(\)\{(?! return;)[^}]*?pg-lang", body)) else "부활"),
        "확정 언어버튼(🇬🇧/🇯🇵)": "OK" if (re.search(r"🇬🇧\s*English|English 판", body) and re.search(r"🇯🇵|日本語版|日本語", body)) else "없음",
        "올디콜라 재료 노출": ("확인 필요" if ("올디콜라" in body and re.search(r"재료|레시피|ingredient", body)) else "OK"),
    }
    rows.append((i, L, t[:40], checks))

keys = list(rows[0][3].keys()) if rows else []
print("| 글 | 언어 | 제목 | " + " | ".join(keys) + " |")
print("|" + "---|" * (3 + len(keys)))
bad = 0
for i, L, t, c in rows:
    vals = [str(c[k]) for k in keys]
    bad += sum(1 for v in vals if v not in ("OK",) and not v.isdigit())
    print(f"| {i} | {L} | {t} | " + " | ".join(vals) + " |")
print(f"\n글 {len(rows)}개 · 위반·누락 칸 {bad}개")
