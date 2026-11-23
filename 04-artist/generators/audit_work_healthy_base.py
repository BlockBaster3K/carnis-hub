#!/usr/bin/env python3
"""Material/UV-specific base-off checks on emitted draft GLBs; not Minecraft QA."""
from pathlib import Path
from PIL import Image
import json,struct
D=Path(__file__).resolve().parents[1]/'analysis_rev31'/'work_models'
reds={(139,32,32),(166,48,48),(107,24,24),(184,64,64),(208,80,80),(122,48,64),(192,64,80),(255,64,64),(255,96,64)}
for ident in ('b017','b018','b019'):
 b=(D/(ident+'.glb')).read_bytes();n=struct.unpack_from('<I',b,12)[0];j=json.loads(b[20:20+n]);start=28+n;img=Image.open(D/(ident+'.png')).convert('RGBA');W=img.width;nodes={n['name']:n for n in j['nodes']};mats=[m['name'] for m in j['materials']]
 def uv(idx):
  a=j['accessors'][idx];v=j['bufferViews'][a['bufferView']];flat=struct.unpack_from('<'+'f'*(2*a['count']),b,start+v.get('byteOffset',0)+a.get('byteOffset',0));return [(flat[i],flat[i+1]) for i in range(0,len(flat),2)]
 def regions(bone):
  node=nodes[bone];mesh=j['meshes'][node['mesh']];out=[]
  for prim in mesh['primitives']:
   if mats[prim['material']]!='healthy_base':continue
   data=uv(prim['attributes']['TEXCOORD_0'])
   for i in range(0,len(data),4):
    q=data[i:i+4];x0=round(min(u for u,v in q)*W-.5);x1=round(max(u for u,v in q)*W+.5);y0=round(min(v for u,v in q)*W-.5);y1=round(max(v for u,v in q)*W+.5);out.append(img.crop((x0,y0,x1,y1)))
  return out
 if ident=='b017':
  faces=regions('head');assert len(faces)==6;front=faces[0];dark=sum(1 for c in front.get_flattened_data() if c[:3]==(26,15,15)); print(ident,'head healthy_base front dark eye texels',dark,'PASS' if dark>=2 else 'FAIL');assert dark>=2
 if ident=='b019':
  for i in range(1,7):
   faces=regions('leg_'+str(i));assert len(faces)==12 # main leg plus hip connector
   red=sum(1 for f in faces for c in f.get_flattened_data() if c[3] and c[:3] in reds)
   print(ident,'leg_'+str(i),'base infected red texels',red,'PASS' if red==0 else 'FAIL');assert red==0
print('Scope: actual GLB UV/material and color membership; not a test of complete silhouette or in-game behavior.')
