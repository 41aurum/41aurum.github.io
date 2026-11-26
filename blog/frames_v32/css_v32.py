import json
P='html body .ag-c-oldie.ag-c-oldie img[data-filename*="oldiecola_%s"]'
Q='html body .ag-c-oldie.ag-c-oldie figure[data-filename*="oldiecola_%s"] span'
AW={'04_padokot.jpg':844,'05_padokot_drawing':420,'06_pinkkot':825,'07b_pin_drawing':420,'08_closet.jpg':885,'08b_closet_drawing':420,'09_pado.jpg':880,'11_pado_drawing':420,'12_cheongpado':825,'14_cheong_drawing':420,'15_bambada':946,'17_bam_drawing':420}  # 본문 img width 속성(=최대 표시 폭)
CUT=0.0065  # 창(매트 두께 0.4%) 그림자 도달: 0.4%×cot(높이 20~80도 면광원)×위 성분 0.77 → 대부분 0.3% 안에서 풀리고 0.65%에서 0 (긴 변 기준)
BASE='https://41aurum.github.io/blog/frames_v32/'
# (파일 조각, 매체, 세로/가로 비, PC 칸 폭, 모바일(390) 칸 폭)
W=[('04_padokot.jpg','oil',1100/844,574,374),('05_padokot_drawing','drawing',1,420,292),('06_pinkkot','oil',1100/825,408,182),
   ('07b_pin_drawing','drawing',1,272,182),('08_closet.jpg','oil',1100/885,272,182),('08b_closet_drawing','drawing',1,408,182),
   ('09_pado.jpg','oil',1100/880,408,182),('11_pado_drawing','drawing',1,272,182),('12_cheongpado','oil',1100/825,272,182),
   ('14_cheong_drawing','drawing',1,408,182),('15_bambada','oil',1100/946,408,150),('17_bam_drawing','drawing',1,272,150)]
K={'drawing':(0.04+0.090, 0.04+0.050),'oil':(0.04+0.076, 0.04+0.050)}
SL={'drawing':(136,94),'oil':(122,94)}
IMG={'drawing':('afr9v32_black_white_draw.png','afr9v32_black_white_draw_mo.png'),'oil':('afr9v32_oak_white_oil.png','afr9v32_oak_white_oil_mo.png')}
def B(k,Wd,a): return k*Wd*a/(1+2*k*(a-1))   # 바깥 긴 변 × k (세로 그림: 긴 변 = 높이)
rows=[];pc=[];mo=[];sp=[];sm=[]
for f,md,a,wp,wm in W:
    bp=B(K[md][0],wp,a); bm=B(K[md][1],wm,a)
    vw=bm/390*100
    pc.append(f'{P%f}{{border-width:min({round(bp)}px,{vw*K[md][0]/K[md][1]:.2f}vw)!important}}')
    mo.append(f'{P%f}{{border-width:{vw:.2f}vw!important}}')
    sp.append(f'{Q%f}::after{{top:min({round(bp)}px,{vw*K[md][0]/K[md][1]:.2f}vw);left:min({round(bp)}px,{vw*K[md][0]/K[md][1]:.2f}vw);width:calc(min({AW[f]}px,100%) - 2*min({round(bp)}px,{vw*K[md][0]/K[md][1]:.2f}vw));bottom:min({round(bp)}px,{vw*K[md][0]/K[md][1]:.2f}vw);background-size:100% {max(1.2,CUT/K[md][0]*bp):.1f}px,{max(1.0,CUT*0.84/K[md][0]*bp):.1f}px 100%!important}}')
    sm.append(f'{Q%f}::after{{top:{vw:.2f}vw;left:{vw:.2f}vw;width:calc(min({AW[f]}px,100%) - {2*vw:.2f}vw);bottom:{vw:.2f}vw;background-size:100% {max(1.0,CUT/K[md][1]*bm):.1f}px,{max(1.0,CUT*0.84/K[md][1]*bm):.1f}px 100%!important}}')
    rows.append(dict(f=f,media=md,pc_cell=wp,pc_border=round(bp),pc_art=wp-2*round(bp),mo_cell=wm,mo_border=round(bm,1),mo_art=round(wm-2*bm)))
sel=lambda md:',\n'.join(P%f for f,m,*_ in W if m==md)
selq=',\n'.join(Q%f for f,*_ in W)
css=f'''<style id="aufr5">/* 아우름 액자 v3.2 (26-11-26 19:09 대표님 판정) — 드로잉 6점 = 검정 테, 유화 6점 = 오크 테(/11 보울러 톤), 이너 = 결 없는 흰 매트(#FAFAF7).
   이너 둘레 색 띠·선 없음(v3.1 옆벽 1.1% 띠 폐기). 그림자 = 테 높이(긴 변 2.6%)가 왼쪽 위 빛(위에서 왼쪽으로 40도, 높이 50도 중심 20~80도 면광원)을 가려 흰 이너의 위·왼에만 떨어지는 반그림자(최대 16%).
   창: 매트 두께(0.4%)가 작품 위·왼 가장자리에 얇은 그림자. 오른쪽·아래에는 그림자 없음. 폭(바깥 긴 변): 테 4% + 흰 이너 드로잉 9%·유화 7.6%(모바일 5%). */
'''+f'''{sel('drawing')},
{sel('oil')}{{
 box-sizing:border-box!important;padding:0!important;background:transparent!important;outline:0!important;border-radius:0!important;
 border:min(16px,2vw) solid #EFEDE8!important;
 box-shadow:4px 8px 12px -4px rgba(40,32,26,.34),1px 2px 3px rgba(40,32,26,.22)!important}}
{sel('drawing')}{{border-image:url({BASE}{IMG['drawing'][0]}) {SL['drawing'][0]} / 1 stretch!important}}
{sel('oil')}{{border-image:url({BASE}{IMG['oil'][0]}) {SL['oil'][0]} / 1 stretch!important}}
{chr(10).join(pc)}
{selq}{{display:block!important;position:relative!important}}
{selq.replace(' span',' span img')}{{display:block!important}}
{selq.replace(',',':after,')}::after{{content:'';position:absolute;pointer-events:none;background:linear-gradient(to bottom,rgba(40,33,26,.15),rgba(40,33,26,.07) 30%,rgba(40,33,26,.025) 65%,rgba(40,33,26,0)) top left no-repeat,linear-gradient(to right,rgba(40,33,26,.15),rgba(40,33,26,.06) 30%,rgba(40,33,26,.02) 65%,rgba(40,33,26,0)) top left no-repeat}}
{chr(10).join(sp)}
@media (max-width:640px){{
{sel('drawing')}{{border-image:url({BASE}{IMG['drawing'][1]}) {SL['drawing'][1]} / 1 stretch!important}}
{sel('oil')}{{border-image:url({BASE}{IMG['oil'][1]}) {SL['oil'][1]} / 1 stretch!important}}
{chr(10).join(mo)}
{chr(10).join(sm)}
{sel('drawing')},
{sel('oil')}{{box-shadow:2px 4px 7px -3px rgba(40,32,26,.32),1px 1px 2px rgba(40,32,26,.2)!important}}}}
</style>'''
open('frag/p5_aufr5_v32.html','w').write(css); json.dump(rows,open('frag/v32_sizes.json','w'),ensure_ascii=False,indent=0)
for r in rows: print(r)
print(len(css))
