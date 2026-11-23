#!/usr/bin/env python3
"""Rest-pose coplanar face inventory; exact convex overlap area, not visibility.
Positive-area coplanar pairs are z-fighting candidates, including hidden faces.
Shared lines/points are reported separately and must not be called z-fighting.
Transparent texture, visibility and animation-time changes are not resolved.
"""
from pathlib import Path
import json,sys
import numpy as np
import cv2
sys.path.insert(0,str(Path(__file__).resolve().parent))
import audit_pose_raster_work as P
O=Path(__file__).resolve().parents[1]/'analysis_rev31'/'coplanar_audit';O.mkdir(exist_ok=True)
for ident in ('b017','b018','b019'):
 doc,fs,_=P.scene(ident);mats=P.matrices(doc,[],0);faces=[]
 for f in fs:
  mat=mats[f['node']];v=(mat@f['points'].T).T[:,:3];e1=v[1]-v[0];e2=v[3]-v[0];u=e1/np.linalg.norm(e1);w=e2/np.linalg.norm(e2);n=np.cross(u,w);faces.append({**f,'v':v,'n':n,'u':u,'w':w,'lo':v.min(axis=0),'hi':v.max(axis=0)})
 records=[]
 for i,a in enumerate(faces):
  for b in faces[i+1:]:
   if (a['node'],a['primitive'],a['cube'])==(b['node'],b['primitive'],b['cube']):continue
   if np.any(a['hi']<b['lo']-1e-6) or np.any(b['hi']<a['lo']-1e-6):continue
   dot=float(a['n']@b['n'])
   if abs(abs(dot)-1)>1e-6 or abs(a['n']@(b['v'][0]-a['v'][0]))>1e-6:continue
   origin=a['v'][0]
   def poly(f):return np.array([[(v-origin)@a['u'],(v-origin)@a['w']] for v in f['v']],dtype=np.float32)
   aa=poly(a);bb=poly(b);area,polyout=cv2.intersectConvexConvex(aa,bb,handleNested=True)
   # AABBs may touch while rotated actual rectangles do not; record as unresolved
   # if zero area and projected bounding boxes overlap, not as an exact edge.
   overlap=all(max(aa[:,k])>=min(bb[:,k])-1e-6 and max(bb[:,k])>=min(aa[:,k])-1e-6 for k in (0,1))
   if not overlap:continue
   def desc(f):return {'bone':f['name'],'primitive':f['primitive'],'cube':f['cube'],'side':f['side'],'material':f['material'],'rect':f['rect']}
   records.append({'a':desc(a),'b':desc(b),'area_blocks2':float(area),'classification':'positive-area overlap' if area>1e-10 else 'zero-area or projected-only candidate','normal_dot':dot})
 pos=[r for r in records if r['area_blocks2']>1e-10];same=[r for r in pos if r['normal_dot']>0]
 report={'entity':ident,'rest_candidates':len(records),'positive_area':len(pos),'same_facing_positive_area':len(same),'records':records,'scope':'Static exported rest transforms, including hidden faces; positive geometric overlap is not proof of actual visible z-fighting. Areas do not use texture alpha. Zero-area candidates include projected false positives. No animation.'}
 (O/(ident+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2));print(ident,'coplanar candidates',len(records),'positive area',len(pos),'same-facing',len(same))
 for r in same[:8]:print('  ',r)
