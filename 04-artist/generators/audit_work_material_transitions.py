#!/usr/bin/env python3
"""Find raw direct skin/flesh, bone/cartilage, cloth/skin transitions in all UV islands.
Conservative: includes hidden UV surfaces, detects only direct 4-neighbour contacts
inside an island. Does NOT yet enumerate occlusion-created contacts between cubes or
all bridges of invalid width. This is a diagnostic, not a complete boundary proof.
"""
from pathlib import Path
from PIL import Image
from collections import Counter
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent));import entities_tz3_rev31_work as E
D=E.OUT
cats={
 'skin':('skin','skin_dark','skin_light'),
 'flesh':('flesh','flesh_dark','flesh_light','vein','vein_light','fluid','fluid_light'),
 'bone':('bone','bone_light','bone_dark','bone_crack'),
 'cartilage':('cartilage','cartilage_dark'),
 'cloth':('shirt','shirt_dark','shirt_light','pants','pants_dark','pants_light'),
}
lookup={}
for category,keys in cats.items():
 for k in keys:
  col=E.C(k)[:3];assert col not in lookup;lookup[col]=category
pairs={frozenset(('skin','flesh')),frozenset(('bone','cartilage')),frozenset(('cloth','skin'))}
for ident in ('b017','b018','b019'):
 meta=json.loads((D/(ident+'_data.json')).read_text());im=Image.open(D/(ident+'.png')).convert('RGBA');errors=[]
 for f in meta['uv_layout']:
  x,y,w,h=f['rect']
  for yy in range(y,y+h):
   for xx in range(x,x+w):
    a=im.getpixel((xx,yy));ca=lookup.get(a[:3]) if a[3] else None
    if not ca:continue
    for dx,dy in ((1,0),(0,1)):
     nx,ny=xx+dx,yy+dy
     if nx>=x+w or ny>=y+h:continue
     b=im.getpixel((nx,ny));cb=lookup.get(b[:3]) if b[3] else None
     if ca!=cb and frozenset((ca,cb)) in pairs:
      errors.append({'bone':f['bone'],'cube':f['cube'],'side':f['side'],'style':f['style'],'a':[xx,yy,*a],'b':[nx,ny,*b],'classes':[ca,cb]})
 out=D/(ident+'_raw_contact_candidates.json');out.write_text(json.dumps(errors,ensure_ascii=False,indent=2))
 print(ident,'intra-island direct-contact candidates',len(errors),'pairs',dict(Counter('~'.join(sorted(e['classes'])) for e in errors)))
 for err in errors[:3]:print(' ',err)
print('This scan is incomplete: it does not enumerate contacts between surfaces, and it does not validate bridge width 2–4 across every material boundary.')
