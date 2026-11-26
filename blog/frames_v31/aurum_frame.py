#!/usr/bin/env python3
"""아우름 디지털 액자 v3.1(이케아식 깨끗한 흰 이너 — 종이 결 없음) / v3(종이 속지, 폐기) / v2 — 실제 나무 표면 사진(Poly Haven CC0 베니어 질감)으로 짠 액자.

사용:
  python3 aurum_frame.py 작품.jpg --mat paper --media drawing|oil|photo   # v3: v3.1: drawing=검정+흰 이너 9%, oil·photo=오크(보울러 톤)+흰 이너 7.6% (모바일 5%)
  python3 aurum_frame.py 작품.jpg --style brown_walnut|brown_oak|black|white --inner on|off [--mat on|off]
         [--bg F7F3EC] [--out 결과.jpg] [--json aurum_frames.json] [--nine 9분할.png]

원칙(대표님 철칙 반영)
- 재질은 그라데이션으로 흉내 내지 않는다: 나무결은 전부 실제 베니어 사진 픽셀. 명암은 '모양(단면)'에서 오는 빛만 쓴다.
- 광택·유리 번쩍임 없음. 빛은 왼쪽 위 하나로 통일(벽 그림자는 오른쪽 아래).
- 네 변은 결이 변을 따라간다(위·아래 가로결, 좌우 세로결), 모서리는 45도 마이터 이음.
- 작품 픽셀은 한 점도 바꾸지 않는다(리사이즈·보정·그림자 덮기 없음) — 실행 끝에 자동 대조.
- 테 두께는 작품 '가로폭' 비례 → 블로그 본문 폭에 꽉 차게 보일 때 어떤 세로/가로 비율이든 화면상 두께가 같다.
"""
import argparse, json, os, sys, datetime
import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
TEX = os.environ.get('AURUM_TEX', os.path.join(HERE, 'tex'))

# 실측 근거: 이케아 RÖDALM 30×40(바깥 32cm, 앞면 1cm), 대표님 Hammer(RÖDALM 3칸) 사진 실측 앞면 2.2cm=바깥폭 3.8%,
# KNOPPÄNG 50×70 바깥 52×72 깊이 2cm(앞면 1cm), LOMVIKEN 50×70 바깥 51.5×71.5(앞면 0.75cm, 알루미늄)
STYLES = {
    # tex: 질감 파일, tone: 목표 평균색, gain: 결 대비 배율, face: 앞면 폭(작품 가로폭 비), x0: 질감에서 떠 올 위치
    'brown_walnut': dict(tex='walnut_veneer', tone=(96, 66, 47), gain=1.25, face=0.042, lip=0.013, lipdark=0.80),
    'brown_oak':    dict(tex='oak_veneer_01', tone=(170, 132, 92), gain=1.00, face=0.042, lip=0.013, lipdark=0.86),
    # v3 시험 톤(18:10 지시 → 18:18 판정으로 오크 확정, 기본값에서 뺌 — 비교 기록용으로만 남김). 결은 월넛 실사(진한 줄무늬가 '나무'로 읽힘), 평균색만 오크 쪽으로.
    'light_brown':  dict(tex='walnut_veneer', tone=(136, 99, 68), gain=1.10, face=0.040, lip=0.012, lipdark=0.82),
    'black':        dict(tex='black_oak_veneer', tone=(30, 28, 27), gain=0.26, face=0.036, lip=0.012, lipdark=0.80),
    'white':        dict(tex='black_walnut_veneer_01', tone=(236, 234, 229), gain=0.16, face=0.036, lip=0.012, lipdark=0.955),
}
SS = 3  # 테 렌더 초과표본(v2.1: 2→3, 이음선 계단 방지). 작품은 1배 그대로 붙임.


def load_tex(name):
    """같은 질감의 다른 구역 캡처(_vgrain, _vgrain_2 …)를 모두 불러 목록으로."""
    out = []
    for suf in ['', '_2', '_3']:
        p = os.path.join(TEX, name + '_vgrain' + suf + '.png')
        if os.path.exists(p):
            out.append(np.asarray(Image.open(p).convert('RGB')).astype(np.float32))
    return out


