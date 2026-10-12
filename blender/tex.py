import numpy as np, sys
from PIL import Image, ImageDraw, ImageFilter
S=1024
rng=np.random.default_rng(5)

def terry():
    im=Image.new('L',(S,S),40);d=ImageDraw.Draw(im)
    n=11000
    for _ in range(n):
        x,y=rng.uniform(0,S,2);th=rng.uniform(0,6.283)
        L=rng.normal(58,16);w=rng.normal(16,3);bend=rng.normal(0,0.9)
        v=rng.uniform(95,235)
        pts=[];cx,cy=x,y;a=th
        for k in range(7):
            pts.append((cx,cy));a+=bend/6;cx+=np.cos(a)*L/6;cy+=np.sin(a)*L/6
        for ox in (-S,0,S):
            for oy in (-S,0,S):
                if (ox and not(x<120 or x>S-120)) or (oy and not(y<120 or y>S-120)):continue
                q=[(px+ox,py+oy) for px,py in pts]
                for ww,vv in ((w,.62),(w*.62,.8),(w*.3,1.0)):
                    c=int(min(255,v*vv))
                    d.line(q,fill=c,width=max(1,int(ww)),joint='curve')
                    r=ww/2
                    for (px,py) in (q[0],q[-1]):
                        d.ellipse([px-r,py-r,px+r,py+r],fill=c)
    h=np.asarray(im.filter(ImageFilter.GaussianBlur(1.4)),dtype=float)/255
    return h
h=terry()
# normal map (OpenGL, +Y up in texture space)
gx=(np.roll(h,-1,1)-np.roll(h,1,1))/2
gy=(np.roll(h,-1,0)-np.roll(h,1,0))/2
st=7.0
nx,ny,nz=-gx*st,gy*st,np.ones_like(h)
l=np.sqrt(nx**2+ny**2+nz**2);nx/=l;ny/=l;nz/=l
nm=np.stack([(nx+1)/2,(ny+1)/2,(nz+1)/2],-1)
Image.fromarray((nm*255).astype('uint8')).save('terry_normal.jpg',quality=92)
# albedo: valleys darker
hb=np.asarray(Image.fromarray((h*255).astype('uint8')).filter(ImageFilter.GaussianBlur(10)),dtype=float)/255
a=0.40+0.60*np.clip(h,0,1)**1.2
a=a/ a.mean()*0.90
Image.fromarray((np.clip(a,0,1)*255).astype('uint8')).convert('RGB').save('terry_albedo.jpg',quality=92)
Image.fromarray((h*255).astype('uint8')).save('terry_h.png')

# marble
def noise(sc):
    r=rng.random((S//sc+2,S//sc+2))
    return np.asarray(Image.fromarray((r*255).astype('uint8')).resize((S,S),Image.BICUBIC),dtype=float)/255
f=sum(noise(sc)*w for sc,w in ((256,.5),(128,.3),(64,.15),(32,.08)))
f=f/f.max()
yy,xx=np.mgrid[0:S,0:S]/S
def veins(ax,ay,k,warp,off,wid):
    u=(xx*ax+yy*ay)*k+warp*(f-0.4)+off
    d=np.abs((u%1.0)-0.5)
    v=np.exp(-(d/wid)**1.6)
    return np.asarray(Image.fromarray((v*255).astype('uint8')).filter(ImageFilter.GaussianBlur(2.2)),dtype=float)/255
vein=veins(0.8,0.55,1.7,1.1,0.1,0.035)*(0.4+0.6*noise(128))
vein2=veins(-0.5,0.9,2.6,0.9,0.4,0.018)*0.55*(noise(64))
cloud=noise(128)*0.5+noise(48)*0.3
base=np.array([0.955,0.945,0.925])
col=base[None,None,:]*(1-0.10*cloud[...,None])
col=col*(1-0.30*vein[...,None]*np.array([0.9,0.92,0.95]))*(1-0.5*vein2[...,None])
col[...,0]+=0.015*vein[...]; 
Image.fromarray((np.clip(col,0,1)*255).astype('uint8')).save('marble.jpg',quality=92)

# madeira clara (freixo) para o interior das gavetas
g=np.zeros((S,S))
for sc_,w_ in ((1,0.5),(3,0.3),(9,0.2)):
    r=rng.random((S//sc_+2,1))
    col=np.asarray(Image.fromarray((r*255).astype('uint8')).resize((S,S),Image.BICUBIC),dtype=float)/255
    g+=col*w_
fine=rng.random((S,S))*0.12
g=g+fine
g=(g-g.min())/(g.max()-g.min())
base=np.array([0.86,0.76,0.62]);img_=base[None,None,:]*(0.82+0.3*g[...,None])
Image.fromarray((np.clip(img_,0,1)*255).astype('uint8')).save('wood.jpg',quality=90)
