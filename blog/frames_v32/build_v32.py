import sys, os, json
sys.path.insert(0,'/home/claude/fv32/code'); os.environ['AURUM_TEX']='/home/claude/fv32/tex'
import aurum_frame as af
Ls=1050; out={}
spec={'afr9v32_black_white_draw.png':('black',0.04,0.090),
      'afr9v32_black_white_draw_mo.png':('black',0.04,0.050),
      'afr9v32_oak_white_oil.png':('brown_oak',0.04,0.076),
      'afr9v32_oak_white_oil_mo.png':('brown_oak',0.04,0.050)}
for fn,(st,f,m) in spec.items():
    F,M,H=round(f*Ls),round(m*Ls),af.WALL_H*Ls
    im,T=af.matframe_nine_v32(st,F,M,H,size=600)
    im.save('nine/'+fn,optimize=True)
    out[fn]=dict(style=st,face=F,wall=0,mat=M,wall_height_px=round(H,1),slice=T,size=im.size,bytes=os.path.getsize('nine/'+fn),
                 ratio_of_long_side=dict(face=f,mat=m,wall_height=af.WALL_H),light=af.LIGHT)
    print(fn,out[fn]['slice'],out[fn]['bytes'])
json.dump(out,open('nine/nine_v32.json','w'),indent=1,ensure_ascii=False)