def grade_all(ts, tone, gain):
    return [grade(t, tone, gain) for t in ts]


def grade(t, tone, gain):
    """실제 질감의 '결 변화'는 살리고 평균색만 목표 톤으로 옮김(색 밀어넣기, 그라데이션 아님)."""
    m = t.reshape(-1, 3).mean(0)
    lum = t.mean(2, keepdims=True); lm = lum.mean()
    # 결(밝기 변화)은 gain 배, 원래 색 차이(나뭇결 속 색 얼룩)는 절반만 유지
    out = np.array(tone, np.float32) + (lum - lm) * gain + (t - lum - (m - lm)) * 0.5 * min(1, gain)
    return np.clip(out, 0, 255)


def strip(pool, width, length, x0, rng):
    """결 방향(세로)으로 length, 가로 width 띠를 떠 옴. 한 장으로 모자라면 다른 캡처·다른 열의 결을 250px 교차로 이음
    (실제 몰딩도 긴 판재를 이어 쓰므로 결이 바뀌는 지점이 있음)."""
    tex = pool[0]
    H, W = tex.shape[:2]
    x0 = int(x0) % max(1, W - width)
    out = tex[:, x0:x0 + width].copy()
    i = 0
    while out.shape[0] < length:
        i += 1
        t2 = pool[i % len(pool)]
        x1 = int(rng.integers(0, max(1, t2.shape[1] - width)))
        nxt = t2[:, x1:x1 + width]
        ov = min(250, nxt.shape[0] // 3)
        a = np.linspace(0, 1, ov)[:, None, None]
        blend = out[-ov:] * (1 - a) + nxt[:ov] * a
        out = np.concatenate([out[:-ov], blend, nxt[ov:]], 0)
    return out[:length]


def profile_shade(t):
    """앞면 단면(0=바깥 모서리, 1=안쪽 모서리)에 따른 빛 계수. 빛을 '향한' 면 +, 등진 면 −.
    반환: (바깥 둥근모 기여, 안쪽 경사면 기여) — 변 방향에 따라 부호를 정함."""
    outer = np.clip(1 - t / 0.10, 0, 1) ** 1.5        # 바깥 둥근모(폭 10%)
    inner = np.clip((t - 0.80) / 0.20, 0, 1)            # 안쪽 경사(폭 20%)
    return outer, inner


def render(art, style='brown_walnut', inner=True, mat=False, bg=(247, 243, 236), seed=7, margin=None, transparent=False, unit=None, rim=None, rim_long=False, face_px=None):
    st = STYLES[style]
    rng = np.random.default_rng(seed)
    aw, ah = art.size
    U = unit or aw                                         # 두께 기준(기본: 작품 가로폭)
    matw = round(U * 0.085) if mat else 0
    if rim:   # v2.1: 나무 테(앞면+이너) = 액자 바깥 가로폭 × rim (실물 이케아 깊은 액자 실측 3.8%)
        base = max(aw, ah) if rim_long else aw   # rim_long: 긴 변 기준(이케아 3.8% 실측이 55cm 긴 변 기준)
        wood = round(rim * (base + 2 * matw) / (1 - 2 * rim))
        face = round(wood * 0.76) if inner else wood
        lip = wood - face if inner else 0
    elif face_px:
        face = face_px; lip = 0
    else:
        face = max(14, round(U * st['face']))
        lip = max(5, round(U * st['lip'])) if inner else 0
    T = face + lip + matw                                   # 작품 가장자리까지 총 두께
    FW, FH = aw + 2 * T, ah + 2 * T
    M = margin if margin is not None else max(24, round(U * 0.05))
    CW, CH = FW + 2 * M, FH + 2 * M

    # ---------- 테(초과표본) ----------
    # v2.1(26-11-26): 45도 이음을 '부드러운 조각 가중치'로 — 이음선 위에서 두 조각 결이 1px 안에서 섞이고,
    # 이음선 자체도 가우스 단면(계단 없음). 조각 판정·단면 빛·이너프레임·매트 경사 모두 같은 가중치로 섞음.
    s = SS
    fw, fh, F, Lp = FW * s, FH * s, face * s, lip * s
    tex = grade_all(load_tex(st['tex']), st['tone'], st['gain'])
    layer = np.zeros((fh, fw, 3), np.float32)
    alpha = np.zeros((fh, fw), np.float32)
    yy, xx = np.mgrid[0:fh, 0:fw].astype(np.float32)
    dT, dB, dL, dR = yy, fh - 1 - yy, xx, fw - 1 - xx
    D = np.stack([dT, dB, dL, dR])
    dmin = D.min(0)
    tau = 0.30 * s                                          # 이음 전이 폭(1배 기준 약 0.3px 스케일)
    Wt = np.exp(-(D - dmin[None]) / tau); Wt /= Wt.sum(0, keepdims=True)
    del D
    inface = dmin < F
    tone_jit = 1 + rng.uniform(-0.035, 0.035, 4)
    pieces = []
    for k in range(4):
        L = fw if k < 2 else fh
        sx = strip(tex, F + 4, L, rng.integers(0, 4000), rng) * tone_jit[k]
        if k < 2:
            sx = np.rot90(sx, 1 if k == 0 else -1)          # (F+4, L)
        pieces.append(np.ascontiguousarray(sx))
    dk = [dT, dB, dL, dR]
    SGN = [1.0, -1.0, 1.0, -1.0]                            # 위·왼 = 빛을 향함
    LVL = [1.03, 0.95, 1.02, 0.96]
    k_out = 0.16 if style != 'white' else 0.06
    k_in = 0.22 if style != 'white' else 0.08
    if style == 'black':
        k_out, k_in = 0.30, 0.38
    def look(k, m, lipmode=False):
        p = pieces[k]; d = dk[k][m]
        if not lipmode:
            dd = np.clip(d, 0, F + 3).astype(int)
            if k == 0: return p[dd, xx[m].astype(int)]
            if k == 1: return p[dd, xx[m].astype(int)]
            return p[yy[m].astype(int), dd]
        q = pieces[(k + 2) % 4]                             # 이너프레임은 다른 조각 결
        if k < 2:
            qq = np.rot90(q) if q.shape[0] > q.shape[1] else q   # (F+4, fw?) 가로 길이
            return qq[(d % qq.shape[0]).astype(int), (xx[m] % qq.shape[1]).astype(int)]
        qq = np.rot90(q) if q.shape[0] < q.shape[1] else q
        return qq[(yy[m] % qq.shape[0]).astype(int), (d % qq.shape[1]).astype(int)]
    face_rgb = np.zeros((fh, fw, 3), np.float32)
    for k in range(4):
        m = inface & (Wt[k] > 1e-4)
        t = np.clip(dk[k][m] / F, 0, 1)
        outer, innr = profile_shade(t)
        sh_k = (1 + SGN[k] * outer * k_out - SGN[k] * innr * k_in) * LVL[k]
        face_rgb[m] += look(k, m) * (Wt[k][m] * sh_k)[:, None]
    layer[inface] = face_rgb[inface]
    del face_rgb
    # 마이터 이음선: 두 변 거리 차의 가우스 단면(계단 없음)
    sig = 0.42 * s
    def cor(a, b): return np.where((a < F + s) & (b < F + s), np.exp(-((a - b) / 1.4142) ** 2 / (2 * sig * sig)), 0)
    seam_w = np.maximum.reduce([cor(dT, dL), cor(dT, dR), cor(dB, dL), cor(dB, dR)]) * inface * np.clip(dmin / s, 0, 1)
    depth = 0.34 if style != 'white' else 0.12
    layer *= (1 - seam_w * depth)[..., None]
    del seam_w
    edge = np.clip(1 - dmin / s, 0, 1)                        # 바깥 가장자리 옆면 살짝
    layer *= (1 - edge * (0.25 if style != 'white' else 0.10))[..., None]
    alpha[inface] = 1

    # ---------- 이너프레임 ----------
    if inner:
        inlip = (dmin >= F) & (dmin < F + Lp)
        tl = np.clip((dmin - F) / Lp, 0, 1)
        lip_rgb = np.zeros((fh, fw, 3), np.float32)
        lsg = np.zeros((fh, fw), np.float32)
        for k in range(4):
            m = inlip & (Wt[k] > 1e-4)
            lip_rgb[m] += look(k, m, True) * Wt[k][m][:, None]
            lsg[m] += Wt[k][m] * (-SGN[k])
        layer[inlip] = lip_rgb[inlip] * st['lipdark']
        del lip_rgb
        alpha[inlip] = 1
        gw = np.clip(1 - (dmin - F) / (s * 1.2), 0, 1) * inlip   # 단 사이 틈
        layer *= (1 - gw * (0.55 if style != 'white' else 0.20))[..., None]
        lin = np.clip((tl - 0.70) / 0.30, 0, 1)
        fac = 1 + lsg * lin * (0.18 if style != 'white' else 0.06)
        layer[inlip] *= fac[inlip][..., None]

    # ---------- 매트 ----------
    if mat:
        Ms = matw * s
        inmat = (dmin >= F + Lp) & (dmin < F + Lp + Ms)
        paper = np.array([244, 241, 234], np.float32)
        g = np.random.default_rng(seed + 11).normal(0, 1, (fh, fw)).astype(np.float32)
        fibr = np.asarray(Image.fromarray(np.clip(g * 40 + 128, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.9))).astype(np.float32)
        fibr = (fibr - 128) / 40 * 1.5
        layer[inmat] = np.clip(paper + fibr[inmat][:, None], 0, 255)
        bev = inmat & (dmin >= F + Lp + Ms - s * 3)
        bsign = Wt[1] + Wt[3] - Wt[0] - Wt[2]
        layer[bev] = np.clip(np.array([250, 248, 243], np.float32) * (1 + bsign[bev] * 0.03)[:, None], 0, 255)
        alpha[inmat] = 1
    del Wt

    # ---------- 앞면이 안쪽에 드리우는 그림자 ----------
    sh = np.zeros((fh, fw), np.float32)
    inside = dmin >= F
    reach = (Lp * 0.9 + s * 3) if inner else (s * 5)
    for dd in (dT, dL):
        m = inside & (dd - F < reach * 2.2)
        sh[m] = np.maximum(sh[m], np.exp(-np.clip(dd[m] - F, 0, None) / (reach * 0.55)))
    for dd in (dB, dR):
        m = inside & (dd - F < reach)
        sh[m] = np.maximum(sh[m], 0.25 * np.exp(-np.clip(dd[m] - F, 0, None) / (reach * 0.35)))
    sh_amt = {'black': 0.55, 'white': 0.22, 'brown_oak': 0.42, 'brown_walnut': 0.50, 'light_brown': 0.46}.get(style, 0.45)
    hole = dmin >= F + Lp + (matw * s)
    mshade = (1 - sh * sh_amt)
    mshade[hole] = 1
    layer *= mshade[..., None]

    # 1배로 축소
    L8 = Image.fromarray(np.clip(layer, 0, 255).astype(np.uint8)).resize((FW, FH), Image.LANCZOS)
    A8 = Image.fromarray((alpha * 255).astype(np.uint8)).resize((FW, FH), Image.LANCZOS)

    # ---------- 벽과 벽 그림자(빛 왼쪽 위 → 오른쪽 아래로) ----------
    if transparent:
        canvas = Image.new('RGBA', (CW, CH), (0, 0, 0, 0))
    else:
        canvas = Image.new('RGBA', (CW, CH), tuple(bg) + (255,))
    shadow = Image.new('L', (CW, CH), 0)
    sd = np.zeros((CH, CW), np.float32)
    ox, oy = round(U * 0.006), round(U * 0.011)
    sd[M + oy:M + oy + FH, M + ox:M + ox + FW] = 1
    soft = np.asarray(Image.fromarray((sd * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(max(4, U * 0.016)))).astype(np.float32) / 255
    sd2 = np.zeros((CH, CW), np.float32); sd2[M + 1:M + 2 + FH, M:M + FW + 1] = 1
    tight = np.asarray(Image.fromarray((sd2 * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(max(1.5, U * 0.003)))).astype(np.float32) / 255
    sa = np.clip(soft * 0.30 + tight * 0.22, 0, 1)
    shadow = Image.fromarray((sa * 255).astype(np.uint8))
    canvas.paste(Image.new('RGBA', (CW, CH), (40, 32, 26, 255)), (0, 0), shadow)
    fr = L8.convert('RGBA'); fr.putalpha(A8)
    canvas.alpha_composite(fr, (M, M))
    # 작품: 1배 그대로
    canvas.paste(art.convert('RGBA'), (M + T, M + T))
    info = dict(style=style, inner=inner, mat=mat, art_px=[aw, ah], face_px=face, lip_px=lip, mat_px=matw,
                total_px=T, margin_px=M, art_box=[M + T, M + T, aw, ah], out_px=[CW, CH])
    return canvas, info


def verify(out, art, box):
    x, y, w, h = box
    a = np.asarray(art.convert('RGB')).astype(int)
    b = np.asarray(out.convert('RGB').crop((x, y, x + w, y + h))).astype(int)
    return int(np.abs(a - b).max())


def nine_slice(style, inner=True, mat=False, size=1200, rim=0.04):
    """CSS border-image용 9분할 자산: 가운데(작품 자리) 투명, 벽 그림자 없음."""
    dummy = Image.new('RGB', (size, size), (128, 128, 128))
    im, info = render(dummy, style, inner, mat, margin=0, transparent=True, rim=rim)
    a = np.asarray(im).copy()
    T = info['total_px']
    a[T:T + size, T:T + size, 3] = 0
    return Image.fromarray(a), T



# ======================= v3.1: 이케아식 '깨끗한 흰 이너(흰 매트)' 액자 =======================
# 대표님 판정(2026-11-26 18:46): "이너프레임 오크톤 이케아처럼 흰색이너만 써라" → 종이 결·누런 톤·얇은 띠 금지.
#   v3의 '수채화지 결(W2) + 따뜻한 흰(244,239,229) + 유화 2.5% 띠'는 폐기.
#   '선화동 in Paris' 사진에서 속지처럼 보인 흰 띠 = 속지 아님(종이 면이 모자라 뒤판이 보인 것) — 오독, 근거로 사용 금지.
# 근거 = 이케아 공식 제품 사진(ikea.com/kr, 2026-11-26 원격 브라우저로 확인):
#   RÖDALM 오크 무늬 30×40 상세컷: 이너 = 결 없는 깨끗한 흰 매트, 창 단면은 가는 흰 선, 테 안쪽 벽이 매트 위·왼에 부드러운 회색 그림자.
#   폭(바깥 긴 변 기준): RÖDALM 30×40 매트 10.7%(제품컷 실측 9.8~11.0%), KNOPPÄNG 50×70 7.6%, Hammer(RÖDALM 3칸) 6.7~8.5%.
#   → 드로잉 PC 9.0%, 유화·사진 PC 7.6%(KNOPPÄNG 50×70 = 대형 규격 비율), 모바일 둘 다 5.0%(칸 150~182px에서 작품 면적 확보).
MAT_TONE = (250, 250, 247)                                  # 이케아 흰 매트(중성 흰, 결 없음) — 누런 톤 금지
MEDIA = {   # 매체별 기본값: 긴 변 대비 비율
    'drawing': dict(style='black', face=0.040, wall=0.011, mat=0.090, mat_mobile=0.050),
    # 대표님 18:18 판정: 오크(/11 보울러와 같은 질감·밝기) 테 유지
    'oil':     dict(style='brown_oak', face=0.040, wall=0.011, mat=0.076, mat_mobile=0.050),
    'photo':   dict(style='brown_oak', face=0.040, wall=0.011, mat=0.076, mat_mobile=0.050),
}


def paper_tile(h, w, seed=3):
    """v3 종이 결 속지 — 대표님 18:46 판정으로 폐기(이케아 흰 이너만). 호출 금지."""
    raise RuntimeError('v3 종이 결 속지는 폐기됨 — v3.1 흰 이너(MAT_TONE 단색)를 쓸 것')


def matframe_nine(style, F, Wd, M, size=900, bevel=3.4, seed=7):
    """CSS border-image용 9분할: 앞면 테(F) + 안쪽 옆벽(Wd) + 흰 이너(M, 창 단면 bevel 포함). 가운데 투명.
    단위는 원본 px(화면에서 border-width로 축소됨). 빛은 왼쪽 위 하나."""
    T = F + Wd + M
    N = size + 2 * T
    # 1) 앞면 테: 기존 v2.1 렌더(실사 결·45도 이음·단면 빛) 그대로, 이너프레임 단 없이
    dummy = Image.new('RGB', (size + 2 * (Wd + M), size + 2 * (Wd + M)), (128, 128, 128))
    face_im, info = render(dummy, style, inner=False, mat=False, margin=0, transparent=True, face_px=F, seed=seed)
    assert info['total_px'] == F
    _fa = np.asarray(face_im).copy(); _fa[F:N - F, F:N - F, 3] = 0; face_im = Image.fromarray(_fa)   # 가운데(더미) 비움
    face = np.asarray(face_im).astype(np.float32)          # RGBA (N, N)
    s = SS
    n = N * s
    up = np.asarray(face_im.resize((n, n), Image.LANCZOS)).astype(np.float32)
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32) + 0.5
    dT, dB, dL, dR = yy, n - yy, xx, n - xx
    D = np.stack([dT, dB, dL, dR]); k = D.argmin(0); dmin = D.min(0); del D
    Fs, Ws, Ms, Bs = F * s, Wd * s, M * s, bevel * s
    rgb = np.zeros((n, n, 3), np.float32)
    # 변별 빛 계수: 위·왼 변(빛을 등진 안쪽 벽/창 단면)은 어둡고, 아래·오른 변은 빛을 받음
    LIT = np.array([0, 1, 0, 1], np.float32)[k]           # 1 = 아래·오른 변
    # 2) 옆벽: 앞면 결을 안쪽으로 접어 비춘 것(같은 재질) + 속지에서 튄 빛
    wall = (dmin >= Fs) & (dmin < Fs + Ws)
    mir = np.clip(2 * Fs - dmin - 1, 0, Fs - 1)             # 앞면에서 대칭 위치
    sy = np.where(k == 0, mir, np.where(k == 1, n - 1 - mir, yy)).astype(int)
    sx = np.where(k == 2, mir, np.where(k == 3, n - 1 - mir, xx)).astype(int)
    src = up[np.clip(sy, 0, n - 1), np.clip(sx, 0, n - 1), :3]
    bounce = {'black': 0.42, 'white': 0.10}.get(style, 0.16)   # 검정 RÖDALM 실측: 옆벽이 속지의 0.72~0.80 밝기로 회색 띠
    matc = np.array(MAT_TONE, np.float32)
    tw = np.clip((dmin - Fs) / Ws, 0, 1)                    # 0=앞면 쪽, 1=속지 쪽
    wl = (src * (1 - bounce) + matc * bounce * (0.55 + 0.45 * tw[..., None]))
    wl *= (0.70 + 0.30 * LIT)[..., None]                    # 위·왼 벽 0.70, 아래·오른 벽 1.0
    rgb[wall] = wl[wall]
    # 3) 흰 이너(매트)
    # v3.1: 결 없는 깨끗한 흰 매트(이케아). 종이 결 타일 사용 안 함.
    inmat = (dmin >= Fs + Ws) & (dmin < Fs + Ws + Ms)
    rgb[inmat] = np.array(MAT_TONE, np.float32)
    # 4) 창 단면(45도 깎인 종이 심): 속지보다 밝은 흰 심. 아래·오른 창변 = 빛을 향함, 위·왼 = 등짐
    bev = inmat & (dmin >= Fs + Ws + Ms - Bs)
    core = np.array([253, 253, 251], np.float32)            # 매트 심도 같은 흰색(이케아 상세컷: 가는 흰 선)
    bshade = np.where(LIT > 0, 1.01, 0.93)
    rgb[bev] = np.clip(core * bshade[bev][:, None], 0, 255)
    # 창 단면 바깥 경계(속지 면과 꺾이는 선)에 아주 옅은 선
    edge = inmat & (np.abs(dmin - (Fs + Ws + Ms - Bs)) < s * 0.6)
    rgb[edge] *= np.where(LIT[edge] > 0, 0.985, 0.95)[:, None]
    # 5) 테·옆벽이 속지 위에 드리우는 그림자(위·왼 진하고 넓게, 아래·오른 옅게)
    inside = dmin >= Fs + Ws
    r = (Ws + 2.2 * s)
    dd = dmin - (Fs + Ws)
    # v3.1: 변마다 자기 거리로 그림자를 따로 계산해 곱함 → 모서리에서 45도 이음선 없이 자연스럽게 겹침(이케아 상세컷)
    shade = np.ones((n, n), np.float32)
    for Dk, lit in ((dT, 0), (dL, 0), (dB, 1), (dR, 1)):
        a_, r_ = (0.07, r * 0.45) if lit else (0.24, r * 1.25)
        shade *= 1 - a_ * np.exp(-np.clip(Dk - (Fs + Ws), 0, None) / r_)
    shade[~inside] = 1
    shade[bev] = 1 - (1 - shade[bev]) * 0.5
    rgb *= shade[..., None]
    # 옆벽 자체에도 앞면이 드리우는 그림자(앞면 바로 안쪽이 가장 어두움)
    ws = 1 - 0.35 * np.exp(-np.clip(dmin - Fs, 0, None) / (Ws * 0.45 + 1))
    rgb[wall] *= ws[wall][:, None]
    alpha = (dmin < Fs + Ws + Ms).astype(np.float32)
    L8 = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).resize((N, N), Image.LANCZOS)
    A8 = Image.fromarray((alpha * 255).astype(np.uint8)).resize((N, N), Image.LANCZOS)
    out = L8.convert('RGBA'); out.putalpha(A8)
    out.alpha_composite(face_im)                            # 앞면 테를 맨 위에
    a = np.asarray(out).copy(); a[T:T + size, T:T + size, 3] = 0
    return Image.fromarray(a), T


def matframe_render(art, media='drawing', mobile=False, bg=(247, 243, 236), margin=None, style=None):
    """작품 1점에 v3.1 액자(테+옆벽+흰 이너)를 씌운 그림(검수·판정용). 작품 픽셀은 그대로."""
    md = MEDIA[media]; st = style or md['style']
    aw, ah = art.size
    m = md['mat_mobile'] if mobile else md['mat']
    k = md['face'] + md['wall'] + m
    a = max(aw, ah) / min(aw, ah)
    W = round(min(aw, ah) * (1 + 2 * k * a / (1 - 2 * k)))     # 바깥 긴 변 기준 비율이 맞도록
    L = max(aw, ah) + (W - min(aw, ah))
    F, Wd, Mm = round(md['face'] * L), max(2, round(md['wall'] * L)), round(m * L)
    nine, T = matframe_nine(st, F, Wd, Mm, size=max(64, min(aw, ah) // 2), bevel=max(1.3, 0.0030 * L))
    FW, FH = aw + 2 * T, ah + 2 * T
    na = np.asarray(nine); S = nine.size[0]; c = S - 2 * T
    fr = np.zeros((FH, FW, 4), np.uint8)
    fr[:T, :T] = na[:T, :T]; fr[:T, -T:] = na[:T, -T:]; fr[-T:, :T] = na[-T:, :T]; fr[-T:, -T:] = na[-T:, -T:]
    def st_(arr, shape): return np.asarray(Image.fromarray(arr).resize(shape, Image.LANCZOS))
    fr[:T, T:-T] = st_(na[:T, T:T + c], (aw, T)); fr[-T:, T:-T] = st_(na[-T:, T:T + c], (aw, T))
    fr[T:-T, :T] = st_(na[T:T + c, :T], (T, ah)); fr[T:-T, -T:] = st_(na[T:T + c, -T:], (T, ah))
    M = margin if margin is not None else max(24, round(L * 0.05))
    canvas = Image.new('RGBA', (FW + 2 * M, FH + 2 * M), tuple(bg) + (255,))
    sd = np.zeros((FH + 2 * M, FW + 2 * M), np.float32)
    ox, oy = round(L * 0.006), round(L * 0.011); sd[M + oy:M + oy + FH, M + ox:M + ox + FW] = 1
    soft = np.asarray(Image.fromarray((sd * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(max(4, L * 0.016)))).astype(np.float32) / 255
    canvas.paste(Image.new('RGBA', canvas.size, (40, 32, 26, 255)), (0, 0), Image.fromarray((np.clip(soft * 0.42, 0, 1) * 255).astype(np.uint8)))
    canvas.alpha_composite(Image.fromarray(fr), (M, M))
    canvas.paste(art.convert('RGBA'), (M + T, M + T))
    return canvas, dict(media=media, style=st, F=F, wall=Wd, mat=Mm, T=T, L=L, art_box=[M + T, M + T, aw, ah])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('art')
    ap.add_argument('--style', default=None, choices=list(STYLES))
    ap.add_argument('--inner', default='on', choices=['on', 'off'])
    ap.add_argument('--mat', default=None, choices=['on', 'off', 'paper'], help='paper = v3.1 이케아식 깨끗한 흰 이너(결 없음, 매체별 기본값)')
    ap.add_argument('--media', default=None, choices=['drawing', 'oil', 'photo'], help='drawing=검정+흰 이너 9%, oil·photo=오크+흰 이너 7.6% (모바일 5%)')
    ap.add_argument('--mobile', action='store_true')
    ap.add_argument('--bg', default='F7F3EC')
    ap.add_argument('--out')
    ap.add_argument('--json', default=os.path.join(HERE, 'aurum_frames.json'))
    ap.add_argument('--quality', type=int, default=92)
    a = ap.parse_args()
    art = Image.open(a.art)
    bg = tuple(int(a.bg[i:i + 2], 16) for i in (0, 2, 4))
    if a.media and a.mat is None: a.mat = 'paper'
    if a.mat == 'paper':
        out, info = matframe_render(art, a.media or 'drawing', a.mobile, bg, style=a.style)
        a.style = info['style']; a.inner = 'off'
    else:
        a.style = a.style or 'brown_walnut'
        out, info = render(art, a.style, a.inner == 'on', a.mat == 'on', bg)
    d = verify(out, art, info['art_box'])
    assert d == 0, f'작품 픽셀이 바뀜(최대 차 {d}) — 중단'
    dst = a.out or os.path.splitext(a.art)[0] + f'_afr_{a.style}{"_in" if a.inner=="on" else ""}{"_mat" if a.mat=="on" else ""}{"_paper" if a.mat=="paper" else ""}.jpg'
    if dst.lower().endswith(('.jpg', '.jpeg')):
        out.convert('RGB').save(dst, quality=a.quality, subsampling=0)
        # JPEG 저장 후에는 압축 때문에 1~3단계 차가 생길 수 있음 → PNG 원본 대조 결과(0)를 기록
    else:
        out.save(dst)
    info.update(src=os.path.basename(a.art), out=os.path.basename(dst), art_pixel_diff_before_save=d,
                date=datetime.date.today().isoformat())
    db = {}
    if os.path.exists(a.json):
        db = json.load(open(a.json, encoding='utf8'))
    db.setdefault('renders', {})[os.path.basename(dst)] = info
    json.dump(db, open(a.json, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
    print(dst, info)


if __name__ == '__main__':
    main()
