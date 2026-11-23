#!/usr/bin/env python3
"""Diagnostic only: selected static cuboid-edge UV continuity, rev3 palette.
No assertion that these checks enumerate all visible material boundaries.
"""
from pathlib import Path
from collections import Counter, defaultdict
from PIL import Image
import json,struct,io,math
R=Path(__file__).resolve().parents[1];OLD=R/'deliverables/tz3_phase_3_1_rev3'; NEW=R/'analysis_rev31/work_models'
def parse(path):
 b=path.read_bytes();n=struct.unpack_from('<I',b,12)[0];assert b[16:20]==b'JSON';j=json.loads(b[20:20+n]);start=28+n
 def read(i):
  a=j['accessors'][i];v=j['bufferViews'][a['bufferView']];d={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];assert a['componentType']==5126
  arr=struct.unpack_from('<'+'f'*(d*a['count']),b,start+v.get('byteOffset',0)+a.get('byteOffset',0));return [arr[x:x+d] for x in range(0,len(arr),d)]
 def image(i):
  v=j['bufferViews'][j['images'][i]['bufferView']];return b[start+v.get('byteOffset',0):start+v.get('byteOffset',0)+v['byteLength']]
 return j,read,image

def canonical(p):return tuple(round(c,6) for c in p)
print('=== Q3: original B019 GLB, materials, textures and pixels ===')
j,rd,embedded=parse(OLD/'b019.glb'); raw=embedded(0); im=Image.open(io.BytesIO(raw)).convert('RGBA'); assert raw==(OLD/'b019.png').read_bytes()
used=Counter(p['material'] for mesh in j['meshes'] for p in mesh['primitives']); print('Embedded base PNG == b019.png bytes:',raw==(OLD/'b019.png').read_bytes());print('Original mesh count',len(j['meshes']),'primitive count',sum(used.values()),'size',im.size)
for i,n in sorted(used.items()):
 m=j['materials'][i];ti=m['pbrMetallicRoughness']['baseColorTexture']['index'];source=j['textures'][ti]['source'];print('material:',m['name'],'primitives:',n,'base texture image index:',source,'factor:',m['pbrMetallicRoughness'].get('baseColorFactor',[1,1,1,1]))
pixels=list(im.get_flattened_data());opaque=[p for p in pixels if p[3]>0]; cream=[(x,y,im.getpixel((x,y))) for y in range(im.height) for x in range(im.width) if im.getpixel((x,y))[3]>0 and min(im.getpixel((x,y))[:3])>=110];print('nonzero alpha:',len(opaque),'max rgb:',tuple(max(p[i] for p in opaque) for i in range(3)),'cream-like (all channels >=110):',len(cream))
for c in [(212,200,160,255),(168,152,112,255),(232,220,192,255)]:print('bone palette pixel',c,'count',pixels.count(c))
print('max-min-channel colors:',sorted(Counter(opaque),key=lambda p:min(p[:3]),reverse=True)[:6]);print('Transparency:',dict(Counter(p[3] for p in pixels)))
glowbytes=embedded(1);glow=Image.open(io.BytesIO(glowbytes)).convert('RGBA');gp=list(glow.get_flattened_data());print('Embedded glow PNG == b019_glow.png bytes:',glowbytes==(OLD/'b019_glow.png').read_bytes());print('Glow cream-like pixels (all channels >=110):',sum(min(p[:3])>=110 and p[3]>0 for p in gp))
print('Limit: absent the reference pixels/coordinates for the claimed cream rectangle, its displayed source is not identified.')
print('\n=== ANGLE DIAGNOSTIC: all emitted GLB cuboid edges ===')
for ident in ['b017','b018','b019']:
 j,rd,emb=parse(NEW/(ident+'.glb'));img=Image.open(io.BytesIO(emb(0))).convert('RGBA');W,H=img.size
 target={'b017':{'head_mesh','torso_mesh'},'b018':{'head_mesh','ribcage_mesh'},'b019':{'head_mesh','body_mesh'}}[ident]
 comparisons=[]
 for mesh in j['meshes']:
  # Audit every cuboid, not only head and torso.
  # Occlusion / material-semantics are not resolved by this edge check.
  for pno,p in enumerate(mesh['primitives']):
   pos=rd(p['attributes']['POSITION']);uv=rd(p['attributes']['TEXCOORD_0']);assert len(pos)==len(uv) and len(pos)%24==0
   for first in range(0,len(pos),24):
    edges=defaultdict(list)
    for f in range(6):
     ix=first+f*4
     for v in range(4):
      i=ix+v;k=ix+(v+1)%4;a,b=canonical(pos[i]),canonical(pos[k]);u,vv=uv[i],uv[k]
      if a>b:a,b=b,a;u,vv=vv,u
      edges[(a,b)].append((f,u,vv))
    assert len(edges)==12 and all(len(x)==2 for x in edges.values()),(ident,mesh['name'])
    for edge,((f,u0,u1),(g,v0,v1)) in edges.items():
     length1=max(abs(u1[0]-u0[0])*W,abs(u1[1]-u0[1])*H);length2=max(abs(v1[0]-v0[0])*W,abs(v1[1]-v0[1])*H);n=max(2,round(max(length1,length2))+1)
     def sample(a,b,t):
      x=min(W-1,max(0,math.floor((a[0]*(1-t)+b[0]*t)*W)));y=min(H-1,max(0,math.floor((a[1]*(1-t)+b[1]*t)*H)));return img.getpixel((x,y))
     samples=[(sample(u0,u1,i/(n-1)),sample(v0,v1,i/(n-1))) for i in range(n)];diff=sum(a!=b for a,b in samples)
     comparisons.append((mesh['name'],pno,first//24,f,g,diff,n))
 bad=[x for x in comparisons if x[-2]]
 print(ident,'edge pairs',len(comparisons),'with any mismatch',len(bad),'samples mismatched',sum(x[-2] for x in comparisons),'/',sum(x[-1] for x in comparisons))
 for row in bad[:5]:print('  mesh/primitive/cube/faces/mismatched/total',row)
print('Scope: static corners of all individual cuboids, not an exhaustive inter-cuboid visibility or material-boundary proof; equal texels are necessary but not sufficient to prove motif flow.')

print('\n=== PACKING LOWER BOUND (current working definition of large) ===')
for ident in ['b017','b018','b019']:
 data=json.loads((NEW/(ident+'_data.json')).read_text()); faces=data['uv_layout']; large=sum(x['large'] for x in faces); total=1024 if ident=='b018' else 256; lower=len(faces)+3*large
 print(ident,'8x8 cells:',total,'faces:',len(faces),'large:',large,'minimum assigned:',lower,'spare:',total-lower,'add one 6-face cube (>=6) fits:',total-lower>=6)
print('Lower bound is necessary, not sufficient for rectangle packing; counts change if geometry or definition of large changes.')
