#!/usr/bin/env python3
"""Static exported GLB, analytic pairwise intersection of cuboid face planes.
Conservatively tests all overlapping surfaces including hidden ones. Samples each
finite line segment at UV-grid scale; records coplanar cases separately. NOT a
proof across animation poses, third-party occlusion, or every subtexel case.
"""
from pathlib import Path
import sys,struct,json,math
from collections import Counter
import numpy as np
from PIL import Image
sys.path.insert(0,str(Path(__file__).resolve().parent));import entities_tz3_rev31_work as E
D=E.OUT; eps=1e-7
family={'skin':('skin','skin_dark','skin_light'),'flesh':('flesh','flesh_dark','flesh_light','vein','vein_light','fluid','fluid_light'),'bone':('bone','bone_light','bone_dark','bone_crack'),'cartilage':('cartilage','cartilage_dark'),'cloth':('shirt','shirt_dark','shirt_light','pants','pants_dark','pants_light'),'dark':('shadow','deep','face_dark')}
categories={E.C(c)[:3]:kind for kind,cs in family.items() for c in cs}
pairs={frozenset(('skin','flesh')):('skin_mid','skin_flesh','wound_mid'),frozenset(('bone','cartilage')):('bone_cart_mid1','bone_cart_mid2'),frozenset(('cloth','skin')):('cloth_mid1','cloth_mid2')}; mid={k:{E.C(c)[:3] for c in v} for k,v in pairs.items()}
def m4(node):
 x,y,z,w=node.get('rotation',[0,0,0,1]);R=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]],float);M=np.eye(4);M[:3,:3]=R;M[:3,3]=node.get('translation',[0,0,0]);return M
def segment(f,g):
 n1,n2=f['n'],g['n'];d=np.cross(n1,n2);l=np.linalg.norm(d)
 if l<1e-7:
  if abs(np.dot(n1,g['v'][0]-f['v'][0]))>1e-6:return None
  # Conservative projected AABB of coplanar quadrilaterals; exact polygon clip pending.
  pr=lambda face: [(np.dot(v-f['v'][0],f['u']),np.dot(v-f['v'][0],f['vdir'])) for v in face['v']]
  a,b=pr(f),pr(g)
  if all(max(t[k] for t in a)>=min(t[k] for t in b)-1e-7 and max(t[k] for t in b)>=min(t[k] for t in a)-1e-7 for k in (0,1)):return 'coplanar'
  return None
 d=d/l;d1=np.dot(n1,f['v'][0]);d2=np.dot(n2,g['v'][0]);p=np.linalg.solve(np.stack([n1,n2,d]),np.array([d1,d2,0.]));lo,hi=-np.inf,np.inf
 for face in (f,g):
  for basis,L in ((face['u'],face['lu']),(face['vdir'],face['lv'])):
   a=np.dot(p-face['v'][0],basis);b=np.dot(d,basis)
   if abs(b)<1e-10:
    if a<-1e-7 or a>L+1e-7:return None
   else:
    aa,bb=(-a/b,(L-a)/b);lo=max(lo,min(aa,bb));hi=min(hi,max(aa,bb))
    if hi<lo-1e-7:return None
 if not np.isfinite(lo+hi) or hi-lo<1e-7:return None
 return p+lo*d,p+hi*d,d

def sample(face,p):
 off=p-face['v'][0];a=np.dot(off,face['u'])/face['lu'];b=np.dot(off,face['vdir'])/face['lv']
 if a<-1e-5 or a>1+1e-5 or b<-1e-5 or b>1+1e-5:return None
 x0,y0,w,h=face['rect'];x=x0+max(0,min(w-1,round(a*(w-1))));y=y0+max(0,min(h-1,round((1-b)*(h-1))));return ((int(x),int(y)),face['im'].getpixel((int(x),int(y))))
def inside(cube,p):
 local=(cube['inv']@np.array([*p,1]))[:3];return bool(np.all(local>cube['low']+1e-6) and np.all(local<cube['high']-1e-6))
