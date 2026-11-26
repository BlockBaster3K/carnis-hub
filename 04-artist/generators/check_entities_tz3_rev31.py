#!/usr/bin/env python3
"""Check emitted GLB UVs, face budgets and explicitly annotated transition rows.
Not a proof that every visible 3-D material boundary is annotated."""
from pathlib import Path
import json,struct,math,io,sys
from collections import Counter
from PIL import Image
D=Path(__file__).resolve().parents[1]/'deliverables/tz3_phase_3_1_rev31'; OLD=D.parent/'tz3_phase_3_1_rev3'
contract={'b017':set('idle walk attack hurt death mask_twitch'.split()),'b018':set('idle walk attack hurt death whip_attack bone_rattle assimilate'.split()),'b019':set('idle walk crawl fuse attack hurt death sac_charge detonate'.split())}
bones={'b017':set('root torso head jaw mask chest_growth arm_left forearm_left arm_right forearm_right leg_left foot_left leg_right foot_right'.split()),'b018':set('root pelvis spine ribcage head jaw rib_left_1 rib_right_1 rib_left_2 rib_right_2 rib_left_3 rib_right_3 sinew_top sinew_mid sinew_bot arm_blade forearm_blade arm_whip whip_seg1 whip_seg2 whip_seg3 leg_left foot_left leg_right foot_right'.split()),'b019':set('root body head jaw sac_left sac_right sac_back leg_1 leg_2 leg_3 leg_4 leg_5 leg_6 tail'.split())}
for id in contract:
 b=(D/(id+'.glb')).read_bytes();magic,ver,length=struct.unpack_from('<4sII',b);assert (magic,ver,length)==(b'glTF',2,len(b))
 jl,typ=struct.unpack_from('<I4s',b,12);assert typ==b'JSON';j=json.loads(b[20:20+jl]);start=20+jl+8
 meta=json.loads((D/(id+'_data.json')).read_text()); W=256 if id=='b018' else 128
 assert {n['name'] for n in j['nodes']}==bones[id] and len(j['nodes'])==len(bones[id])
 assert {a['name'] for a in j['animations']}==contract[id] and 'skins' not in j
 old=json.loads((OLD/(id+'.animation.json')).read_text());new=json.loads((D/(id+'.animation.json')).read_text());assert old==new and set(new['animations'])==contract[id]
 def floats(index, dim):
  a=j['accessors'][index];assert a['componentType']==5126
  view=j['bufferViews'][a['bufferView']];p=start+view.get('byteOffset',0)+a.get('byteOffset',0)
  flat=struct.unpack_from('<'+'f'*(dim*a['count']),b,p);return [flat[i:i+dim] for i in range(0,len(flat),dim)]
 for anim in j['animations']:
  for sm in anim['samplers']:
   time=floats(sm['input'],1);assert all(abs(t[0]-k/20)<1e-5 for k,t in enumerate(time))
   if anim['extras']['loop'] or anim['name'] not in ('death','assimilate'):
    out=j['accessors'][sm['output']];dim={'VEC3':3,'VEC4':4}[out['type']];values=floats(sm['output'],dim)
    assert all(abs(a-b)<1e-5 for a,b in zip(values[0],values[-1])),(id,anim['name'])
 sampler=j['samplers'][0];assert (sampler['minFilter'],sampler['magFilter'])==(9728,9728)
 img=Image.open(D/(id+'.png'));glow=Image.open(D/(id+'_glow.png'));assert img.size==glow.size==(W,W) and img.mode==glow.mode=='RGBA'
 for k,im in enumerate((img,glow)):
  view=j['bufferViews'][j['images'][k]['bufferView']];off=start+view.get('byteOffset',0);embedded_bytes=b[off:off+view['byteLength']];external=(D/(id+('_glow.png' if k else '.png'))).read_bytes();assert embedded_bytes==external
 # Reconstruct UV rectangles from actual TEXCOORD_0 vertex buffers, independently of manifest.
 rects=[];large=0
 for mesh in j['meshes']:
  for p in mesh['primitives']:
   uv=floats(p['attributes']['TEXCOORD_0'],2);pos=floats(p['attributes']['POSITION'],3);assert len(uv)==len(pos) and len(uv)%4==0 and p.get('mode',4)==4
   for a in range(0,len(uv),4):
    quad=uv[a:a+4]; xs=[u*W for u,v in quad];ys=[v*W for u,v in quad]
    x0=round(min(xs)-.5);y0=round(min(ys)-.5);x1=round(max(xs)+.5);y1=round(max(ys)+.5)
    assert 0<=x0<x1<=W and 0<=y0<y1<=W
    w=x1-x0;h=y1-y0;assert w>=8 and h>=8,(id,mesh['name'],w,h)
    v=pos[a:a+4];norm=lambda n:math.sqrt(sum(q*q for q in n));d1=norm([v[1][i]-v[0][i] for i in range(3)]);d2=norm([v[3][i]-v[0][i] for i in range(3)]);area=d1*d2
    if max(d1,d2)>=.25-1e-6 or area>=.045-1e-6:large+=1;assert w>=16 and h>=16,(id,mesh['name'],area,w,h)
    rects.append((x0,y0,x1,y1))
 assert len(rects)==len(meta['uv_layout'])
 pixels=bytearray(W*W); over=0
 for x0,y0,x1,y1 in rects:
  for y in range(y0,y1):
   for x in range(x0,x1):
    p=y*W+x;over+=pixels[p];pixels[p]=1
 assert not over
 vacant=pixels.count(0);assert vacant/(W*W)<=.05
 colors=[];art=set()
 for x0,y0,x1,y1 in rects:
  region=img.crop((x0,y0,x1,y1)); cs={p[:3] for p in region.get_flattened_data() if p[3]};colors.append(len(cs));key=(region.size,region.tobytes());assert key not in art,(id,'identical face artwork');art.add(key)
 assert min(colors)>=3,(id,min(colors))
 samples=meta['transition_samples'];assert samples
 for s in samples:
  actual=['#%02X%02X%02X'%img.getpixel(tuple(x))[:3] for x in s['coords']]
  assert actual==s['colors'],(id,s,actual)
 bbox=meta['rest_bounds'];box=meta['hitbox'];assert -box[0]/2<=bbox[0][0] and bbox[0][1]<=box[0]/2 and 0<=bbox[1][0] and bbox[1][1]<=box[1] and -box[2]/2<=bbox[2][0] and bbox[2][1]<=box[2]/2
 print(f'{id}: UV {len(rects)} faces, overlap={over}, min=8x8, large>=16x16={large}, unassigned={vacant}/{W*W} ({100*vacant/W**2:.3f}%), 3-tone islands={len(colors)}/{len(colors)}, identical face art=0, gradient probes={len(samples)}/{len(samples)}, names+20fps+PNG+pose=OK')
 print(f'{id}: BOUNDARY-COVERAGE NOT PROVEN: {len(samples)} annotated row probes, visible 3-D boundary enumeration not implemented')
