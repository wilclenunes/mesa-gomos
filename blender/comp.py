from PIL import Image
import numpy as np,sys
r=Image.open('render.png').convert('RGBA');W,H=r.size
g=np.linspace(0,1,H)[:,None,None]
top=np.array([0xF1,0xEE,0xE9]);bot=np.array([0xDD,0xD5,0xCB])
bg=(top*(1-g)+bot*g)*np.ones((1,W,1));bg=Image.fromarray(bg.astype('uint8')).convert('RGBA')
bg.alpha_composite(r);bg.convert('RGB').save(sys.argv[1])