def trace_on_cube(face,p,direction,distance,bycube):
 # Follow a straight path on the unfolded cuboid; when crossing a face edge,
 # rotate onto the adjacent face rather than stopping at that UV island.
 f=face;point=p.copy();direction=direction.copy();remaining=distance
 for _ in range(6):
  rel=point-f['v'][0];a=np.dot(rel,f['u']);b=np.dot(rel,f['vdir']);du=np.dot(direction,f['u']);dv=np.dot(direction,f['vdir']);candidates=[]
  for val,delta,L,basis in ((a,du,f['lu'],f['u']),(b,dv,f['lv'],f['vdir'])):
   if delta>1e-9:candidates.append(((L-val)/delta,basis))
   elif delta<-1e-9:candidates.append((-val/delta,-basis))
  candidates=[(max(0.,t),normal) for t,normal in candidates if t>=-1e-6]
  if not candidates:return None
  t,normal=min(candidates,key=lambda v:v[0])
  if t>=remaining-1e-9:return f,point+direction*remaining,direction
  point=point+direction*t;remaining-=t
  near=[nf for nf in bycube[f['cube']] if np.dot(nf['n'],normal)>.99999]
  if len(near)!=1:return None
  direction=-f['n'];f=near[0];point=point+direction*1e-9;remaining=max(0.,remaining-1e-9)
 return None

def surface_key(face,xy):
 x0,y0,w,h=face['rect'];i=xy[0]-x0;j=xy[1]-y0;N=w-1;side=face['side']
 return {'front':(i,N-j,N),'back':(N-i,N-j,0),'right':(N,N-j,N-i),'left':(0,N-j,i),'top':(i,N,j),'bottom':(i,0,N-j)}[side]
def rays(face,other,p,d,bycube):
 normal=np.cross(d,face['n']);normal/=np.linalg.norm(normal);side=[]
 def density(f,v):return math.sqrt((np.dot(v,f['u'])*(f['rect'][2]-1)/f['lu'])**2+(np.dot(v,f['vdir'])*(f['rect'][3]-1)/f['lv'])**2)
 for sign in (-1,1):
  direction=sign*normal;distance=.2/max(density(face,direction),1e-9);vals=[];last=None
  for _ in range(120):
   hit=trace_on_cube(face,p,direction,distance,bycube)
   if hit is None or inside(other,hit[1]):break
   f,pt,actual_direction=hit;r=sample(f,pt)
   if r is None:break
   key=surface_key(f,r[0])
   if key!=last:vals.append(r);last=key
   if len(vals)>=6:break
   distance+=.40/max(density(f,actual_direction),1e-9)
  if vals:side.append(vals)
 return side
