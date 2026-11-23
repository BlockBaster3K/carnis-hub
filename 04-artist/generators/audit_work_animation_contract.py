#!/usr/bin/env python3
from pathlib import Path
import json,struct
R=Path(__file__).resolve().parents[1];D=R/'analysis_rev31'/'work_models';P=R/'deliverables'/'tz3_phase_3_1_rev31'
def gl(p):
 b=p.read_bytes();n=struct.unpack_from('<I',b,12)[0];return json.loads(b[20:20+n]),b,28+n
def tracks(p):
 j,b,off=gl(p);out={}
 for anim in j['animations']:
  for c in anim['channels']:
   s=anim['samplers'][c['sampler']];key=(anim['name'],j['nodes'][c['target']['node']]['name'],c['target']['path']);vals=[]
   for idx in [s['input'],s['output']]:
    a=j['accessors'][idx];v=j['bufferViews'][a['bufferView']];i=off+v.get('byteOffset',0)+a.get('byteOffset',0);vals.append(b[i:i+v['byteLength']])
   out[key]=vals
 return j,out
for id in ('b017','b018','b019'):
 ja,a=tracks(P/(id+'.glb'));jb,b=tracks(D/(id+'.glb'));delta=[k for k in a if a[k]!=b.get(k)];json_equal=(P/(id+'.animation.json')).read_bytes()==(D/(id+'.animation.json')).read_bytes();same=a.keys()==b.keys() and not delta
 print(id,'GLB animation channel buffers identical',same,'changed channels',len(delta),'animation JSON bytes identical',json_equal);assert same and json_equal
 if id=='b019':
  old={n['name']:n.get('translation') for n in ja['nodes']};new={n['name']:n.get('translation') for n in jb['nodes']};moved=[n for n in old if any(abs(a-b)>1e-7 for a,b in zip(old[n],new[n]))];print('  changed local rest translations:',moved,'(six leg pivots follow staged leg geometry; descendants may compensate parent offsets)')
print('Scope: key buffers, channel labels and separate JSON; does not establish GeckoLib runtime integration.')
