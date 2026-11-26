import sys, os, json
sys.path.insert(0,'/home/claude/fv33/code'); os.environ['AURUM_TEX']='/home/claude/fv33/tex'
import aurum_frame as af
Ls=1050; out={}
spec={'afr9v33_black_white_draw.png':('black',0.04,0.090),'afr9v33_black_white_draw_mo.png':('black',0.04,0.050),
      'afr9v33_oak_white_oil.png':('brown_oak',0.04,0.076),'afr9v33_oak_white_oil_mo.png':('brown_oak',0.04,0.050)}
for fn,(st,f,m) in spec.items():
    F,M=round(f*Ls),round(m*Ls)
    im,T=af.matframe_nine_v33(st,F,M,Ls,size=600)
    im.save('/home/claude/fv33/nine/'+fn,optimize=True)
    out[fn]=dict(style=st,face=F,mat=M,slice=T,size=im.size,bytes=os.path.getsize('/home/claude/fv33/nine/'+fn),ratio_of_long_side=dict(face=f,mat=m),shadow=af.SHADOW33,bevel=af.BEVEL33,art_shadow=af.ART_SHADOW33)
    print(fn,T,out[fn]['bytes'])
json.dump(out,open('/home/claude/fv33/nine/nine_v33.json','w'),indent=1,ensure_ascii=False)