for ident in ('b017','b018','b019'):
 raw=(D/(ident+'.glb')).read_bytes();ll=struct.unpack_from('<I',raw,12)[0];doc=json.loads(raw[20:20+ll]);base=28+ll;im=Image.open(D/(ident+'.png')).convert('RGBA');W=im.width
 def floats(idx):
  a=doc['accessors'][idx];v=doc['bufferViews'][a['bufferView']];d={'VEC2':2,'VEC3':3}[a['type']];f=struct.unpack_from('<'+'f'*(d*a['count']),raw,base+v.get('byteOffset',0)+a.get('byteOffset',0));return [f[i:i+d] for i in range(0,len(f),d)]
 parents={child:i for i,node in enumerate(doc['nodes']) for child in node.get('children',[])};world={}
 def global_m(i):
  if i not in world:world[i]=(global_m(parents[i]) if i in parents else np.eye(4))@m4(doc['nodes'][i])
  return world[i]
 cubes=[];faces=[]
 for i,node in enumerate(doc['nodes']):
  if 'mesh' not in node:continue
  M=global_m(i);inv=np.linalg.inv(M);mesh=doc['meshes'][node['mesh']]
  for pi,prim in enumerate(mesh['primitives']):
   v=np.array(floats(prim['attributes']['POSITION']));uv=floats(prim['attributes']['TEXCOORD_0']);assert len(v)%24==0
   for ci in range(len(v)//24):
    local=v[ci*24:(ci+1)*24];cube={'name':node['name'],'primitive':pi,'cube':ci,'inv':inv,'low':np.min(local,axis=0),'high':np.max(local,axis=0),'M':M};cidx=len(cubes);cubes.append(cube)
    for k in range(6):
     a=ci*24+k*4;verts=np.array([(M@np.array([*r,1]))[:3] for r in v[a:a+4]]);e1=verts[1]-verts[0];e2=verts[3]-verts[0];lu=np.linalg.norm(e1);lv=np.linalg.norm(e2);u=e1/lu;vv=e2/lv;n=np.cross(u,vv);n/=np.linalg.norm(n);tex=uv[a:a+4];x0=round(min(t[0] for t in tex)*W-.5);y0=round(min(t[1] for t in tex)*W-.5);w=round(max(t[0] for t in tex)*W+.5)-x0;h=round(max(t[1] for t in tex)*W+.5)-y0
     faces.append({'cube':cidx,'side':['front','back','right','left','top','bottom'][k],'v':verts,'u':u,'vdir':vv,'lu':lu,'lv':lv,'n':n,'rect':[x0,y0,w,h],'im':im,'lo':verts.min(axis=0),'hi':verts.max(axis=0)})
 from collections import defaultdict
 bycube=defaultdict(list)
 for face in faces:bycube[face['cube']].append(face)
 intersections=[];coplanar=[];rays_checked=0;invalid=[];matched=Counter()
 for ia,f in enumerate(faces):
  for g in faces[ia+1:]:
   if f['cube']==g['cube']:continue
   if np.any(f['hi']<g['lo']-1e-6) or np.any(g['hi']<f['lo']-1e-6):continue
   seg=segment(f,g)
   if seg is None:continue
   a,b=cubes[f['cube']],cubes[g['cube']];identity=[[a['name'],a['primitive'],a['cube'],f['side']],[b['name'],b['primitive'],b['cube'],g['side']]]
   if isinstance(seg,str):coplanar.append(identity);continue
   p0,p1,d=seg;length=np.linalg.norm(p1-p0);dens=max((f['rect'][2]-1)/f['lu'],(f['rect'][3]-1)/f['lv'],(g['rect'][2]-1)/g['lu'],(g['rect'][3]-1)/g['lv']);steps=max(2,min(1000,math.ceil(length*dens)+1));intersections.append({'faces':identity,'length':round(float(length),8),'samples':steps})
   for s in range(steps):
    p=p0+(p1-p0)*(s+.5)/steps;ra=rays(f,b,p,d,bycube);rb=rays(g,a,p,d,bycube)
    for aa in ra:
     for bb in rb:
      # Determine the closest unambiguously classified source on each face.
      x=next((k for k,v in enumerate(aa) if v[1][3] and v[1][:3] in categories),None);y=next((k for k,v in enumerate(bb) if v[1][3] and v[1][:3] in categories),None)
      if x is None or y is None:continue
      ca=categories[aa[x][1][:3]];cb=categories[bb[y][1][:3]];pair=frozenset((ca,cb))
      if ca==cb or pair not in mid:continue
      between=[v[1][:3] for v in reversed(aa[:x])]+[v[1][:3] for v in bb[:y]];allowed=mid[pair];good=2<=len(between)<=4 and all(t in allowed for t in between)
      rays_checked+=1;matched['OK' if good else 'FAIL']+=1
      if not good:invalid.append({'faces':identity,'world':[round(float(q),6) for q in p],'a':[(xy,list(c)) for xy,c in aa[:x+1]],'b':[(xy,list(c)) for xy,c in bb[:y+1]],'a_probe':[(xy,list(c)) for xy,c in aa],'b_probe':[(xy,list(c)) for xy,c in bb],'classes':[ca,cb],'width':len(between),'reason':'width' if not 2<=len(between)<=4 else 'unclassified intermediate'})
 report={'cube_count':len(cubes),'face_count':len(faces),'nonparallel_segments':len(intersections),'segments':intersections,'coplanar_candidates':len(coplanar),'coplanar':coplanar,'material_rays':rays_checked,'rays':dict(matched),'failures':invalid,'scope':'static GLB geometry only; includes hidden/coplanar surfaces; coplanar candidates not resolved; segment samples not mathematical proof of all subtexel points'}
 (D/(ident+'_geometry_contact_audit.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2));print(ident,'cuboids',len(cubes),'intersecting face segments',len(intersections),'coplanar candidates',len(coplanar),'material probes',rays_checked,'passed',matched['OK'],'failed',matched['FAIL'])
 for v in invalid[:3]:print(' ',v)
print('Scope incomplete: dark/shadow treated as its own class, coplanar visibility, moving poses, and continuous coverage are unresolved; hidden contacts may be false positives.')
