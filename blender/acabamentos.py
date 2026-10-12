import numpy as np, io, base64, json
from PIL import Image
S=512
rng=np.random.default_rng(21)
fx=np.fft.fftfreq(S)[None,:];fy=np.fft.fftfreq(S)[:,None]
def pnoise(scale,ax=1.0,ay=1.0,seed=None):
    r=(np.random.default_rng(seed) if seed is not None else rng).standard_normal((S,S))
    f=np.fft.fft2(r);k=np.exp(-((fx*scale*ax)**2+(fy*scale*ay)**2)*3.0)
    o=np.real(np.fft.ifft2(f*k));o=(o-o.min())/(o.max()-o.min());return o
yy,xx=np.mgrid[0:S,0:S]/S
def lerp(a,b,t):return a[None,None,:]*(1-t[...,None])+b[None,None,:]*t[...,None]
def rgb(h):h=h.lstrip('#');return np.array([int(h[i:i+2],16)/255 for i in(0,2,4)])
def save(a,path_key,out,q=84):
    im=Image.fromarray((np.clip(a,0,1)*255).astype('uint8'));b=io.BytesIO();im.save(b,'JPEG',quality=q)
    out[path_key]='data:image/jpeg;base64,'+base64.b64encode(b.getvalue()).decode();return len(b.getvalue())
# ---- madeira: veio horizontal (ao longo de u)
def wood(light,dark,ringf=14,warp=0.8,streak=0.5,pore=0.35,wash=None,seed=0):
    w=pnoise(60,1.0,0.25,seed)                         # deformação lenta ao longo do veio
    ring=np.sin((yy*ringf+ (w-0.5)*warp*6)*2*np.pi)*0.5+0.5
    ring=ring**1.6
    st=pnoise(160,1.0,0.03,seed+1)                    # estrias finas alongadas
    fine=pnoise(260,1.0,0.02,seed+2)
    t=np.clip(0.55*ring+streak*0.6*(st-0.5)+0.25*(fine-0.5)+0.2,0,1)
    col=lerp(rgb(light),rgb(dark),t)
    if wash is not None:                                # lavado: poros claros (cerused)
        p=np.clip((fine-0.45)*3.2,0,1)*pore*2+np.clip((st-0.55)*2.5,0,1)*0.5
        col=col*(1-np.clip(p,0,1)[...,None]*0.75)+rgb(wash)[None,None,:]*np.clip(p,0,1)[...,None]*0.75
    return col
out={}
woods={
 'carvalho':dict(light='#C79A63',dark='#8C6338',ringf=12),
 'nogueira':dict(light='#7A5036',dark='#3A2216',ringf=10,streak=0.8),
 'pauferro':dict(light='#5A2E22',dark='#1B0E0B',ringf=16,streak=1.0,warp=1.2),
 'freixo':dict(light='#E3CBA3',dark='#B8956A',ringf=9),
 'cerejeira':dict(light='#B9683F',dark='#7A3A22',ringf=11),
 'ebano':dict(light='#3A312C',dark='#0E0B0A',ringf=18,streak=0.9),
 'carvalho_lavado':dict(light='#D8C4A4',dark='#A8916E',ringf=12,wash='#F4EEE4',pore=0.5),
 'nogueira_lavada':dict(light='#9A7F6B',dark='#5E4638',ringf=10,wash='#D8CCC0',pore=0.45,streak=0.8),
 'cinza_lavado':dict(light='#B7B4AE',dark='#7E7A74',ringf=12,wash='#E9E7E3',pore=0.5),
 'branco_lavado':dict(light='#EDE9E1',dark='#CFC8BB',ringf=12,wash='#FFFFFF',pore=0.4),
}
sizes={}
for i,(k,p) in enumerate(woods.items()):
    sizes[k]=save(wood(seed=i*7,**p),k,out)
# ---- pedras
def vein(ax,ay,k,wp,off,wid,f,blur_s=None):
    u=(xx*ax+yy*ay)*k+wp*(f-0.5)+off
    d=np.abs((u%1.0)-0.5);v=np.exp(-(d/wid)**1.5)
    return v
