#!/usr/bin/env python3
"""Rasterize actual exported GLB poses at keyframes. Work-in-progress audit only.

Twenty-FPS sampled poses and 4 azimuths; measures per-bone projected pixel
ownership, separately for all materials and healthy-only. Transparent surfaces
are treated as opaque for ownership; boundaries, all angles and intermediate
frames are NOT proven by this tool. No Minecraft/GeckoLib simulation.
"""
from pathlib import Path
from collections import Counter
import json, struct, math, sys
import numpy as np
import cv2
from PIL import Image, ImageDraw

D=Path(__file__).resolve().parents[1]/'analysis_rev31'/'work_models'
O=Path(__file__).resolve().parents[1]/'analysis_rev31'/'pose_audit';O.mkdir(exist_ok=True)
W,H,S=540,560,230
SIDES=['front','back','right','left','top','bottom']

def scene(ident):
 raw=(D/(ident+'.glb')).read_bytes();n=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+n]);start=28+n
 def access(i):
  a=doc['accessors'][i];v=doc['bufferViews'][a['bufferView']];d={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];assert a['componentType']==5126
  return np.frombuffer(raw,dtype='<f4',count=d*a['count'],offset=start+v.get('byteOffset',0)+a.get('byteOffset',0)).reshape((-1,d)).copy()
 im=np.asarray(Image.open(D/(ident+'.png')).convert('RGBA'))
 faces=[]
 for ni,node in enumerate(doc['nodes']):
  if 'mesh' not in node:continue
  for pi,prim in enumerate(doc['meshes'][node['mesh']]['primitives']):
   mat=doc['materials'][prim['material']]['name'];pts=access(prim['attributes']['POSITION']);uv=access(prim['attributes']['TEXCOORD_0']);assert len(pts)%24==0
   for off in range(0,len(pts),4):
    tex=uv[off:off+4];x0=round(float(tex[:,0].min())*im.shape[1]-.5);x1=round(float(tex[:,0].max())*im.shape[1]+.5);y0=round(float(tex[:,1].min())*im.shape[0]-.5);y1=round(float(tex[:,1].max())*im.shape[0]+.5)
    p=pts[off:off+4];e1=p[1]-p[0];e2=p[3]-p[0];nn=np.cross(e1,e2);nn/=np.linalg.norm(nn)
    faces.append({'node':ni,'name':node['name'],'primitive':pi,'cube':off//24,'material':mat,'side':SIDES[(off%24)//4],'rect':[x0,y0,x1-x0,y1-y0],'points':np.c_[p,np.ones(4)],'normal':nn,'texture':im[y0:y1,x0:x1].copy()})
 animations={}
 for anim in doc['animations']:
  tracks=[]
  for channel in anim['channels']:
   s=anim['samplers'][channel['sampler']];assert s.get('interpolation','LINEAR')=='LINEAR';tracks.append((channel['target']['node'],channel['target']['path'],access(s['input']).ravel(),access(s['output'])))
  animations[anim['name']]=tracks
 return doc,faces,animations

def trs(t,q,s):
 x,y,z,w=q;R=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]],float)
 M=np.eye(4);M[:3,:3]=R@np.diag(s);M[:3,3]=t;return M

def matrices(doc,tracks,t):
 nodes=doc['nodes'];values=[{'translation':n.get('translation',[0,0,0]),'rotation':n.get('rotation',[0,0,0,1]),'scale':n.get('scale',[1,1,1])} for n in nodes]
 for i,path,ts,vs in tracks:
  k=int(np.searchsorted(ts,t,side='right'))
  if k==0:v=vs[0]
  elif k>=len(ts):v=vs[-1]
  else:
   a,b=vs[k-1],vs[k];f=(t-ts[k-1])/(ts[k]-ts[k-1]);
   if path=='rotation':
    dot=float(np.dot(a,b));b=-b if dot<0 else b;dot=abs(dot)
    if dot<.9995:
     th=math.acos(min(1.,dot));v=(math.sin((1-f)*th)*a+math.sin(f*th)*b)/math.sin(th)
    else:v=a*(1-f)+b*f;v/=np.linalg.norm(v)
   else:v=a*(1-f)+b*f
  values[i][path]=v
 parents={child:i for i,n in enumerate(nodes) for child in n.get('children',[])};world={}
 def matrix(i):
  if i not in world:
   x=values[i];world[i]=(matrix(parents[i]) if i in parents else np.eye(4))@trs(x['translation'],x['rotation'],x['scale'])
  return world[i]
 return [matrix(i) for i in range(len(nodes))]

