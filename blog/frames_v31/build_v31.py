import sys, os, json
sys.path.insert(0,'/home/claude/fv31/code'); os.environ['AURUM_TEX']='/home/claude/fv31/tex'
import aurum_frame as af
Ls=1050; out={}
spec={'afr9v31_black_white_draw.png':('black',0.04,0.011,0.090,3.2),
      'afr9v31_black_white_draw_mo.png':('black',0.04,0.011,0.050,4.0),
      'afr9v31_oak_white_oil.png':('brown_oak',0.04,0.011,0.076,3.2),
      'afr9v31_oak_white_oil_mo.png':('brown_oak',0.04,0.011,0.050,4.0)}
for fn,(st,f,w,m,bv) in spec.items():
    F,Wd,M=round(f*Ls),round(w*Ls),round(m*Ls)
    im,T=af.matframe_nine(st,F,Wd,M,size=600,bevel=bv)
    im.save('nine/'+fn,optimize=True)
    out[fn]=dict(style=st,face=F,wall=Wd,mat=M,slice=T,size=im.size,bytes=os.path.getsize('nine/'+fn),ratio_of_long_side=dict(face=f,wall=w,mat=m))
    print(fn,out[fn])
json.dump(out,open('nine/nine_v31.json','w'),indent=1)
