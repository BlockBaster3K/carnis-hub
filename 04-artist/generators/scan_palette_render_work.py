#!/usr/bin/env python3
"""Exact palette-and-raster audit of draft PNGs; scope of renderer explained in output.
Writes all exceptional (x,y,RGBA/RGB) points, including an empty list when clean.
"""
from pathlib import Path
from PIL import Image
from collections import Counter
import json,sys,itertools
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent));import entities_tz3_rev31_work as E
D=E.OUT; pal={E.C(k)[:3] for k in E.P}; bg=(23,17,19)
shades={tuple(int(x*f) for x in c) for c in pal for f in (1.0,.85,.96)}
root={tuple(int(x*f) for x in E.C(t)[:3]) for t in ('ground','ground_light','ground_dark') for f in (1.0,.85,.96)}
def blend(fg,bg):
 a=178/255;return tuple(int(fg[i]*a+bg[i]*(1-a)) for i in range(3))
allowed=shades|{bg};level=allowed.copy()
# Repeated alpha blend can occur when several roots overlap in the orthographic view.
for i in range(3):
 level={blend(f,b) for f in root for b in level};allowed.update(level)
for ident in ('b017','b018','b019'):
 data=json.loads((D/(ident+'_data.json')).read_text());img=Image.open(D/(ident+'.png')).convert('RGBA');palette_err=[];root_alphas=Counter();coords=set()
 for f in data['uv_layout']:
  x,y,w,h=f['rect']
  for yy in range(y,y+h):
   for xx in range(x,x+w):
    assert (xx,yy) not in coords;coords.add((xx,yy));c=img.getpixel((xx,yy))
    if c[3] and c[:3] not in pal:palette_err.append({'x':xx,'y':yy,'rgba':list(c),'face':[f['bone'],f['cube'],f['side']]})
    if f['style']=='rootlet':root_alphas[c[3]]+=1
 renders={}
 for mode in ('front','side'):
  render=Image.open(D/(ident+'_'+mode+'.png')).convert('RGB');bad=[];hist=Counter()
  # Exclude title and caption labels, and scan the complete model area, not just a crop.
  for y in range(48,render.height-55):
   for x in range(render.width):
    c=render.getpixel((x,y))
    if c not in allowed:
     bad.append({'x':x,'y':y,'rgb':list(c)});hist[c]+=1
  renders[mode]={'scanned_bounds':[0,48,render.width,render.height-55],'exceptions':bad,'top_exceptions':[(list(c),n) for c,n in hist.most_common(10)]}
 (D/(ident+'_scan_exceptions.json')).write_text(json.dumps({'palette_exception_coordinates':palette_err,'render':renders,'root_alpha_hist':dict(root_alphas)},ensure_ascii=False,indent=2))
 print(ident,'palette exceptions',len(palette_err),'front render exceptions',len(renders['front']['exceptions']),'side render exceptions',len(renders['side']['exceptions']),'root alpha',dict(root_alphas))
 if renders['front']['exceptions']:print('  front examples',renders['front']['exceptions'][:3])
 if renders['side']['exceptions']:print('  side examples',renders['side']['exceptions'][:3])
print('Render model: nearest; factors 1, .85, .96; alpha=178/255 composited over palette or background up to 3 layers. Header/caption excluded. This validates this software renderer, not Minecraft or arbitrary lighting.')
