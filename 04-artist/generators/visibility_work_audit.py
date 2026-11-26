#!/usr/bin/env python3
"""Estimate static game-angle face visibility by z-buffer; NOT exhaustive 3D visibility.
Returns projected coverage after occlusion for 16 view angles, and a conservative
large-face budget. alpha > 0 is treated as opaque, so translucent overlap is approximate.
"""
from pathlib import Path
import sys,math,json
import numpy as np,cv2
sys.path.insert(0,str(Path(__file__).resolve().parent)); import entities_tz3_rev31_work as E
OUT=Path(__file__).resolve().parents[1]/'analysis_rev31'/'work_visibility'; OUT.mkdir(exist_ok=True); W,H=260,350;SCALE=155
faceside=['front','back','right','left','top','bottom']

def make(m):
 E.fit_rest(m); atlas=E.FaceAtlas(m);m.atlas=atlas;mats=[]
 for node in m.nodes:
  par=mats[m.byname[node['parent']]] if node['parent'] else np.eye(4); piv=np.array(node['pivot']);pp=np.array(m.nodes[m.byname[node['parent']]]['pivot']) if node['parent'] else np.zeros(3); roll={'arm_left':.14,'arm_right':-.14,'arm_blade':-.14,'arm_whip':.14}.get(node['name'],0.);c,s=math.cos(roll),math.sin(roll)
  mats.append(par@np.array([[c,-s,0,piv[0]-pp[0]],[s,c,0,piv[1]-pp[1]],[0,0,1,piv[2]-pp[2]],[0,0,0,1]]))
 fs=[]
 for node in m.nodes:
  mat=mats[m.byname[node['name']]];piv=node['pivot']
  for ci,(center,size,sty,var,face,glow) in enumerate(node['cubes']):
   x,y,z=[center[i]-piv[i] for i in range(3)];a,b,c=[q/2 for q in size]
   specs=[((0,0,1),[(x-a,y-b,z+c),(x+a,y-b,z+c),(x+a,y+b,z+c),(x-a,y+b,z+c)],size[0]*size[1]),((0,0,-1),[(x+a,y-b,z-c),(x-a,y-b,z-c),(x-a,y+b,z-c),(x+a,y+b,z-c)],size[0]*size[1]),((1,0,0),[(x+a,y-b,z+c),(x+a,y-b,z-c),(x+a,y+b,z-c),(x+a,y+b,z+c)],size[1]*size[2]),((-1,0,0),[(x-a,y-b,z-c),(x-a,y-b,z+c),(x-a,y+b,z+c),(x-a,y+b,z-c)],size[1]*size[2]),((0,1,0),[(x-a,y+b,z+c),(x+a,y+b,z+c),(x+a,y+b,z-c),(x-a,y+b,z-c)],size[0]*size[2]),((0,-1,0),[(x-a,y-b,z-c),(x+a,y-b,z-c),(x+a,y-b,z+c),(x-a,y-b,z+c)],size[0]*size[2])]
   for idx,(n,verts,area) in enumerate(specs):
    rect=atlas.lookup[(node['name'],ci,faceside[idx])]['rect'];xx,yy,w,h=rect;rgba=np.array(atlas.base.crop((xx,yy,xx+w,yy+h)));alpha=rgba[:,:,3]
    vv=np.array([(mat@np.array([*v,1]))[:3] for v in verts]);normal=mat[:3,:3]@n
    fs.append({'node':node['name'],'cube':ci,'side':faceside[idx],'style':sty,'area':area,'v':vv,'n':normal,'alpha':alpha,'rgba':rgba,'max_visible':0,'total_visible':0,'view_45':0})
 families={'skin':('skin','skin_dark','skin_light'),'flesh':('flesh','flesh_dark','flesh_light','vein','vein_light','fluid','fluid_light'),'bone':('bone','bone_light','bone_dark','bone_crack'),'cartilage':('cartilage','cartilage_dark'),'cloth':('shirt','shirt_dark','shirt_light','pants','pants_dark','pants_light')}
 colors={E.C(k)[:3]:i+1 for i,(category,ks) in enumerate(families.items()) for k in ks};classnames=['none']+list(families);compat={(1,2),(3,4),(1,5)};contacts={}
 for view in range(16):
  phi=2*math.pi*(view%8)/8; el=[.10,.36][view//8];camera=np.array([math.sin(phi),el,math.cos(phi)]);camera/=np.linalg.norm(camera);right=np.array([camera[2],0,-camera[0]]);right/=np.linalg.norm(right);up=np.cross(camera,right);up/=np.linalg.norm(up)
  depth=np.full((H,W),-np.inf,dtype=np.float32);which=np.full((H,W),-1,dtype=np.int16);rendered=np.zeros((H,W,3),np.uint8)
  for i,f in enumerate(fs):
   if f['side']=='bottom' or np.dot(f['n'],camera)<=0:continue
   vv=f['v'];dst=np.array([[W/2+v@right*SCALE,H-20-v@up*SCALE] for v in vv],dtype=np.float32);xmin=max(0,int(np.floor(dst[:,0].min()))-1);xmax=min(W,int(np.ceil(dst[:,0].max()))+2);ymin=max(0,int(np.floor(dst[:,1].min()))-1);ymax=min(H,int(np.ceil(dst[:,1].max()))+2)
   if xmin>=xmax or ymin>=ymax:continue
   dest=dst-np.array([xmin,ymin],dtype=np.float32);hh,ww=f['alpha'].shape;src=np.float32([[0,hh-1],[ww-1,hh-1],[ww-1,0],[0,0]]);M=cv2.getPerspectiveTransform(src,dest);shape=(xmax-xmin,ymax-ymin)
   war=cv2.warpPerspective(f['alpha'],M,shape,flags=cv2.INTER_NEAREST);mask=np.zeros((shape[1],shape[0]),np.uint8);cv2.fillConvexPoly(mask,np.rint(dest).astype(np.int32),255)
   ds=vv@camera;coeff=np.linalg.lstsq(np.column_stack((dst,np.ones(4))),ds,rcond=None)[0];gy,gx=np.mgrid[ymin:ymax,xmin:xmax];dd=coeff[0]*gx+coeff[1]*gy+coeff[2];window=depth[ymin:ymax,xmin:xmax];ok=(mask>0)&(war>0)&(dd>=window-1e-6);window[ok]=dd[ok];which[ymin:ymax,xmin:xmax][ok]=i
   rgb=cv2.warpPerspective(f['rgba'][:,:,:3],M,shape,flags=cv2.INTER_NEAREST);rendered[ymin:ymax,xmin:xmax][ok]=rgb[ok]
  label=np.zeros((H,W),np.uint8)
  for col,k in colors.items():label[np.all(rendered==col,axis=2)]=k
  for dy,dx in ((0,1),(1,0)):
   h=H-dy;w=W-dx;a=which[:h,:w];b=which[dy:dy+h,dx:dx+w];ca=label[:h,:w];cb=label[dy:dy+h,dx:dx+w];za=depth[:h,:w];zb=depth[dy:dy+h,dx:dx+w]
   with np.errstate(invalid='ignore'): near=np.abs(za-zb)<.035
   for ca0,cb0 in compat:
    selected=(a>=0)&(b>=0)&(a!=b)&near&(((ca==ca0)&(cb==cb0))|((ca==cb0)&(cb==ca0)))
    ys,xs=np.where(selected)
    for y,x in zip(ys,xs):
     i=int(a[y,x]);j=int(b[y,x]);u=fs[i];v=fs[j]
     if u['node']==v['node'] and u['cube']==v['cube']:continue
     pair=tuple(sorted((i,j)));key=(pair,ca0,cb0)
     if key not in contacts:contacts[key]={'face_a':[u['node'],u['cube'],u['side'],u['style']],'face_b':[v['node'],v['cube'],v['side'],v['style']],'classes':[classnames[ca0],classnames[cb0]],'first_view':view,'first_pixel':[int(x),int(y)],'observations':0}
     contacts[key]['observations']+=1
  counts=np.bincount(which[which>=0],minlength=len(fs))
  for i,num in enumerate(counts):
   f=fs[i];f['max_visible']=max(f['max_visible'],int(num));f['total_visible']+=int(num)
   if view==1:f['view_45']=int(num)
 # >=64 raster pixels and physical area >= .01 block²: explicit, conservative,
 # provisional and reviewable; bottom faces and entirely occluded treated as small.
 for f in fs:
  f['classification']='large' if f['side']!='bottom' and f['max_visible']>=64 and f['area']>=.01 and f['style']!='rootlet' else 'small'
  del f['v'],f['n'],f['alpha'],f['rgba']
 return fs,list(contacts.values())
for m in [E.revise(E.humanoid('b017')),E.revise(E.humanoid('b018')),E.revise(E.creeper())]:
 fs,contacts=make(m);n=sum(f['classification']=='large' for f in fs);total=1024 if m.id=='b018' else 256;lower=len(fs)+3*n
 print(f"{m.id}: inter-cuboid direct-material contact candidate pairs={len(contacts)} observations={sum(c['observations'] for c in contacts)}");(OUT/(m.id+'_contacts.json')).write_text(json.dumps(contacts,ensure_ascii=False,indent=2));print(f"{m.id}: faces={len(fs)} visible={sum(f['max_visible']>0 for f in fs)} large={n} min_cells={lower} budget={total} evacuation_threshold={'YES' if m.id!='b018' and lower>=230 else 'no'}")
 p=OUT/(m.id+'_visibility_budget.json');p.write_text(json.dumps({'resolution':[W,H],'scale':SCALE,'views':16,'criterion':'non-bottom, max visible >=64 raster pixels, physical area >=0.01 block², not rootlet','faces':fs},ensure_ascii=False,indent=2))