def raster(faces,mats,phi,healthy=False,image=False,detail=False):
 cam=np.array([math.sin(phi),.12,math.cos(phi)]);cam/=np.linalg.norm(cam);right=np.array([cam[2],0,-cam[0]]);right/=np.linalg.norm(right);up=np.cross(cam,right)
 # Fit the projected pose by panning, not by scaling. The previous fixed camera
 # cropped death frames and made the leg-visibility count unreliable.
 vv_all=np.concatenate([(mats[f['node']]@f['points'].T).T[:,:3] for f in faces]);hr=vv_all@right;vr=vv_all@up;hr0=(hr.min()+hr.max())/2;vr0=(vr.min()+vr.max())/2
 if (hr.max()-hr.min())*S>W-8 or (vr.max()-vr.min())*S>H-8:raise ValueError('pose exceeds raster frame; must not silently crop')
 depth=np.full((H,W),-np.inf,dtype=np.float32);owner=np.full((H,W),-1,np.int16);out=np.zeros((H,W,3),np.uint8);out[:]=[23,17,19]
 source=np.zeros((H,W,3),np.uint8) if detail else None
 for i,f in enumerate(faces):
  if healthy and f['material']!='healthy_base':continue
  mat=mats[f['node']];normal=np.linalg.inv(mat[:3,:3]).T@f['normal']
  if normal@cam<=0:continue
  vv=(mat@f['points'].T).T[:,:3];dst=np.array([[W/2+(v@right-hr0)*S,H/2-(v@up-vr0)*S] for v in vv],dtype=np.float32)
  xmin=max(0,int(np.floor(dst[:,0].min()))-1);xmax=min(W,int(np.ceil(dst[:,0].max()))+2);ymin=max(0,int(np.floor(dst[:,1].min()))-1);ymax=min(H,int(np.ceil(dst[:,1].max()))+2)
  if xmin>=xmax or ymin>=ymax:continue
  dest=dst-np.array([xmin,ymin],dtype=np.float32);tex=f['texture'];hh,ww=tex.shape[:2];src=np.float32([[0,hh-1],[ww-1,hh-1],[ww-1,0],[0,0]]);M=cv2.getPerspectiveTransform(src,dest);shape=(xmax-xmin,ymax-ymin)
  warped=cv2.warpPerspective(tex,M,shape,flags=cv2.INTER_NEAREST);mask=np.zeros((shape[1],shape[0]),np.uint8);cv2.fillConvexPoly(mask,np.rint(dest).astype(np.int32),255)
  coeff=np.linalg.lstsq(np.column_stack((dst,np.ones(4))),vv@cam,rcond=None)[0];gy,gx=np.mgrid[ymin:ymax,xmin:xmax];dd=coeff[0]*gx+coeff[1]*gy+coeff[2];window=depth[ymin:ymax,xmin:xmax];valid=(mask>0)&(warped[:,:,3]>0)&(dd>=window-1e-6);window[valid]=dd[valid];owner[ymin:ymax,xmin:xmax][valid]=i
  if detail:source[ymin:ymax,xmin:xmax][valid]=warped[:,:,:3][valid]
  if image:
   factor=.85 if f['side']=='right' else 1 if f['side']=='front' else .96;rgb=(warped[:,:,:3].astype(float)*factor).astype(np.uint8);out[ymin:ymax,xmin:xmax][valid]=rgb[valid]
 counts=Counter()
 ids,n=np.unique(owner[owner>=0],return_counts=True)
 for i,v in zip(ids,n):counts[faces[int(i)]['name']]+=int(v)
 if detail:return counts,out,owner,depth,source
 return counts,out

def main():
 for ident in (sys.argv[1:] or ('b017','b018','b019')):
  if ident not in ('b017','b018','b019'):raise ValueError(ident)
  doc,faces,anims=scene(ident);rows=[];previews=[]
  for aname,tracks in anims.items():
   duration=max(float(ts[-1]) for _,_,ts,_ in tracks);steps=round(duration*20)
   chosen=sorted({0,round(steps*.25),round(steps*.5),round(steps*.75),steps})
   # Sample all animation keyframes and both 45-degree views. Outputs are counts,
   # not a guarantee of leg separability or of visibility from all angles.
   for frame in range(steps+1):
    t=frame/20;mats=matrices(doc,tracks,t)
    for view,phi in [('front45',math.pi/4),('back45',math.pi*3/4)]:
     for healthy in ([False,True] if ident=='b019' else [False]):
      make_image=frame in chosen and view=='front45' and not healthy
      counts,img=raster(faces,mats,phi,healthy,make_image)
      if ident=='b019':
       legs=[counts.get('leg_'+str(i),0) for i in range(1,7)];rows.append({'animation':aname,'frame':frame,'time':t,'view':view,'healthy':healthy,'legs_pixels':legs})
      if make_image and aname in ('idle','walk','attack','death','crawl','assimilate'):
       im=Image.fromarray(img);ImageDraw.Draw(im).text((6,6),f'{ident} {aname} t={t:.2f}',fill='white');previews.append(im)
  if rows:
   failures=[r for r in rows if min(r['legs_pixels'])<20];report={'scope':'20-fps animation keys, two 45-degree azimuths, opaque ownership approximation; <20 pixels is a warning not automatic visual-clarity criterion','samples':len(rows),'low_visibility':len(failures),'low_visibility_examples':failures[:80],'rows':rows};(O/(ident+'_leg_pose_coverage.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2));print(ident,'pose/view/material samples',len(rows),'leg with <20 pixels',len(failures));print('examples',failures[:5])
  if previews:
   cols=5;can=Image.new('RGB',(cols*W,math.ceil(len(previews)/cols)*H),(23,17,19))
   for i,img in enumerate(previews):can.paste(img,((i%cols)*W,(i//cols)*H))
   can.save(O/(ident+'_pose_sheet.png'))
if __name__=='__main__':main()
