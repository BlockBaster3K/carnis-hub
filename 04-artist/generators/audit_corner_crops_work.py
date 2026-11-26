#!/usr/bin/env python3
"""GLB rest-pose close-ups at two three-quarter angles; visual review, not proof."""
from pathlib import Path
import sys,math
import numpy as np
from PIL import Image,ImageDraw
sys.path.insert(0,str(Path(__file__).resolve().parent));import audit_pose_raster_work as P
O=Path(__file__).resolve().parents[1]/'analysis_rev31'/'corner_pose_audit';O.mkdir(exist_ok=True)
groups={'b017':{'head':{'head','jaw','mask'},'torso':{'torso','chest_growth'}},'b018':{'head':{'head','jaw'},'torso':{'pelvis','spine','ribcage','rib_left_1','rib_left_2','rib_left_3','rib_right_1','rib_right_2','rib_right_3','sinew_top','sinew_mid','sinew_bot'}},'b019':{'head':{'head','jaw'},'torso':{'body','sac_left','sac_right','sac_back'}}}
for ident in ('b017','b018','b019'):
 doc,faces,anims=P.scene(ident);mats=P.matrices(doc,[],0)
 canvas=Image.new('RGB',(900,900),(23,17,19));draw=ImageDraw.Draw(canvas)
 for col,phi in enumerate((-math.pi/4,math.pi/4)):
  _,im=P.raster(faces,mats,phi,False,True);im=Image.fromarray(im)
  cam=np.array([math.sin(phi),.12,math.cos(phi)]);cam/=np.linalg.norm(cam);right=np.array([cam[2],0,-cam[0]]);right/=np.linalg.norm(right);up=np.cross(cam,right)
  allv=np.concatenate([(mats[f['node']]@f['points'].T).T[:,:3] for f in faces]);r=allv@right;u=allv@up;hr0=(r.min()+r.max())/2;vr0=(u.min()+u.max())/2
  for row,(name,names) in enumerate(groups[ident].items()):
   vv=np.concatenate([(mats[f['node']]@f['points'].T).T[:,:3] for f in faces if f['name'] in names]);xs=P.W/2+(vv@right-hr0)*P.S;ys=P.H/2-(vv@up-vr0)*P.S
   box=(max(0,int(xs.min())-10),max(0,int(ys.min())-10),min(P.W,int(xs.max())+11),min(P.H,int(ys.max())+11));crop=im.crop(box);scale=min(420/crop.width,390/crop.height);crop=crop.resize((max(1,round(crop.width*scale)),max(1,round(crop.height*scale))),Image.Resampling.NEAREST)
   canvas.paste(crop,(col*450+(450-crop.width)//2,row*450+36+(390-crop.height)//2));draw.text((col*450+12,row*450+10),ident+' '+name+' '+('-45' if col==0 else '+45'),fill='#E8C5C0')
 canvas.save(O/(ident+'_corners.png'));print(ident,'corner crops rendered; inspect continuity and visibility manually')
