#!/usr/bin/env python3
"""Conservative intra-island scan for ordered semantic runs with intermediate pixels.
Checks both orthogonal directions; does not include inter-cuboid intersections or
oblique boundaries and cannot prove every visible boundary is covered.
"""
from pathlib import Path
from PIL import Image
from collections import Counter
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent));import entities_tz3_rev31_work as E
D=E.OUT
families={'skin':('skin','skin_dark','skin_light'), 'flesh':('flesh','flesh_dark','flesh_light','vein','vein_light','fluid','fluid_light'), 'bone':('bone','bone_light','bone_dark','bone_crack'), 'cartilage':('cartilage','cartilage_dark'), 'cloth':('shirt','shirt_dark','shirt_light','pants','pants_dark','pants_light')}
cats={E.C(c)[:3]:kind for kind,ks in families.items() for c in ks}
pairs={frozenset(('skin','flesh')):('skin_mid','skin_flesh','wound_mid'),frozenset(('bone','cartilage')):('bone_cart_mid1','bone_cart_mid2'),frozenset(('skin','cloth')):('cloth_mid1','cloth_mid2')};middle={k:{E.C(c)[:3] for c in v} for k,v in pairs.items()}
for id in ('b017','b018','b019'):
 meta=json.loads((D/(id+'_data.json')).read_text());im=Image.open(D/(id+'.png')).convert('RGBA');items=[]
 for f in meta['uv_layout']:
  x,y,w,h=f['rect']
  # One pass left→right and one top→bottom; reverse pairs are naturally included.
  seqs=([[(x+u,y+v) for u in range(w)] for v in range(h)]+[[(x+u,y+v) for v in range(h)] for u in range(w)])
  for path in seqs:
   cs=[im.getpixel(p) for p in path];i=0
   while i<len(path)-1:
    first=cats.get(cs[i][:3]) if cs[i][3] else None
    if not first:i+=1;continue
    found=False
    for pair,allowed in middle.items():
     if first not in pair:continue
     j=i+1
     while j<len(path) and cs[j][3] and cs[j][:3] in allowed:j+=1
     if j<len(path) and cs[j][3] and cats.get(cs[j][:3]) in pair and cats.get(cs[j][:3])!=first:
      width=j-i-1;items.append({'bone':f['bone'],'cube':f['cube'],'side':f['side'],'style':f['style'],'start':path[i],'end':path[j],'classes':[first,cats[cs[j][:3]]],'bridge_width':width,'tones':[list(cs[k][:3]) for k in range(i,j+1)],'ok':2<=width<=4 and len({cs[k][:3] for k in range(i,j+1)})>=3});found=True
    i+=1
 fails=[r for r in items if not r['ok']];(D/(id+'_intra_face_widths.json')).write_text(json.dumps({'samples':items,'failures':fails},ensure_ascii=False,indent=2))
 print(id,'orthogonal semantic runs',len(items),'valid',len(items)-len(fails),'failed',len(fails),'widths',dict(Counter(v['bridge_width'] for v in items)))
 for r in fails[:3]:print(' ',r)
print('Not exhaustive for all visible boundaries: no oblique paths or interactions between distinct cuboids.')
