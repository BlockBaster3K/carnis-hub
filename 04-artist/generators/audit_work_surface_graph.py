#!/usr/bin/env python3
"""Surface-graph semantic-transition audit on exported GLB TEXCOORDs.
For every exported cuboid (including hidden faces), merge texels on shared cube
edges and perform graph-distance measurements through allowed transition tones.
Scope: intra-cuboid only, semantic categories declared below, nearest sampling.
Does not enumerate contacts created by intersections of different cubes.
"""
from pathlib import Path
from collections import defaultdict,deque,Counter
from PIL import Image
import json,struct,sys
sys.path.insert(0,str(Path(__file__).resolve().parent));import entities_tz3_rev31_work as E
D=E.OUT
families={'skin':('skin','skin_dark','skin_light'),'flesh':('flesh','flesh_dark','flesh_light','vein','vein_light','fluid','fluid_light'),'bone':('bone','bone_light','bone_dark','bone_crack'),'cartilage':('cartilage','cartilage_dark'),'cloth':('shirt','shirt_dark','shirt_light','pants','pants_dark','pants_light')}
cats={E.C(c)[:3]:kind for kind,ks in families.items() for c in ks}
pairs=[('skin','flesh',('skin_mid','skin_flesh','wound_mid')),('bone','cartilage',('bone_cart_mid1','bone_cart_mid2')),('skin','cloth',('cloth_mid1','cloth_mid2'))]
for ident in ('b017','b018','b019'):
 b=(D/(ident+'.glb')).read_bytes();n=struct.unpack_from('<I',b,12)[0];j=json.loads(b[20:20+n]);start=28+n;im=Image.open(D/(ident+'.png')).convert('RGBA');W=im.width
 def floats(idx):
  a=j['accessors'][idx];v=j['bufferViews'][a['bufferView']];assert a['componentType']==5126;d={'VEC2':2,'VEC3':3}[a['type']];flat=struct.unpack_from('<'+'f'*(d*a['count']),b,start+v.get('byteOffset',0)+a.get('byteOffset',0));return [flat[i:i+d] for i in range(0,len(flat),d)]
 results=[];cube_count=0
 for mesh in j['meshes']:
  for prim_id,prim in enumerate(mesh['primitives']):
   uv=floats(prim['attributes']['TEXCOORD_0']);assert len(uv)%24==0
   for cubeidx in range(len(uv)//24):
    cube_count+=1;refs=defaultdict(list);adj=defaultdict(set)
    for face in range(6):
     q=uv[cubeidx*24+face*4:cubeidx*24+(face+1)*4];x0=round(min(u for u,v in q)*W-.5);x1=round(max(u for u,v in q)*W+.5);y0=round(min(v for u,v in q)*W-.5);y1=round(max(v for u,v in q)*W+.5);assert x1-x0==y1-y0;size=x1-x0;N=size-1
     # Export faces: front, back, right, left, top, bottom. Image v points down.
     def xyz(i,k):return [(i,N-k,N),(N-i,N-k,0),(N,N-k,N-i),(0,N-k,i),(i,N,k),(i,0,N-k)][face]
     for y in range(size):
      for x in range(size):
       p=xyz(x,y);refs[p].append((x0+x,y0+y))
       for xx,yy in ((x+1,y),(x,y+1)):
        if xx<size and yy<size:q=xyz(xx,yy);adj[p].add(q);adj[q].add(p)
    colors={p:im.getpixel(c[0]) for p,c in refs.items()}
    for p,coords in refs.items():assert all(im.getpixel(c)==colors[p] for c in coords),(ident,mesh['name'],cubeidx,'seam')
    for A,B,mnames in pairs:
     middle={E.C(k)[:3] for k in mnames};AS={p for p,c in colors.items() if c[3] and cats.get(c[:3])==A};BS={p for p,c in colors.items() if c[3] and cats.get(c[:3])==B};MS={p for p,c in colors.items() if c[3] and c[:3] in middle}
     if not AS or not BS:continue
     direct=[(p,q) for p in AS for q in adj[p] if q in BS]
     def distances(sources):
      d={p:1 for q in sources for p in adj[q] if p in MS};queue=deque(d)
      while queue:
       p=queue.popleft()
       for q in adj[p]:
        if q in MS and q not in d:d[q]=d[p]+1;queue.append(q)
      return d
     da=distances(AS);db=distances(BS);common=da.keys()&db.keys(); width={p:da[p]+db[p]-1 for p in common};bad={p:w for p,w in width.items() if not (2<=w<=4)}
     result={'mesh':mesh['name'],'primitive':prim_id,'cuboid':cubeidx,'pair':[A,B],'direct_count':len(direct),'bridge_nodes':len(common),'width_histogram':dict(Counter(width.values())),'invalid_nodes':len(bad),'invalid_examples':[{'surface_xyz':p,'texels':refs[p],'width':w} for p,w in list(bad.items())[:10]]}
     if direct or common:results.append(result)
 counts=Counter();
 for r in results:counts.update({'direct':r['direct_count'],'bridge_nodes':r['bridge_nodes'],'invalid':r['invalid_nodes']})
 out={'cube_count':cube_count,'results':results,'totals':dict(counts),'coverage':'all cuboid surfaces, even hidden, on static export; not inter-cuboid contacts or any proof of full visibility'}
 (D/(ident+'_surface_graph_audit.json')).write_text(json.dumps(out,ensure_ascii=False,indent=2))
 print(ident,'cuboids',cube_count,'direct',counts['direct'],'bridge texels',counts['bridge_nodes'],'outside 2-4 graph-pixel widths',counts['invalid'])
 print('  invalid examples:',[{'mesh':r['mesh'],'cube':r['cuboid'],'pair':r['pair'],'bad':r['invalid_nodes'],'hist':r['width_histogram']} for r in results if r['invalid_nodes']][:4])
print('Partial only: graph distance is measured along surfaces, not Euclidean normal width; semantic mapping is heuristic; no inter-cuboid contacts or animation poses.')