def stone(base,vc,veins,cloud=0.08,cloudc=None,seed=0):
    f=pnoise(70,1,1,seed);g=pnoise(130,1,1,seed+1);c=pnoise(40,1,1,seed+2)
    col=np.ones((S,S,3))*rgb(base)[None,None,:]
    cc=rgb(cloudc) if cloudc else rgb(base)*0.82
    col=col*(1-cloud*2*c[...,None])+cc[None,None,:]*cloud*2*c[...,None]
    for (ax,ay,k,wp,off,wid,strength,colr,gm) in veins:
        v=vein(ax,ay,k,wp,off,wid,f if gm==0 else g)*strength*np.clip((pnoise(55,1,1,seed+int(off*10)+5)-0.38)*3.2,0,1)
        col=col*(1-v[...,None])+rgb(colr)[None,None,:]*v[...,None]
    return col
stones={
 'carrara':dict(base='#EDEDEB',vc='',veins=[(1,1,2,0.55,0.1,0.05,0.55,'#8C9096',0),(1,-1,3,0.5,0.4,0.025,0.45,'#9AA0A6',1)],cloud=0.07),
 'calacatta':dict(base='#F6F3EC',vc='',veins=[(1,1,2,0.6,0.2,0.05,0.9,'#B58A4A',0),(1,2,2,0.5,0.6,0.02,0.6,'#8E8478',1),(-1,1,3,0.6,0.1,0.015,0.5,'#C9A267',0)],cloud=0.05),
 'statuario':dict(base='#F2F2F0',vc='',veins=[(1,1,2,0.5,0.3,0.03,0.85,'#4B4E54',0),(1,-2,2,0.5,0.5,0.015,0.55,'#767A80',1)],cloud=0.04),
 'nero':dict(base='#0B0B0C',vc='',veins=[(1,1,2,0.6,0.2,0.03,0.9,'#F0EEE8',0),(1,-1,3,0.5,0.5,0.012,0.7,'#D9C9A0',1)],cloud=0.1,cloudc='#2A2A2C'),
 'emperador':dict(base='#6B4430',vc='',veins=[(1,1,3,0.55,0.3,0.05,0.7,'#D9BF9C',0),(1,-1,2,0.5,0.1,0.02,0.5,'#E8D5B7',1)],cloud=0.25,cloudc='#8E6446'),
 'verde':dict(base='#123D32',vc='',veins=[(1,1,2,0.55,0.2,0.04,0.8,'#E4EBE2',0),(1,-1,3,0.5,0.45,0.015,0.55,'#B8C9B6',1)],cloud=0.2,cloudc='#2C6A55'),
}
for i,(k,p) in enumerate(stones.items()):
    sizes[k]=save(stone(seed=100+i*5,**{a:b for a,b in p.items() if a!='vc'},base=p['base']) if False else stone(p['base'],'',p['veins'],p['cloud'],p.get('cloudc'),100+i*5),k,out,q=88)
# travertino: faixas horizontais + poros
b=pnoise(40,1.0,0.1,300);fi=pnoise(200,1.0,0.03,301);po=pnoise(7,1,1,302)
t=np.clip(0.5*b+0.3*fi,0,1)
col=lerp(rgb('#E3D6BF'),rgb('#BFA987'),t)
pores=np.clip((po-0.66)*5,0,1);col=col*(1-pores[...,None]*0.28)
sizes['travertino']=save(col,'travertino',out,88)
open('/home/user/mesa-gomos/acabamentos-3d.js','w').write('/* Texturas de madeira e pedra (geradas por blender/acabamentos.py). */\nwindow.ACAB='+json.dumps(out)+';\n')
print(sizes)
# folha de contacto
ims=[]
import re
for k,v in out.items():
    ims.append(Image.open(io.BytesIO(base64.b64decode(v.split(',')[1]))).resize((200,200)))
sheet=Image.new('RGB',(200*6,200*3))
for i,im in enumerate(ims[:18]):sheet.paste(im,((i%6)*200,(i//6)*200))
sheet.save('../acab_sheet.png');print(list(out.keys()))
