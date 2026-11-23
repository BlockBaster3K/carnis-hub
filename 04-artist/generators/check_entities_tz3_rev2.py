#!/usr/bin/env python3
"""Независимые структурные проверки GLB/PNG фазы 3.1."""
from pathlib import Path
import json,struct,math,io,sys
from PIL import Image
D=Path(__file__).resolve().parents[1]/'deliverables/tz3_phase_3_1_rev2'
for ident in ['b017','b018','b019']:
 b=(D/(ident+'.glb')).read_bytes();magic,version,length=struct.unpack_from('<4sII',b);assert (magic,version,length)==(b'glTF',2,len(b))
 n,tag=struct.unpack_from('<I4s',b,12);assert tag==b'JSON';j=json.loads(b[20:20+n]);boff=20+n+8
 names=[x.get('name','') for x in j['nodes']];assert all(names) and len(names)==len(set(names))
 meta=json.loads((D/(ident+'_data.json')).read_text());assert names==[x['name'] for x in meta['bones']]
 for ix,suffix in enumerate(['','_glow']):
  im=Image.open(D/(ident+suffix+'.png'));assert im.mode=='RGBA' and im.size==(64,64)
  view=j['bufferViews'][j['images'][ix]['bufferView']];embedded=Image.open(io.BytesIO(b[boff+view.get('byteOffset',0):boff+view.get('byteOffset',0)+view['byteLength']]))
  assert embedded.tobytes()==im.tobytes()
  if suffix=='_glow':assert all(a==255 and (r,g,bl) in [(0,0,0),(255,64,64),(255,96,64)] for r,g,bl,a in im.getdata())
 for anim,spec in zip(j['animations'],meta['animations']):
  assert anim['name']==spec['name'] and anim['channels'];assert abs(anim['extras']['fps']-20)<.001
  for sm in anim['samplers']:
   acc=j['accessors'][sm['input']];view=j['bufferViews'][acc['bufferView']];off=boff+view.get('byteOffset',0)+acc.get('byteOffset',0)
   times=struct.unpack_from('<'+'f'*acc['count'],b,off)
   assert len(times)==round(spec['duration']*20)+1 and abs(times[-1]-spec['duration'])<1e-5
   assert all(abs(t-i/20)<1e-5 for i,t in enumerate(times))
   assert j['accessors'][sm['output']]['count']==len(times)
   if spec['mode']=='loop':
    ao=j['accessors'][sm['output']];vo=j['bufferViews'][ao['bufferView']];off2=boff+vo.get('byteOffset',0)+ao.get('byteOffset',0);dim={'VEC3':3,'VEC4':4}[ao['type']]
    vals=struct.unpack_from('<'+'f'*(len(times)*dim),b,off2);assert all(abs(vals[k]-vals[-dim+k])<1e-5 for k in range(dim)),(ident,anim['name'])
 print(ident, 'OK',len(names),'костей',len(j['animations']),'анимаций')
