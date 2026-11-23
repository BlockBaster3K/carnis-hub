#!/usr/bin/env python3
"""Orthographic rest-pose preview, six textured cuboid faces, software rasterizer."""
from pathlib import Path
import sys,math, cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,str(Path(__file__).resolve().parent));import entities_tz3 as e
models=[e.humanoid('b017'),e.humanoid('b018'),e.creeper()]
W,H=420,740; scale=290
try: font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20)
except: font=ImageFont.load_default()
canvas=Image.new('RGB',(W*3,H),(23,17,19))
for mi,m in enumerate(models):
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
 camera=np.array([.37,.12,1.]); camera=camera/np.linalg.norm(camera)
 right=np.array([camera[2],0,-camera[0]]);right/=np.linalg.norm(right)
 up=np.cross(camera,right);up/=np.linalg.norm(up)
 def project(v):return [W/2+np.dot(v,right)*scale, H-95-np.dot(v,up)*scale]
 faces=[]
 for node in m.nodes:
  mat=mats[m.byname[node['name']]];piv=node['pivot']
  for center,size,style,var,face,glow in node['cubes']:
   x,y,z=[center[i]-piv[i] for i in range(3)];a,b,c=[v/2 for v in size]
   fs=[('front',(0,0,1),[(x-a,y-b,z+c),(x+a,y-b,z+c),(x+a,y+b,z+c),(x-a,y+b,z+c)]),('back',(0,0,-1),[(x+a,y-b,z-c),(x-a,y-b,z-c),(x-a,y+b,z-c),(x+a,y+b,z-c)]),('right',(1,0,0),[(x+a,y-b,z+c),(x+a,y-b,z-c),(x+a,y+b,z-c),(x+a,y+b,z+c)]),('left',(-1,0,0),[(x-a,y-b,z-c),(x-a,y-b,z+c),(x-a,y+b,z+c),(x-a,y+b,z-c)]),('top',(0,1,0),[(x-a,y+b,z+c),(x+a,y+b,z+c),(x+a,y+b,z-c),(x-a,y+b,z-c)]),('bottom',(0,-1,0),[(x-a,y-b,z-c),(x+a,y-b,z-c),(x+a,y-b,z+c),(x-a,y-b,z+c)])]
   for side,normal,vertices in fs:
    n=mat[:3,:3]@normal
    if np.dot(n,camera)<=0:continue
    vv=[p3(v,mat) for v in vertices];score=np.dot(sum(vv)/4,camera)
    light=glow and (side=='front' or style in ('sac','sinew'));textureface=face if side=='front' else 'side'
    tile=m.atlas.tile(style,var,textureface,light);xx=(tile%8)*8;yy=(tile//8)*8
    texture=np.array(m.atlas.base.crop((xx,yy,xx+8,yy+8)))
    fw,fh=((size[0],size[1]) if side in ('front','back') else (size[2],size[1]) if side in ('left','right') else (size[0],size[2])); faces.append((score,vv,texture,side,fw,fh))
 img=np.zeros((H,W,4),dtype=np.uint8);img[:,:,:]=[23,17,19,255]
 for _,vv,texture,side,fw,fh in sorted(faces,key=lambda x:x[0]):
  # matches export's UV: bottom-left,bottom-right,top-right,top-left
  factor=max(fw,fh);u=3.5*fw/factor;v=3.5*fh/factor;src=np.float32([[3.5-u,3.5+v],[3.5+u,3.5+v],[3.5+u,3.5-v],[3.5-u,3.5-v]]);dst=np.float32([project(v) for v in vv]);M=cv2.getPerspectiveTransform(src,dst)
  tex=texture.copy();factor=.85 if side=='right' else 1.0 if side=='front' else .96;tex[:,:,:3]=(tex[:,:,:3].astype(float)*factor).astype('uint8')
  war=cv2.warpPerspective(tex,M,(W,H),flags=cv2.INTER_NEAREST,borderMode=cv2.BORDER_CONSTANT,borderValue=(0,0,0,0));mask=np.zeros((H,W),dtype=np.uint8); cv2.fillConvexPoly(mask,np.rint(dst).astype('int32'),255); a=(war[:,:,3:4].astype(float)/255)*(mask[:,:,None]/255)
  img[:,:,:3]=(war[:,:,:3]*a+img[:,:,:3]*(1-a)).astype('uint8')
 out=Image.fromarray(img).convert('RGB');d=ImageDraw.Draw(out);d.text((18,15),m.id.upper()+' · '+m.label,font=font,fill='#E8C5C0');d.text((18,H-47),'Ортографический вид · поза покоя',font=font,fill='#C9A9A4')
 canvas.paste(out,(mi*W,0))
canvas.save(e.OUT/'preview_models.png')
