#!/usr/bin/env python3
"""Orthographic rest-pose preview, six textured cuboid faces, software rasterizer."""
from pathlib import Path
import sys,math, cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,str(Path(__file__).resolve().parent));import entities_tz3_rev31 as e
e.OUT=Path(__file__).resolve().parents[1]/'analysis_rev31'/'threequarter45'; e.OUT.mkdir(parents=True,exist_ok=True)
base=[e.revise(e.humanoid('b017')),e.revise(e.humanoid('b018')),e.revise(e.creeper())]
for m in base:e.fit_rest(m)
models=base+base
W,H=420,740; scale=290
try: font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20)
except: font=ImageFont.load_default()
canvas=Image.new('RGB',(W*3,H*2),(23,17,19))
for mi,m in enumerate(models):
 scale=290
 e.export(m)
 mats=[]
 for node in m.nodes:
  par=mats[m.byname[node['parent']]] if node['parent'] else np.eye(4)
  pivot=np.array(node['pivot']);p=np.array(m.nodes[m.byname[node['parent']]]['pivot']) if node['parent'] else np.zeros(3)
  roll={'arm_left':.14,'arm_right':-.14,'arm_blade':-.14,'arm_whip':.14}.get(node['name'],0)
  c,s=math.cos(roll),math.sin(roll); local=np.array([[c,-s,0,pivot[0]-p[0]],[s,c,0,pivot[1]-p[1]],[0,0,1,pivot[2]-p[2]],[0,0,0,1]])
  mats.append(par@local)
 def p3(xyz,mat):
  return (mat@np.array([*xyz,1.]))[:3]
 # camera from positive Z and positive X, plus modest elevation
 camera=np.array([1.,.12,1.] if mi<3 else [1.,.12,.03]); camera=camera/np.linalg.norm(camera)
 right=np.array([camera[2],0,-camera[0]]);right/=np.linalg.norm(right)
 up=np.cross(camera,right);up/=np.linalg.norm(up)
 def project(v):return [W/2+np.dot(v,right)*scale, H-95-np.dot(v,up)*scale]
 faces=[]
 for node in m.nodes:
  mat=mats[m.byname[node['name']]];piv=node['pivot']
  for ci,(center,size,style,var,face,glow) in enumerate(node['cubes']):
   x,y,z=[center[i]-piv[i] for i in range(3)];a,b,c=[v/2 for v in size]
   fs=[('front',(0,0,1),[(x-a,y-b,z+c),(x+a,y-b,z+c),(x+a,y+b,z+c),(x-a,y+b,z+c)]),('back',(0,0,-1),[(x+a,y-b,z-c),(x-a,y-b,z-c),(x-a,y+b,z-c),(x+a,y+b,z-c)]),('right',(1,0,0),[(x+a,y-b,z+c),(x+a,y-b,z-c),(x+a,y+b,z-c),(x+a,y+b,z+c)]),('left',(-1,0,0),[(x-a,y-b,z-c),(x-a,y-b,z+c),(x-a,y+b,z+c),(x-a,y+b,z-c)]),('top',(0,1,0),[(x-a,y+b,z+c),(x+a,y+b,z+c),(x+a,y+b,z-c),(x-a,y+b,z-c)]),('bottom',(0,-1,0),[(x-a,y-b,z-c),(x+a,y-b,z-c),(x+a,y-b,z+c),(x-a,y-b,z+c)])]
   for side,normal,vertices in fs:
    n=mat[:3,:3]@normal
    if np.dot(n,camera)<=0:continue
    vv=[p3(v,mat) for v in vertices];score=np.dot(sum(vv)/4,camera)
    light=glow and (side=='front' or style in ('sac','sinew'));textureface=face if side=='front' else 'side'
    f=m.atlas.lookup[(node['name'],ci,side)];xx,yy,ww,hh=f['rect']
    texture=np.array(m.atlas.base.crop((xx,yy,xx+ww,yy+hh)))
    fw,fh=((size[0],size[1]) if side in ('front','back') else (size[2],size[1]) if side in ('left','right') else (size[0],size[2])); faces.append((score,vv,texture,side,fw,fh))
 img=np.zeros((H,W,4),dtype=np.uint8);img[:,:,:]=[23,17,19,255]
 depthbuf=np.full((H,W),-np.inf,dtype=np.float32); gy,gx=np.mgrid[0:H,0:W]
 for _,vv,texture,side,fw,fh in sorted(faces,key=lambda x:x[0]):
  # matches export's UV: bottom-left,bottom-right,top-right,top-left
  hh,ww=texture.shape[:2];src=np.float32([[0,hh-1],[ww-1,hh-1],[ww-1,0],[0,0]]);dst=np.float32([project(v) for v in vv]);M=cv2.getPerspectiveTransform(src,dst)
  tex=texture.copy();factor=.85 if side=='right' else 1.0 if side=='front' else .96;tex[:,:,:3]=(tex[:,:,:3].astype(float)*factor).astype('uint8')
  war=cv2.warpPerspective(tex,M,(W,H),flags=cv2.INTER_NEAREST,borderMode=cv2.BORDER_CONSTANT,borderValue=(0,0,0,0));mask=np.zeros((H,W),dtype=np.uint8); cv2.fillConvexPoly(mask,np.rint(dst).astype('int32'),255); depths=np.array([np.dot(v,camera) for v in vv]); plane=np.linalg.lstsq(np.column_stack((dst,np.ones(4))),depths,rcond=None)[0]; depth=plane[0]*gx+plane[1]*gy+plane[2]; visible=(mask>0)&(depth>=depthbuf-1e-6)&(war[:,:,3]>0); a=(war[:,:,3:4].astype(float)/255)*visible[:,:,None]; depthbuf[visible]=depth[visible]
  img[:,:,:3]=(war[:,:,:3]*a+img[:,:,:3]*(1-a)).astype('uint8')
 out=Image.fromarray(img).convert('RGB');d=ImageDraw.Draw(out);d.text((18,15),m.id.upper()+' · '+m.label,font=font,fill='#E8C5C0');d.text((18,H-47),'Три четверти 45°' if mi<3 else 'Профиль / шесть лап' if mi==5 else 'Профиль',font=font,fill='#C9A9A4')
 out.save(e.OUT/(m.id+('_front.png' if mi<3 else '_side.png')))
 canvas.paste(out,((mi%3)*W,(mi//3)*H))
canvas.save(e.OUT/'preview_models.png')
for m in base:
 m.atlas.base.resize((512,512),Image.Resampling.NEAREST).save(e.OUT/(m.id+'_uv.png'))
