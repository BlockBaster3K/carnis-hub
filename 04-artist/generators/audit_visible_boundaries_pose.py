#!/usr/bin/env python3
"""Partial raster inventory of potential visible direct-material boundaries.
Actual emitted GLB, every 20-fps animation key, four azimuths, one elevation.
Pixel ownership and source RGB via z-buffer, nearest sampling. A close depth
threshold filters distant projected overlap but does not prove geometric contact.
No claims about intermediate animation times, all angles, hidden/transparent
layers, oblique normal width, subpixel features, or Minecraft renderer.
"""
from pathlib import Path
import sys,json,math
from collections import Counter
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
import audit_pose_raster_work as P
import entities_tz3_rev31_work as E

OUT=Path(__file__).resolve().parents[1]/'analysis_rev31'/'pose_boundary_candidates';OUT.mkdir(exist_ok=True)
families={'skin':('skin','skin_dark','skin_light'),'flesh':('flesh','flesh_dark','flesh_light','vein','vein_light','fluid','fluid_light'),'bone':('bone','bone_light','bone_dark','bone_crack'),'cartilage':('cartilage','cartilage_dark'),'cloth':('shirt','shirt_dark','shirt_light','pants','pants_dark','pants_light')}
labels=['none']+list(families)
lut=np.zeros(256**3,dtype=np.uint8)
for n,(label,keys) in enumerate(families.items(),1):
 for k in keys:
  r,g,b=E.C(k)[:3];lut[(r<<16)|(g<<8)|b]=n
pairs={(1,2),(3,4),(1,5)}
def source_rgb(rgb,y,x):return [int(c) for c in rgb[y,x]]
for ident in (sys.argv[1:] or ('b017','b018','b019')):
 if ident not in ('b017','b018','b019'):raise ValueError(ident)
 doc,faces,anims=P.scene(ident);grouped={};observations=Counter();frames=0
 for anim,tracks in anims.items():
  duration=max(float(ts[-1]) for _,_,ts,_ in tracks);steps=round(duration*20)
  for frame in range(steps+1):
   t=frame/20;mats=P.matrices(doc,tracks,t)
   for view,phi in enumerate((0,math.pi/4,math.pi/2,math.pi*3/4)):
    _,_,owner,depth,rgb=P.raster(faces,mats,phi,False,False,True);frames+=1
    rgb=rgb.astype(np.uint32);cat=lut[(rgb[:,:,0]<<16)|(rgb[:,:,1]<<8)|rgb[:,:,2]]
    for dy,dx in ((0,1),(1,0)):
     a=owner[:P.H-dy,:P.W-dx];b=owner[dy:,dx:];ca=cat[:P.H-dy,:P.W-dx];cb=cat[dy:,dx:];za=depth[:P.H-dy,:P.W-dx];zb=depth[dy:,dx:]
     with np.errstate(invalid='ignore'):near=np.abs(za-zb)<=2.0/P.S
     match=np.zeros(a.shape,bool)
     for x,y in pairs:match|=((ca==x)&(cb==y))|((ca==y)&(cb==x))
     ys,xs=np.where((a>=0)&(b>=0)&near&match)
     for y,x in zip(ys,xs):
      fa,fb=int(a[y,x]),int(b[y,x]);u,v=faces[fa],faces[fb];same=(u['node'],u['primitive'],u['cube'])==(v['node'],v['primitive'],v['cube']);k=tuple(sorted((fa,fb)))+tuple(sorted((int(ca[y,x]),int(cb[y,x]))))
      if k not in grouped:
       def desc(f):return {'bone':f['name'],'primitive':f['primitive'],'cube':f['cube'],'side':f['side'],'material':f['material'],'atlas_rect':f['rect']}
       grouped[k]={'face_a':desc(u),'face_b':desc(v),'categories':[labels[int(ca[y,x])],labels[int(cb[y,x])]],'same_cuboid':same,'first':{'clip':anim,'frame':frame,'time':t,'azimuth_deg':view*45,'pixel':[int(x),int(y)],'rgb_a':source_rgb(rgb,y,x),'rgb_b':source_rgb(rgb,y+dy,x+dx),'depth_difference':float(abs(za[y,x]-zb[y,x]))},'observations':0,'sampled_poses':set()}
      rec=grouped[k];rec['observations']+=1;rec['sampled_poses'].add((anim,frame,view));observations['same' if same else 'different']+=1
 for rec in grouped.values():rec['sampled_poses']=len(rec['sampled_poses'])
 records=sorted(grouped.values(),key=lambda r:-r['observations']);report={'entity':ident,'sampling':'all animation keyframes at 20 fps; 0,45,90,135 degrees, elevation approximately 7 degrees; full materials; nearest, alpha>0 treated opaque; 540x560, 230 px/block, centered on each pose; depth difference <=2 screen pixels in model scale','samples':frames,'observations':dict(observations),'candidate_face_pairs':len(records),'different_cuboid_pairs':sum(not r['same_cuboid'] for r in records),'records':records,'scope_limitations':'A candidate is a projected visual adjacency, not necessarily physical contact: depth can differ by <=2/230 blocks. Does not measure transition normal width; does not evaluate transparent layering, 3D occlusion behind frontmost surface, arbitrary view angles, continuous times between animation keys, GPU or Minecraft.'}
 (OUT/(ident+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2));print(ident,'poses/views',frames,'candidate groups',len(records),'intercube groups',report['different_cuboid_pairs'],'observations',dict(observations),flush=True)
