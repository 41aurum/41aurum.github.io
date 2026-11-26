import json
P='html body .ag-c-oldie.ag-c-oldie img[data-filename*="oldiecola_%s"]'
BASE='https://41aurum.github.io/blog/frames_v31/'
# (파일 조각, 매체, 세로/가로 비, PC 칸 폭, 모바일(390) 칸 폭)
W=[('04_padokot.jpg','oil',1100/844,574,374),('05_padokot_drawing','drawing',1,420,292),('06_pinkkot','oil',1100/825,408,182),
   ('07b_pin_drawing','drawing',1,272,182),('08_closet.jpg','oil',1100/885,272,182),('08b_closet_drawing','drawing',1,408,182),
   ('09_pado.jpg','oil',1100/880,408,182),('11_pado_drawing','drawing',1,272,182),('12_cheongpado','oil',1100/825,272,182),
   ('14_cheong_drawing','drawing',1,408,182),('15_bambada','oil',1100/946,408,150),('17_bam_drawing','drawing',1,272,150)]
K={'drawing':(0.04+0.011+0.090, 0.04+0.011+0.050),'oil':(0.04+0.011+0.076, 0.04+0.011+0.050)}
SL={'drawing':(148,106),'oil':(134,106)}
IMG={'drawing':('afr9v31_black_white_draw.png','afr9v31_black_white_draw_mo.png'),'oil':('afr9v31_oak_white_oil.png','afr9v31_oak_white_oil_mo.png')}
def B(k,Wd,a): return k*Wd*a/(1+2*k*(a-1))   # 바깥 긴 변 × k (세로 그림: 긴 변 = 높이)
rows=[];pc=[];mo=[]
for f,md,a,wp,wm in W:
    bp=B(K[md][0],wp,a); bm=B(K[md][1],wm,a)
    vw=bm/390*100
    pc.append(f'{P%f}{{border-width:min({round(bp)}px,{vw*K[md][0]/K[md][1]:.2f}vw)!important}}')
    mo.append(f'{P%f}{{border-width:{vw:.2f}vw!important}}')
    rows.append(dict(f=f,media=md,pc_cell=wp,pc_border=round(bp),pc_art=wp-2*round(bp),mo_cell=wm,mo_border=round(bm,1),mo_art=round(wm-2*bm)))
sel=lambda md:',\n'.join(P%f for f,m,*_ in W if m==md)
css=f'''<style id="aufr5">/* 아우름 액자 v3.1 (26-11-26 18:46 대표님 판정) — 드로잉 6점 = 검정 테 + 이케아식 깨끗한 흰 이너, 유화(캔버스) 6점 = 오크 테(/11 보울러 톤) + 같은 흰 이너.
   이너 = 결 없는 중성 흰 매트(#FAFAF7), 창 단면 가는 흰 선, 테 안쪽 벽이 위·왼에 드리우는 그림자 — 이케아 RÖDALM 오크 무늬 상세컷 대조.
   폭(바깥 긴 변 기준): 테 4%, 옆벽 1.1%, 흰 이너 드로잉 9%·유화 7.6%(모바일 둘 다 5%) — RÖDALM 30×40 10.7%·KNOPPÄNG 50×70 7.6% 근거. 빛 왼쪽 위, 광택 없음. */
'''+f'''{sel('drawing')},
{sel('oil')}{{
 box-sizing:border-box!important;padding:0!important;background:transparent!important;outline:0!important;border-radius:0!important;
 border:min(16px,2vw) solid #EFEDE8!important;
 box-shadow:4px 8px 12px -4px rgba(40,32,26,.34),1px 2px 3px rgba(40,32,26,.22)!important}}
{sel('drawing')}{{border-image:url({BASE}{IMG['drawing'][0]}) {SL['drawing'][0]} / 1 stretch!important}}
{sel('oil')}{{border-image:url({BASE}{IMG['oil'][0]}) {SL['oil'][0]} / 1 stretch!important}}
{chr(10).join(pc)}
@media (max-width:640px){{
{sel('drawing')}{{border-image:url({BASE}{IMG['drawing'][1]}) {SL['drawing'][1]} / 1 stretch!important}}
{sel('oil')}{{border-image:url({BASE}{IMG['oil'][1]}) {SL['oil'][1]} / 1 stretch!important}}
{chr(10).join(mo)}
{sel('drawing')},
{sel('oil')}{{box-shadow:2px 4px 7px -3px rgba(40,32,26,.32),1px 1px 2px rgba(40,32,26,.2)!important}}}}
</style>'''
open('frag/p5_aufr5_v31.html','w').write(css); json.dump(rows,open('frag/v31_sizes.json','w'),ensure_ascii=False,indent=0)
for r in rows: print(r)
print(len(css))
