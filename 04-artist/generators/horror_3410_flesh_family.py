#!/usr/bin/env python3
"""Four authored material sources -> candidate tiles. Deterministic; no random.

Experimental staging, never overwrites the 3.4.10 source tree. The four source
quadrants are distinct compositions, not rotates/flips/offsets of one 64px tile.
Moisan periodic-plus-smooth decomposition suppresses join gradients; this is a
numeric aid, not a substitute for inspecting the mixed wall in game.
"""
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
import json,hashlib
R=Path(__file__).resolve().parents[1];M=R/'analysis_horror_3410/materials';O=R/'analysis_horror_3410/candidate_flesh_16';O.mkdir(exist_ok=True)
family={'living_flesh':['living_flesh_master.png','living_flesh_2.png','living_flesh_3.png','living_flesh_master.png'], 'ossified_flesh':['ossified_flesh_master.png','ossified_flesh_2.png','ossified_flesh_master.png','ossified_flesh_2.png'], 'charred_flesh':['charred_flesh_master.png']*4, 'fireproof_flesh':['fireproof_flesh_master.png']*4}
def periodic(a):
 a=a.astype(np.float64) # avoid uint8 wraparound in signed boundary differences
 h,w,_=a.shape;v=np.zeros_like(a,dtype=float);v[0,:,:]+=a[0,:,:]-a[-1,:,:];v[-1,:,:]+=a[-1,:,:]-a[0,:,:];v[:,0,:]+=a[:,0,:]-a[:,-1,:];v[:,-1,:]+=a[:,-1,:]-a[:,0,:]
 yy,xx=np.mgrid[:h,:w];den=2*np.cos(2*np.pi*xx/w)+2*np.cos(2*np.pi*yy/h)-4;den[0,0]=1
 smooth=np.fft.ifft2(np.fft.fft2(v,axes=(0,1))/den[:,:,None],axes=(0,1)).real;smooth-=smooth.mean(axis=(0,1),keepdims=True)
 return np.clip(np.rint(a+smooth),0,255).astype('uint8')
def metrics(img):
 a=np.asarray(img,dtype=float)[:,:,:3];x=np.abs(a[:,1:]-a[:,:-1]).mean();y=np.abs(a[1:]-a[:-1]).mean();sx=np.abs(a[:,0]-a[:,-1]).mean();sy=np.abs(a[0]-a[-1]).mean();return {'edge_x':round(sx,3),'edge_y':round(sy,3),'internal_x':round(x,3),'internal_y':round(y,3),'ratio_x':round(sx/max(x,1e-9),3),'ratio_y':round(sy/max(y,1e-9),3)}
records=[];images={}
for name,filenames in family.items():
 for i,(xx,yy) in enumerate([(0,0),(1,0),(0,1),(1,1)]):
  filename=filenames[i];src=Image.open(M/filename).convert('RGB');w,h=src.size;assert w>=128 and h>=128
  crop=src.crop((xx*w//2,yy*h//2,(xx+1)*w//2,(yy+1)*h//2)).resize((64,64),Image.Resampling.LANCZOS);a=periodic(np.array(crop));out=Image.fromarray(a,'RGB').convert('RGBA');path=O/(f'{name}_{i}.png');out.save(path,optimize=True);images[(name,i)]=out
  records.append({'name':path.name,'dimensions':[64,64],'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'metrics':metrics(out),'source':filename,'source_quadrant':i})
 # Harmonize the outer four pixels of related tiles toward a shared edge profile;
 # preserve most of the authored interior and 35% of each edge's own color.
 # This reduces mixed-variant jumps but does not prove continuity of structures.
 arrays=[np.asarray(images[(name,i)].convert('RGB'),dtype=float).copy() for i in range(4)]
 left=np.mean([v for a in arrays for v in (a[:,0,:],a[:,-1,:])],axis=0)
 top=np.mean([v for a in arrays for v in (a[0,:,:],a[-1,:,:])],axis=0)
 for i,a in enumerate(arrays):
  for k,weight in enumerate((.65,.43,.20,.06)):
   for x in (k,63-k):a[:,x,:]=a[:,x,:]*(1-weight)+left*weight
  for k,weight in enumerate((.65,.43,.20,.06)):
   for y in (k,63-k):a[y,:,:]=a[y,:,:]*(1-weight)+top*weight
  # Keep darks and highlights in warm near-black/near-white ranges, avoiding
  # the explicitly forbidden #000000, #FFFFFF and pure RGB primaries.
  a=np.maximum(a,np.array([8,5,6]));a=np.minimum(a,np.array([248,240,235]))
  out=Image.fromarray(np.rint(a).astype('uint8'),'RGB').convert('RGBA');path=O/(f'{name}_{i}.png');out.save(path,optimize=True);images[(name,i)]=out
  rec=records[-4+i];rec.update({'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'metrics':metrics(out)})
# Montage is an internal comparison and mixed-variant wall, not proof of gameplay.
sheet=Image.new('RGB',(4*256,4*292),(22,18,20));d=ImageDraw.Draw(sheet)
for row,name in enumerate(family):
 for col in range(4):
  im=images[(name,col)].resize((256,256),Image.Resampling.NEAREST);sheet.paste(im,(col*256,row*292+26));d.text((col*256+4,row*292+5),name+' '+str(col),fill='white')
sheet.save(O/'candidate_families.png')
wall=Image.new('RGB',(4*256,4*256),(0,0,0));pattern=[[0,1,2,3],[2,3,0,1],[1,0,3,2],[3,2,1,0]]
for row in range(4):
 for col in range(4):
  tile=images[('living_flesh',pattern[row][col])].resize((256,256),Image.Resampling.NEAREST);wall.paste(tile,(col*256,row*256))
wall.save(O/'living_mixed_wall.png')
(O/'metrics.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
for r in records:print(r['name'],r['metrics'])
