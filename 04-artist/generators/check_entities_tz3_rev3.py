#!/usr/bin/env python3
"""Структурный контроль контракта rev3. Визуальная оценка сюда не входит."""
from pathlib import Path
from collections import defaultdict
import json,struct,io,math,sys
from PIL import Image
D=Path(__file__).resolve().parents[1]/'deliverables/tz3_phase_3_1_rev3'
contract={'b017':['idle','walk','attack','hurt','death','mask_twitch'],
'b018':['idle','walk','attack','hurt','death','whip_attack','bone_rattle','assimilate'],
'b019':['idle','walk','crawl','fuse','attack','hurt','death','sac_charge','detonate']}
expected_bones={
'b017':'root torso head jaw mask chest_growth arm_left forearm_left arm_right forearm_right leg_left foot_left leg_right foot_right'.split(),
'b018':'root pelvis spine ribcage head jaw rib_left_1 rib_right_1 rib_left_2 rib_right_2 rib_left_3 rib_right_3 sinew_top sinew_mid sinew_bot arm_blade forearm_blade arm_whip whip_seg1 whip_seg2 whip_seg3 leg_left foot_left leg_right foot_right'.split(),
'b019':'root body head jaw sac_left sac_right sac_back leg_1 leg_2 leg_3 leg_4 leg_5 leg_6 tail'.split()}
for ident in contract:
 b=(D/(ident+'.glb')).read_bytes();magic,version,length=struct.unpack_from('<4sII',b);assert (magic,version,length)==(b'glTF',2,len(b))
 n,tag=struct.unpack_from('<I4s',b,12);assert tag==b'JSON';j=json.loads(b[20:20+n]);boff=20+n+8
 names=[x.get('name','') for x in j['nodes']];assert all(names) and len(names)==len(set(names)) and set(names)==set(expected_bones[ident]),(ident,names)
 assert 'skins' not in j
 assert all(p.get('mode',4)==4 for mesh in j['meshes'] for p in mesh['primitives'])
 assert j['samplers'][0]['minFilter']==9728 and j['samplers'][0]['magFilter']==9728
 meta=json.loads((D/(ident+'_data.json')).read_text());box=meta['hitbox'];bounds=meta['rest_bounds']
 assert bounds[0][0]>=-box[0]/2 and bounds[0][1]<=box[0]/2 and bounds[1][0]>=0 and bounds[1][1]<=box[1] and bounds[2][0]>=-box[2]/2 and bounds[2][1]<=box[2]/2
 for ix,suffix in enumerate(['','_glow']):
  im=Image.open(D/(ident+suffix+'.png'));assert im.mode=='RGBA' and im.size==(64,64)
  view=j['bufferViews'][j['images'][ix]['bufferView']];embedded=Image.open(io.BytesIO(b[boff+view.get('byteOffset',0):boff+view.get('byteOffset',0)+view['byteLength']]))
  assert embedded.tobytes()==im.tobytes()
  if suffix=='_glow':assert all(a==255 and (r,g,bl) in [(0,0,0),(255,64,64),(255,96,64),(208,80,80)] for r,g,bl,a in im.get_flattened_data())
 for suffix in ['_front.png','_side.png','_uv.png']:
  with Image.open(D/(ident+suffix)) as im:assert min(im.size)>=256
 names_json=json.loads((D/(ident+'.animation.json')).read_text());assert 'animations' in names_json and set(names_json['animations'])==set(contract[ident])
 assert set(x['name'] for x in j['animations'])==set(contract[ident])
 by_name={x['name']:x for x in meta['animations']}
 for anim in j['animations']:
  spec=by_name[anim['name']];assert anim['channels'] and anim['extras']['fps']==20
  for sm in anim['samplers']:
   acc=j['accessors'][sm['input']];view=j['bufferViews'][acc['bufferView']];off=boff+view.get('byteOffset',0)+acc.get('byteOffset',0)
   times=struct.unpack_from('<'+'f'*acc['count'],b,off)
   assert len(times)==round(spec['duration']*20)+1 and abs(times[-1]-spec['duration'])<1e-5 and all(abs(t-i/20)<1e-5 for i,t in enumerate(times))
   ao=j['accessors'][sm['output']];assert ao['count']==len(times)
   if spec['mode']=='loop' or anim['name'] not in ('death','assimilate'):
    vo=j['bufferViews'][ao['bufferView']];off2=boff+vo.get('byteOffset',0)+ao.get('byteOffset',0);dim={'VEC3':3,'VEC4':4}[ao['type']]
    vals=struct.unpack_from('<'+'f'*(len(times)*dim),b,off2)
    assert all(abs(vals[k]-vals[-dim+k])<1e-5 for k in range(dim)),(ident,anim['name'])
 # Exact atlas tile equality, a limited proxy, not visual uniqueness of motifs.
 im=Image.open(D/(ident+'.png')); groups=defaultdict(list);mincolors=100
 for i,k in enumerate(meta['tiles']):
  x=i%8*8;y=i//8*8;tile=im.crop((x,y,x+8,y+8));groups[tile.tobytes()].append(k);mincolors=min(mincolors,len(set(tile.get_flattened_data())))
 assert max(map(len,groups.values()))<=2 and mincolors>=3,(ident,mincolors,[x for x in groups.values() if len(x)>2])
 print(ident,'OK',len(names),'bones',len(j['animations']),'animations; 20fps; AABB; PNG; 3+ colors/tile; max equal tiles',max(map(len,groups.values())))
