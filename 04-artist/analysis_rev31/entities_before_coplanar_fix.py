#!/usr/bin/env python3
"""Carnis TZ-3 phase 3.1. Procedural assembly of manually positioned cuboids,
hand-authored pixel swatches, bones, and 20 fps keyframes into glTF 2.0 GLB.
No Tabula or Blockbench. 1 glTF unit = 1 Minecraft block.
"""
import math, json, struct, io, base64, zipfile
from pathlib import Path
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'analysis_rev31'/'work_models';OUT.mkdir(parents=True,exist_ok=True)
P={'flesh':'#8B2020','flesh_light':'#A63030','flesh_dark':'#6B1818','shadow':'#2A1515','deep':'#1A0F0F','vein':'#B84040','vein_light':'#D05050','bone':'#D4C8A0','bone_dark':'#A89870','fluid':'#7A3040','fluid_light':'#C04050','glow':'#FF4040','glow2':'#FF6040','ground':'#582A27','ground_light':'#A55F49','ground_dark':'#46201E', 'skin':'#596C4A', 'skin_dark':'#3C4E36', 'skin_light':'#758661', 'shirt':'#39534C', 'shirt_dark':'#273B34', 'shirt_light':'#587065', 'pants':'#49403F', 'pants_dark':'#302927', 'pants_light':'#685652','skin_mid':'#6B7A5A','wound_mid':'#8B4040','shirt_mid':'#4B3538','skin_flesh':'#7A5040','bone_light':'#E8DCC0','bone_crack':'#6B5D40','cartilage':'#B8A878','cartilage_dark':'#9A8A60','sinew_dark':'#8B3030','face_dark':'#1A1A1A','cloth_mid1':'#506356','cloth_mid2':'#66705B','bone_cart_mid1':'#CBBE93','bone_cart_mid2':'#C2B389'}
def C(k):
 h=P[k].lstrip('#');return tuple(int(h[i:i+2],16) for i in (0,2,4))+(255,)
# Five manually placed pixel-art marks per tile, same palette across entities.
STROKES=[[(1,1),(2,1),(2,2),(4,4),(5,4),(5,5)],[(1,4),(2,4),(3,3),(4,3),(5,2)],[(1,2),(2,2),(3,3),(4,3),(5,4)],[(1,1),(1,2),(2,3),(4,5),(5,5)],[(1,5),(2,4),(3,4),(4,3),(5,3)]]
TYPES={
 'flesh':('flesh_dark','flesh','shadow'), 'raw':('flesh','flesh_light','flesh_dark'),
 'crust':('shadow','flesh_dark','deep'), 'bone':('bone','bone_light','bone_dark'),
 'sinew':('vein','vein_light','sinew_dark'), 'sac':('fluid','fluid_light','shadow'),
 'mask':('flesh','flesh_light','flesh_dark'), 'rootlet':('ground','ground_light','ground_dark'),
 'skin':('skin','skin_light','skin_dark'), 'shirt':('shirt','shirt_light','shirt_dark'),
 'pants':('pants','pants_light','pants_dark'), 'eye':('deep','glow','shadow'), 'infection':('skin','skin_light','skin_dark'), 'shirt_wound':('shirt','shirt_light','shirt_dark'), 'bone_join':('bone','bone_light','bone_dark'), 'whip_glow':('sinew_dark','vein_light','flesh_dark'), 'tail_glow':('skin','skin_light','skin_dark'), 'cartilage':('cartilage','bone','cartilage_dark'), 'eye_mask':('deep','glow2','shadow'), 'ink':('face_dark','shadow','deep'), 'cloth_skin':('shirt','skin_light','shirt_dark'), 'leg_mix':('skin','skin_light','skin_dark'), 'leg_wound':('skin','skin_light','skin_dark')}
# Explicit, connected 8×8 swatches. b base, l light, d shade; no noise.
PATTERNS={
 'flesh':["bbbbbbbb","bbbllbbb","bbllldbb","bdllldbb","bdddbbbb","bbbllbbb","bbllbbbb","bbbbbbbb"],
 'raw':["bbbbbbbb","bbllbbbb","bllldbbb","bllldbbb","bdddbbbb","bbllldbb","bbllldbb","bbbbbbbb"],
 'crust':["bbbbbbbb","bbllbbbb","blddlbbb","blddlbbb","bbddbbbb","bbblldbb","bbbdddbb","bbbbbbbb"],
 'bone':["bbbbbbbb","bblllbbb","bllllbbb","bbblbbbb","bbbllbbb","bblllbbb","bblddbbb","bbbbbbbb"],
 'sinew':["bbbbbbbb","bllbbbbb","bdllbbbb","bbdlllbb","bbblddbb","bbllldbb","bblddbbb","bbbbbbbb"],
 'sac':["bbbbbbbb","bllllbbb","blllldbb","blbbldbb","blllldbb","bbdddbbb","bbllbbbb","bbbbbbbb"],
 'mask':["bbbbbbbb","bbllllbb","bllbbllb","blbddblb","blbddblb","bbddddbb","bblllldb","bbbbbbbb"],
 'skin':["bbbbbbbb","bbbllbbb","bbllllbb","bblldbbb","bbddbbbb","bbbllbbb","bbllbbbb","bbbbbbbb"],
 'shirt':["bbbbbbbb","bbbllbbb","bbbllbbb","bbblbbbb","bblddbbb","bblddbbb","bbllbbbb","bbbbbbbb"],
 'pants':["bbbbbbbb","bblbbbbb","bbllbbbb","bbllbbbb","bbldbbbb","bbldbbbb","bbllbbbb","bbbbbbbb"],
 'rootlet':["bbbbbbbb","bbllbbbb","bbllbbbb","bbldbbbb","bbldbbbb","bbllbbbb","bbddbbbb","bbbbbbbb"],
 'eye':["bbbbbbbb","bdddddbb","bdllllbb","bdllllbb","bdddddbb","bbbbbbbb","bbbbbbbb","bbbbbbbb"]}
class Atlas:
 def __init__(self):
  self.base=Image.new('RGBA',(64,64),(0,0,0,0));self.glow=Image.new('RGBA',(64,64),(0,0,0,255));self.cache={};self.tiles=[]
 def tile(self,style,variant=0,face='side',glow=False):
  if style in ('rootlet','ink'):variant=0
  key=(style,variant%5,face,glow)
  if key in self.cache:return self.cache[key]
  idx=len(self.tiles);assert idx<64,(idx,key)
  x=(idx%8)*8;y=(idx//8)*8
  a,b,d=TYPES[style];im=Image.new('RGBA',(8,8),C(a));pix=im.load()
  pattern=PATTERNS.get(style,PATTERNS['flesh'])
  assert len(pattern)==8 and all(len(row)==8 for row in pattern)
  tone={'b':a,'l':b,'d':d}
  for yy,row in enumerate(pattern):
   for xx,ch in enumerate(row):pix[xx,yy]=C(tone[ch])
  # Hand-painted nonrepeating directional motifs; variants are different drawings,
  # not rotations or mirrors. The base and highlights are shared material colors.
  strokes=[[(1, 1), (2, 1), (2, 2), (3, 2), (3, 3)], [(5, 1), (4, 1), (4, 2), (4, 3), (3, 3), (2, 4)], [(1, 5), (2, 5), (2, 4), (3, 4), (4, 3)], [(5, 5), (4, 5), (4, 4), (3, 4), (3, 3), (2, 3)], [(1, 3), (2, 3), (3, 2), (3, 1), (4, 2)], [(2, 1), (3, 1), (4, 2), (4, 3), (5, 4)], [(1, 4), (2, 4), (3, 3), (3, 2), (4, 2)], [(5, 2), (5, 3), (4, 3), (4, 4), (3, 4), (2, 5)], [(2, 5), (3, 5), (3, 4), (4, 3), (5, 3)], [(1, 2), (2, 2), (3, 2), (3, 3), (4, 4)], [(4, 1), (3, 1), (3, 2), (2, 2), (2, 3)], [(5, 4), (4, 4), (3, 3), (2, 3), (2, 2)], [(1, 5), (1, 4), (2, 4), (3, 3), (4, 3)], [(2, 1), (2, 2), (3, 2), (4, 3), (4, 4)], [(5, 1), (5, 2), (4, 2), (3, 3), (2, 3)], [(1, 3), (2, 4), (3, 4), (3, 5), (4, 5)], [(4, 1), (4, 2), (3, 3), (2, 3), (1, 3)], [(1, 1), (1, 2), (2, 3), (3, 3), (4, 4)], [(5, 5), (5, 4), (4, 3), (3, 3), (2, 2)], [(1, 4), (2, 3), (3, 3), (4, 2), (5, 2)], [(2, 5), (2, 4), (3, 3), (3, 2), (4, 1)], [(5, 3), (4, 3), (3, 2), (2, 2), (2, 1)], [(1, 2), (1, 3), (2, 4), (3, 4), (4, 5)], [(3, 1), (3, 2), (2, 3), (2, 4), (1, 5)], [(5, 1), (4, 2), (4, 3), (3, 4), (3, 5)], [(1, 5), (2, 4), (3, 4), (4, 4), (5, 3)], [(1, 1), (2, 2), (3, 2), (4, 2), (5, 1)], [(2, 2), (2, 3), (3, 4), (4, 4), (5, 5)], [(1, 4), (2, 4), (3, 5), (4, 5), (5, 4)], [(4, 1), (3, 2), (3, 3), (2, 4), (1, 4)], [(5, 4), (4, 3), (3, 3), (2, 2), (1, 2)], [(1, 3), (2, 2), (3, 2), (4, 3), (5, 3)], [(2, 1), (3, 2), (4, 2), (5, 3), (5, 4)], [(1, 5), (2, 5), (3, 4), (4, 4), (5, 5)], [(5, 5), (4, 4), (3, 4), (2, 3), (1, 3)], [(1, 1), (1, 2), (2, 2), (3, 3), (3, 4)]]
  if style in ('skin','shirt','pants','bone','raw','flesh','sinew','sac','crust','mask','cartilage'):
   # First wipe the inherited repeated motif, then draw a distinct connected mark.
   im=Image.new('RGBA',(8,8),C(a)); pix=im.load()
   pts=strokes[idx%len(strokes)]
   for u,v in pts:pix[u,v]=C(d)
   for u,v in [(u+1,v) for u,v in pts if u<6][:3]:pix[u,v]=C(b)
   if style=='bone':
    for u,v in pts[:3]:pix[u,v]=C('bone_crack')
    for u,v in [(1,1),(2,1),(3,1)]:pix[u,v]=C('bone_light')
   if style in ('sinew','mask','raw','flesh'):
    u,v=pts[-1]; pix[min(7,u+1),v]=C('vein_light')
  if style in ('infection','shirt_wound','bone_join'):
   # Jagged 2–4-pixel color transition, specified as a unique pixel map.
   zone={'infection':{'g':'skin','u':'skin_mid','v':'skin_flesh','r':'flesh','h':'flesh_light','d':'skin_dark'},
         'shirt_wound':{'g':'shirt','u':'shirt_mid','v':'wound_mid','r':'flesh','h':'flesh_light','d':'shirt_dark'},
         'bone_join':{'g':'bone','u':'cartilage','v':'sinew_dark','r':'vein','h':'vein_light','d':'bone_dark'}}[style]
   artset=[['ggguvrhh','ggguvrrr','gguvrrrh','gduuvrrr','ggguvrrr','gguvvrrr','gduvrrhr','ggguvrrr'],['ggguvrrr','gguvvrrh','gduuvrrr','ggguvrrr','ggguvrhr','gguvvrrr','gguvrrrh','ggguvrrr'],['gguvrrrh','gduuvrrr','ggguvrrr','gguvvrrr','gguvrrrh','ggguvrrr','gduuvrrr','gguvvrhr'],['gduuvrrr','ggguvrrh','gguvrrrh','gguvvrrr','ggguvrhr','gduuvrrr','ggguvrrr','gguvvrrr'],['ggguvrhr','gguvvrrr','gguvrrrh','ggguvrrr','gduuvrrr','ggguvrrr','gguvvrhr','gguvrrrh']]; art=artset[variant%5]
   for yy,row in enumerate(art):
    for xx,ch in enumerate(row):pix[xx,yy]=C(zone[ch])
  # Signature motifs occupy front-face-only tiles.
  if face=='zombie_face':
   for u,v in [(1,2),(2,2),(4,2),(5,2)]:pix[u,v]=C('deep')
   for u,v in [(1,2),(5,2)]:pix[u,v]=C('glow')
   for u,v in [(2,5),(3,5),(4,5)]:pix[u,v]=C('shadow')
  if face=='mask_face':
   for u,v in [(0,0),(1,0),(5,0),(6,0)]:pix[u,v]=C('fluid_light')
   for u,v in [(1,2),(5,2)]:pix[u,v]=C('glow')
   for u,v in [(2,5),(3,5),(4,5)]:pix[u,v]=C('deep')
  if face=='skull_face':
   for u,v in [(1,2),(2,2),(4,2),(5,2)]:pix[u,v]=C('deep')
   for u,v in [(1,2),(5,2)]:pix[u,v]=C('glow')
   for u,v in [(2,5),(4,5)]:pix[u,v]=C('shadow')
  if face=='creeper_face':
   for u,v in [(1,2),(2,2),(4,2),(5,2)]:pix[u,v]=C('deep')
   for u,v in [(1,2),(5,2)]:pix[u,v]=C('glow')
   for u,v in [(1,5),(2,5),(3,5),(4,5),(5,5)]:pix[u,v]=C('deep')
  if style=='sac':
   for u,v in [(2,2),(5,4)]:pix[u,v]=C('fluid_light')
   for u,v in [(2,3),(5,5)]:pix[u,v]=C('flesh_dark')
  if style=='rootlet':
   for yy in range(8):
    for xx in range(8):
     r,g,b,alpha=pix[xx,yy];pix[xx,yy]=(r,g,b, 128 if yy>=6 else 178)
  self.base.paste(im,(x,y))
  if glow:
   gp=self.glow.load()
   if face in ('mask_face','zombie_face','skull_face','creeper_face') or style in ('eye','eye_mask'):
    for u,v in ([(2,3),(3,3),(4,3)] if style in ('eye','eye_mask') else [(1,2),(5,2)]):gp[x+u,y+v]=C('glow2' if style=='eye_mask' else 'glow')
    if face=='mask_face':
     for u,v in [(1,0),(5,0)]:gp[x+u,y+v]=C('glow2')
   elif style=='sac':
    for u,v in [(2,2),(3,2),(2,3),(3,3),(4,3)]:gp[x+u,y+v]=C('glow')
   elif style in ('sinew','whip_glow'):
    for u,v in [(2,2),(3,3),(4,4)]:gp[x+u,y+v]=C('vein_light' if style=='sinew' else 'glow')
   elif style in ('raw','tail_glow'):
    for u,v in ([(3,3)] if style=='tail_glow' else [(2,3),(3,3),(4,4)]):gp[x+u,y+v]=C('glow')
  self.tiles.append(key);self.cache[key]=idx;return idx
 def uv(self,i):
  x=(i%8)*8;y=(i//8)*8
  # Texel-centre inset protects against crossing tile boundaries with nearest sampling.
  return ((x+.5)/64,(y+.5)/64,(x+7.5)/64,(y+7.5)/64)
class Model:
 def __init__(self,id,label):self.id=id;self.label=label;self.nodes=[];self.meta=[];self.atlas=Atlas();self.byname={};self.cubes=[]
 def bone(self,name,parent,pivot,role):
  assert name not in self.byname and name
  self.byname[name]=len(self.nodes);self.nodes.append({'name':name,'parent':parent,'pivot':pivot,'cubes':[]});self.meta.append((name,role));return name
 def cube(self,bone,center,size,style,var=0,face='side',glow=False):
  assert all(x>0 for x in size)
  item=(center,size,style,var,face,glow);self.nodes[self.byname[bone]]['cubes'].append(item);self.cubes.append((bone,item))

def humanoid(kind):
 zombie=kind=='b017';m=Model(kind,'Заражённый зомби' if zombie else 'Заражённый скелет');b=m.bone;c=m.cube
 if zombie:
  b('root',None,(0,0,0),'корень')
  b('torso','root',(0,.94,0),'торс в остатках рубахи и открытая плоть')
  b('head','torso',(0,1.51,0),'череп и видимая зелёная кожа')
  b('jaw','head',(0,1.54,.05),'нижняя челюсть')
  b('mask','head',(0,1.68,.12),'выступающая биомаска, пустулы, светящиеся глаза')
  b('chest_growth','torso',(.08,1.28,.12),'отдельный грудной нарост')
  for side,sgn in [('left',1),('right',-1)]:
   b('arm_'+side,'torso',(sgn*.225,1.45,0),'плечо: '+('мутировавшее' if side=='left' else 'сохранившее кожу'))
   b('forearm_'+side,'arm_'+side,(sgn*(.255 if side=='left' else .235),1.18,0),'предплечье: '+('когти и наросты' if side=='left' else 'кисть'))
   b('leg_'+side,'root',(sgn*.095,.94,0),'нога: '+('рваная одежда' if side=='left' else 'нарост и корка'))
   b('foot_'+side,'leg_'+side,(sgn*.095,.12,.015),'стопа и корешки')
  c('torso',(0,1.25,0),(.37,.61,.20),'shirt',0)
  c('torso',(-.12,1.17,.106),(.11,.31,.018),'shirt_dark' if False else 'shirt',0)
  # Torn opening has an irregular, stepped flesh boundary.
  for pos,sz in [((.045,1.33,.114),(.16,.29,.03)),((.105,1.19,.117),(.12,.12,.035)),((.01,1.45,.115),(.10,.09,.03))]:c('torso',pos,sz,'raw',1)
  c('head',(0,1.70,0),(.30,.33,.24),'skin',1)
  c('head',(0,1.855,-.01),(.31,.06,.25),'pants',2)
  c('head',(-.10,1.68,.124),(.08,.17,.012),'skin',2)
  c('jaw',(0,1.54,.08),(.26,.075,.12),'skin',3)
  # Mask is an actual assembly standing about 0.14 blocks (2.2 px) in front of the skull.
  for center,size in [((0,1.84,.195),(.28,.07,.13)),((-.12,1.73,.20),(.06,.20,.13)),((.12,1.73,.20),(.06,.20,.13)),((0,1.69,.205),(.055,.17,.14)),((.045,1.61,.20),(.18,.06,.13))]:c('mask',center,size,'mask',1)
  for y in [1.83,1.79,1.70,1.63]:
   for x in [-.10,.10]:c('mask',(x,y,.268),(.045,.014,.014),'raw',int(y*100)%5)
  for x in [-.067,.067]:c('mask',(x,1.75,.235),(.05,.045,.035),'eye_mask',0,'side',True)
  c('mask',(-.09,1.90,.08),(.10,.13,.12),'sac',1,'side',True)
  c('mask',(.075,1.91,.10),(.12,.15,.13),'sac',3,'side',True)
  c('torso',(.035,1.30,.135),(.18,.24,.015),'shirt_wound',1)
  c('chest_growth',(.10,1.30,.16),(.15,.22,.12),'raw',3)
  c('chest_growth',(.15,1.37,.20),(.11,.11,.09),'sac',1)
  c('chest_growth',(.025,1.25,.18),(.07,.12,.08),'sinew',2)
  # Healthy right arm remains visibly green; left is > 2x thicker with distinct protrusions.
  c('arm_right',(-.235,1.34,0),(.12,.27,.15),'shirt',2)
  c('forearm_right',(-.238,1.04,.01),(.11,.29,.14),'skin',0)
  c('forearm_right',(-.238,.89,.01),(.115,.09,.15),'skin',2)
  c('arm_left',(.25,1.34,0),(.11,.26,.12),'skin',4)
  c('arm_left',(.25,1.34,0),(.205,.29,.19),'infection',2)
  c('arm_left',(.26,1.32,.105),(.15,.18,.02),'raw',4,'side',True)
  c('arm_left',(.34,1.39,-.01),(.13,.15,.17),'sac',2)
  c('arm_left',(.28,1.47,.06),(.13,.12,.16),'crust',1)
  c('forearm_left',(.275,1.03,.01),(.10,.28,.11),'skin',3)
  c('forearm_left',(.275,1.03,.01),(.20,.32,.18),'raw',3)
  c('forearm_left',(.35,1.06,.03),(.12,.15,.13),'crust',2)
  c('forearm_left',(.30,.87,.04),(.20,.10,.19),'flesh',2)
  for z in [-.025,.035,.095]:
   c('forearm_left',(.31,.79,z),(.038,.13,.034),'crust',1)
   c('forearm_left',(.32,.735,z+.012),(.032,.045,.03),'raw',2)
  for side,sgn in [('left',1),('right',-1)]:
   c('leg_'+side,(sgn*.095,.52,0),(.16,.78,.16),'pants',0)
   c('leg_'+side,(sgn*.095,.33,.085),(.11,.17,.025),'skin',1)
   if side=='right':
    c('leg_right',(-.10,.57,.105),(.17,.34,.06),'crust',2)
    c('leg_right',(-.17,.51,.10),(.08,.16,.09),'raw',1)
    c('leg_right',(-.12,.72,.12),(.10,.07,.07),'bone',2)
   c('foot_'+side,(sgn*.095,.08,.035),(.16,.13,.23),'pants',2)
   for i in range(3):c('foot_'+side,(sgn*.095+(-.045+i*.045),.022,.08),(.018,.04,.17),'rootlet',i)
 else:
  b('root',None,(0,0,0),'корень');b('pelvis','root',(0,.90,0),'таз');b('spine','pelvis',(0,1.02,0),'позвоночник');b('ribcage','spine',(0,1.18,0),'каркас для отдельных рёбер')
  b('head','spine',(0,1.56,0),'череп с глазницами');b('jaw','head',(0,1.59,.05),'подвижная нижняя челюсть')
  for i,y in enumerate([1.45,1.31,1.17],1):
   for side,sgn in [('left',1),('right',-1)]:b('rib_'+side+'_'+str(i),'ribcage',(sgn*.035,y,0),'отдельное ребро, крепление у позвоночника')
  for n,y in [('sinew_top',1.43),('sinew_mid',1.29),('sinew_bot',1.15)]:b(n,'ribcage',(0,y,.10),'витая мясистая перемычка и узлы')
  b('arm_blade','ribcage',(-.22,1.48,0),'костяное плечо');b('forearm_blade','arm_blade',(-.25,1.20,0),'кисть-лезвие')
  b('arm_whip','ribcage',(.22,1.48,0),'плечо плети');b('whip_seg1','arm_whip',(.25,1.22,0),'первый сегмент плети');b('whip_seg2','whip_seg1',(.25,.99,0),'второй сегмент плети');b('whip_seg3','whip_seg2',(.25,.76,0),'кончик плети')
  for side,sgn in [('left',1),('right',-1)]:
   b('leg_'+side,'pelvis',(sgn*.09,.90,0),'бедро и голень');b('foot_'+side,'leg_'+side,(sgn*.09,.12,0),'стопа с корешками')
  c('pelvis',(0,.90,0),(.27,.13,.13),'bone',1);c('pelvis',(-.12,.91,0),(.08,.14,.14),'bone',1);c('pelvis',(.12,.91,0),(.08,.14,.14),'bone',1)
  c('spine',(0,1.30,0),(.07,.55,.08),'bone',0)
  for y in [1.08,1.19,1.30,1.41,1.52]:
   c('spine',(0,y,-.025),(.11,.055,.09),'bone',2)
   c('spine',(0,y-.038,-.025),(.07,.02,.085),'cartilage',2)
  # Skull: cranium, cheeks and separate jaw; dark recessed sockets and teeth are real pieces.
  c('head',(0,1.78,-.02),(.27,.34,.20),'bone',0)
  c('head',(0,1.91,.075),(.28,.08,.07),'bone',1)
  for x in [-.105,.105]:c('head',(x,1.73,.082),(.06,.19,.07),'bone',2)
  for x in [-.062,.062]:
   c('head',(x,1.79,.092),(.07,.08,.035),'crust',0)
   c('head',(x,1.79,.113),(.035,.035,.018),'eye',0,'side',True)
  c('head',(0,1.70,.10),(.035,.07,.04),'bone',1)
  for x in [-.025,.025]:c('head',(x,1.70,.125),(.016,.025,.012),'crust',2)
  for j,x in enumerate([-.08,-.04,0,.04,.08]):c('head',(x,1.65,.12),(.022+j*.001,.035,.02),'bone',j)
  c('jaw',(0,1.60,.06),(.23,.055,.13),'bone',0)
  for x in [-.075,-.025,.025,.075]:c('jaw',(x,1.63,.135),(.025,.045,.018),'bone',2)
  for i,y in enumerate([1.45,1.31,1.17],1):
   for side,sgn in [('left',1),('right',-1)]:
    n='rib_'+side+'_'+str(i); k=[1.0,.90,.77][i-1]; thick=[.055,.045,.035][i-1]
    c(n,(sgn*.09,y,0),(.14*k,thick,.11),'bone',i)
    c(n,(sgn*(.09+.07*k),y-.03,.025),(.04,.08*k,.11),'bone',i+1)
    c(n,(sgn*(.09+.04*k),y-.06,.082),(.085*k,.035,.045),'bone',i+2)
    c(n,(sgn*.035,y,.045),(.04,.04,.03),'bone_join',i)

  # Braiding: intertwined alternating raised strands and knots, visibly separate volumes.
  for n,y in [('sinew_top',1.405),('sinew_mid',1.265),('sinew_bot',1.125)]:
   for i,x in enumerate([-.12,-.08,-.04,0,.04,.08,.12]):
    dy=.016 if i%2==0 else -.016
    c(n,(x,y+dy,.127),(.047,.052,.045),'sinew',i%5,'side',True)
    c(n,(x,y-dy,.153),(.035,.035,.035),'flesh',i%5)
   c(n,(0,y,.175),(.075,.065,.055),'raw',1)
  c('arm_blade',(-.235,1.34,0),(.085,.27,.09),'bone',1)
  c('forearm_blade',(-.255,1.04,0),(.09,.32,.09),'bone',4)
  c('forearm_blade',(-.27,.87,.03),(.15,.17,.06),'bone',3)
  c('forearm_blade',(-.32,.80,.03),(.055,.12,.05),'bone',3)
  c('arm_whip',(.235,1.35,0),(.09,.27,.10),'bone',1)
  for n,y,size in [('whip_seg1',1.10,.085),('whip_seg2',.87,.065),('whip_seg3',.65,.045)]:
   c(n,(.25,y,0),(size*.65,.23,size*.65),'bone',1)
   c(n,(.25,y,0),(size,.23,size),'sinew',2)
   c(n,(.25,y+.05,.025),(size*1.15,.045,size*1.1),'whip_glow',2,'side',True)
  for side,sgn in [('left',1),('right',-1)]:
   c('leg_'+side,(sgn*.09,.50,0),(.075,.75,.085),'bone',2)
   for y in [.80,.50,.20]:c('leg_'+side,(sgn*.09,y,0),(.13,.095,.12),'cartilage' if y==.50 else 'bone',1)
   c('foot_'+side,(sgn*.09,.07,.03),(.13,.11,.21),'bone',3)
   for k in range(3):c('foot_'+side,(sgn*.09+(k-1)*.035,.022,.09),(.018,.04,.17),'rootlet',k)
 return m

def creeper():
 m=Model('b019','Заражённый крипер');b=m.bone;c=m.cube
 b('root',None,(0,0,0),'корень')
 b('body','root',(0,.40,0),'компактное вертикальное тело, рубец заражения')
 b('head','body',(0,1.12,.09),'широкая плоская голова и глаза')
 b('jaw','head',(0,1.22,.235),'нижний край рта')
 b('sac_left','body',(.13,1.04,-.16),'левый спинной мешок')
 b('sac_right','body',(-.13,1.04,-.16),'правый спинной мешок')
 b('sac_back','body',(0,.90,-.19),'крупный задний мешок')
 # Stagger the six joints along Z; all feet stay within the 0.6×0.6 box.
 positions=[(-.222,.20),(.222,.115),(-.222,.03),(.222,-.055),(-.222,-.14),(.222,-.225)]
 for i,(x,z) in enumerate(positions,1):b('leg_'+str(i),'root',(x,.40,z),'лапа '+('передняя' if i<=2 else 'средняя' if i<=4 else 'задняя'))
 b('tail','body',(0,.58,-.18),'малый хвост и светящийся кончик')
 # Healthy base kept as a complete volume under infection meshes.
 c('body',(0,.755,-.015),(.48,.71,.32),'skin',0)
 c('body',(0,1.105,.06),(.34,.10,.24),'skin',3)
 c('body',(.03,.82,.149),(.32,.38,.012),'infection',0)
 c('body',(.11,.82,.164),(.17,.22,.025),'raw',1,'side',True)
 for center,size in [((.14,.88,.181),(.11,.11,.035)),((.075,.74,.18),(.09,.075,.035)),((.16,.71,.173),(.055,.07,.028))]:c('body',center,size,'flesh',3)
 # Wider-than-body upright creeper head, shallow depth, flat crown.
 c('head',(0,1.385,.085),(.56,.55,.30),'skin',2)
 # Separate eye frames / pupils, all within hitbox front face.
 for x in [-.14,.14]:
  c('head',(x,1.43,.243),(.115,.10,.018),'ink',0)
  c('head',(x,1.43,.255),(.042,.043,.012),'eye',1,'side',True)
 # Characteristic inverted V rendered as separate segments; dark central cavity.
 for i,(x,y) in enumerate([(-.09,1.265),(-.05,1.295),(0,1.325),(.05,1.295),(.09,1.265)]):
  c('head',(x,y,.246),(.052,.06,.024),'ink',i)
 c('head',(0,1.29,.253),(.025,.025,.015),'flesh',4)
 c('jaw',(0,1.235,.245),(.12,.032,.028),'flesh',3)
 # Fractured organic silhouette, several staggered blocks instead of one square.
 for pos,sz in [((.245,1.53,.205),(.09,.11,.065)),((.205,1.575,.223),(.10,.07,.065)),((-.235,1.25,.19),(.07,.08,.07))]:c('head',pos,sz,'raw',2)
 # Three separate materials/UV marks; all retained within the 0.6 depth.
 c('sac_left',(.135,1.035,-.205),(.15,.16,.15),'sac',1,'side',True)
 c('sac_left',(.16,1.065,-.26),(.075,.085,.06),'flesh',3)
 c('sac_right',(-.135,1.025,-.205),(.15,.17,.15),'sac',2,'side',True)
 c('sac_right',(-.16,1.05,-.26),(.075,.07,.06),'flesh',2)
 c('sac_back',(0,.85,-.215),(.21,.22,.17),'sac',3,'side',True)
 c('sac_back',(0,.91,-.26),(.11,.10,.06),'raw',3)
 for i,(x,z) in enumerate(positions,1):
  sx=.135 if i<=2 else .11; depth=.062; sy=.36 if i<=2 else .33
  c('leg_'+str(i),(x,.225,z),(sx,sy,depth),'skin',i%5)
  c('leg_'+str(i),(x,.055,z),(sx+.01,.10,.075),'flesh',i%5)
  c('leg_'+str(i),(x,.045,z+.026),(.045,.045,.022),'crust',i%5)
  for dx in [-.03,.02]:c('leg_'+str(i),(x+dx,.014,z+.015),(.014,.028,.04),'rootlet',i%5)
 c('tail',(0,.58,-.23),(.05,.065,.12),'skin',1)
 c('tail',(0,.57,-.285),(.035,.04,.03),'tail_glow',1,'side',True)
 return m


# Key pose controls expressed in radians for rotations, rest values 0/1.
def controls(kind,anim,t,T):
 phase=2*math.pi*t/T; w=math.sin(phase); vals={}
 def r(n,axis,v): vals[(n,'rotation')]=tuple(v if i==axis else 0.0 for i in range(3))
 def s(n,x,y,z):vals[(n,'scale')]=(x,y,z)
 def tr(n,x,y,z):vals[(n,'translation')]=(x,y,z)
 if anim in ('idle','bone_rattle'):
  r('head',2,.035*w);s('torso' if kind=='b017' else 'ribcage' if kind=='b018' else 'body',1+.015*w,1+.01*w,1+.015*w)
  if kind=='b018' and anim=='idle':r('jaw',0,.035*w)
  if kind=='b019' and anim=='idle':
   for n in ('sac_left','sac_right','sac_back'):s(n,1+.025*w,1+.025*w,1+.025*w)
  if anim=='bone_rattle':r('ribcage',2,.09*math.sin(phase*4));r('jaw',0,.07*math.sin(phase*4))
 elif anim in ('walk','crawl'):
  if kind=='b019':
   for i in range(1,7):r('leg_'+str(i),0,.32*math.sin(phase+(0 if i in [1,4,5] else math.pi)))
   r('body',2,.035*w)
   if anim=='crawl':tr('root',0,-.10,0);r('body',0,.13)
  elif kind=='b017':
   r('leg_left',0,.40*w);r('leg_right',0,-.40*w);r('arm_left',0,-.23*w);r('arm_right',0,.23*w)
  else:
   r('leg_left',0,.4*w);r('leg_right',0,-.4*w);r('arm_blade',0,-.22*w);r('arm_whip',0,.22*w)
 elif anim in ('attack','whip_attack'):
  z=math.sin(math.pi*t/T)
  if kind=='b017':r('arm_left',0,-1.25*z);r('forearm_left',0,-.5*z);r('jaw',0,.20*z)
  elif kind=='b018':
   if anim=='attack':r('arm_blade',0,-1.25*z);r('forearm_blade',0,-.35*z)
   else:
    r('arm_whip',0,-1.4*z)
    for i in (1,2,3):r('whip_seg'+str(i),0,.7*math.sin(math.pi*max(0,min(1,(t/T-(i-1)*.10)/(1-(i-1)*.10)))))
  else:r('head',0,-.5*z);tr('body',0,0,.07*z)
 elif anim=='hurt':
  z=math.sin(math.pi*t/T);r('body' if kind=='b019' else 'torso' if kind=='b017' else 'spine',0,-.18*z)
  if kind=='b018':r('jaw',0,.14*z);r('ribcage',2,.11*z)
 elif anim=='death':
  z=t/T;r('root',0,-1.35*z);tr('root',0,-.10*z,0);r('head',0,.25*z)
  if kind=='b018':
   r('arm_blade',2,-.5*z);r('arm_whip',2,.5*z);r('leg_left',2,.25*z);r('leg_right',2,-.25*z)
 elif anim=='mask_twitch':r('mask',2,.14*math.sin(2*math.pi*t/T));r('jaw',0,.13*math.sin(math.pi*t/T))
 elif anim in ('fuse','sac_charge'):
  z=math.sin(math.pi*t/T) if anim=='sac_charge' else .5+.5*math.sin(phase*3)
  for n in ('sac_left','sac_right','sac_back'):s(n,1+.26*z,1+.26*z,1+.26*z)
  r('body',2,.035*math.sin(phase*4))
 elif anim=='assimilate':
  z=t/T;impulse=math.sin(math.pi*min(1,t/(T*.65)));r('spine',0,-.20*impulse+.08*z);r('ribcage',2,.10*impulse)
  for n in ('sinew_top','sinew_mid','sinew_bot'):s(n,1+.16*z,1+.11*z,1+.12*z)
 elif anim=='detonate':
  z=math.sin(math.pi*t/T);s('body',1+.28*z,1+.18*z,1+.28*z)
  for n in ('sac_left','sac_right','sac_back'):s(n,1+.6*z,1+.6*z,1+.6*z)
  tr('root',0,.10*z,0)
 return vals
ANIMS={
 'b017':[('idle',3,'loop'),('walk',.8,'loop'),('attack',.4,'once'),('hurt',.2,'once'),('death',1.5,'once'),('mask_twitch',.15,'once')],
 'b018':[('idle',3,'loop'),('walk',.8,'loop'),('attack',.4,'once'),('hurt',.2,'once'),('death',1.5,'once'),('whip_attack',.4,'once'),('bone_rattle',2,'loop'),('assimilate',.6,'once')],
 'b019':[('idle',3,'loop'),('walk',.8,'loop'),('attack',.4,'once'),('hurt',.2,'once'),('death',1.5,'once'),('crawl',.8,'loop'),('fuse',1,'loop'),('sac_charge',1,'once'),('detonate',.5,'once')],
}
def quat(e):
 x,y,z=[v/2 for v in e];sx,cx=math.sin(x),math.cos(x);sy,cy=math.sin(y),math.cos(y);sz,cz=math.sin(z),math.cos(z)
 return (sx*cy*cz-cx*sy*sz,cx*sy*cz+sx*cy*sz,cx*cy*sz-sx*sy*cz,cx*cy*cz+sx*sy*sz)
class FaceAtlas:
 """One independently allocated island per cuboid face; 8px grid packing."""
 def __init__(self,m):
  self.m=m;self.size=256;N=self.size//8;total=N*N # pre-authorized evacuation
  faces=[]
  for node in m.nodes:
   for ci,(center,size,style,var,face,glow) in enumerate(node['cubes']):
    sx,sy,sz=size
    for side,fw,fh in [('front',sx,sy),('back',sx,sy),('right',sz,sy),('left',sz,sy),('top',sx,sz),('bottom',sx,sz)]:
     faces.append({'bone':node['name'],'cube':ci,'side':side,'style':style,'variant':var,'face':face,'glow':glow,'area':fw*fh,'large':max(fw,fh)>=.25 or fw*fh>=.045,'size':8})
  count=len(faces)
  # Every non-root cuboid has six 16x16 faces; root rods have six 8x8 faces.
  # This assigns a conservative budget even to hidden non-root faces, and keeps
  # all six face grids commensurate for angular consistency work.
  for f in faces:
   f['size']=8 if f['style']=='rootlet' else 16
  if sum((f['size']//8)**2 for f in faces)>total:raise ValueError(('UV budget',m.id,count))
  used=[[False]*N for _ in range(N)]
  for i in sorted(range(count),key=lambda i:faces[i]['size'],reverse=True):
   f=faces[i];q=f['size']//8;found=None
   for gy in range(N-q+1):
    for gx in range(N-q+1):
     if all(not used[yy][xx] for yy in range(gy,gy+q) for xx in range(gx,gx+q)):
      found=(gx,gy);break
    if found:break
   if not found:raise ValueError(('packing failed',m.id,i,q))
   gx,gy=found
   for yy in range(gy,gy+q):
    for xx in range(gx,gx+q):used[yy][xx]=True
   f['rect']=[gx*8,gy*8,q*8,q*8]
  self.base=Image.new('RGBA',(self.size,self.size),(0,0,0,0));self.glow=Image.new('RGBA',(self.size,self.size),(0,0,0,255));self.lookup={};self.layout=faces;self.tiles=[];self.transitions=[]
  for i,f in enumerate(faces):
   self.lookup[(f['bone'],f['cube'],f['side'])]=f
   self.paint(f,i)
  self.sync_cuboid_edges()
  self.resolve_identical_art()
  self.paint_contact_rims()
  self.paint_shoulder_stitch()
  self.ensure_minimum_detail()
  self.resolve_identical_art(protect_annotations=False)
  self.repair_direct_material_contacts()
  self.normalise_surface_bands()
  self.apply_cross_contact_edits()
  self.repair_direct_material_contacts()
  # Keep honest accounting of annotations invalidated by corner edits; they are
  # not accepted as checked transitions and must be remade in the full audit.
  self.transition_invalidated=[];saved=[]
  for sample in self.transitions:
   actual=['#%02X%02X%02X'%self.base.getpixel(tuple(pt))[:3] for pt in sample['coords']]
   (saved if actual==sample['colors'] else self.transition_invalidated).append(sample)
  self.transitions=saved
  self.unused=sum(not b for row in used for b in row)*64
  self.used=self.size*self.size-self.unused
  if self.unused/(self.size*self.size)>.75:raise ValueError(('unused budget failed',m.id,self.unused))
 def paint_contact_rims(self):
  # Integrate inset overlays into their parent material on every exposed edge.
  # Face grids agree at cube corners because each face has the same ring width.
  for f in self.layout:
   bone,sty=f['bone'],f['style'];x,y,w,h=f['rect']; side=f['side'];outer=None
   if self.m.id=='b017':
    if sty in ('mask','infection') or (sty=='raw' and bone!='chest_growth') or (sty=='sac' and bone=='mask') or (sty=='crust' and bone=='forearm_left'):outer=('skin','skin_mid','skin_flesh')
    if sty=='shirt_wound':outer=('shirt','shirt_mid','wound_mid')
    if sty=='cloth_skin':outer=('skin','cloth_mid2','cloth_mid1')
   elif self.m.id=='b019':
    if sty in ('infection','raw','sac','leg_wound'):outer=('skin','skin_mid','skin_flesh')
   elif self.m.id=='b018' and sty=='cartilage':outer=('bone','bone_cart_mid1','bone_cart_mid2')
   if outer:
    if self.m.id=='b018':
     converted={C(t)[:3] for t in ('bone','bone_dark','bone_light','bone_crack','bone_cart_mid1','bone_cart_mid2')};central='cartilage_dark'
    elif sty=='cloth_skin':
     converted={C(t)[:3] for t in ('skin','skin_dark','skin_light','cloth_mid1','cloth_mid2')};central='shirt'
    elif sty=='shirt_wound':
     converted={C(t)[:3] for t in ('shirt','shirt_dark','shirt_light','shirt_mid','wound_mid')};central='flesh'
    else:
     converted={C(t)[:3] for t in ('skin','skin_dark','skin_light','skin_mid','skin_flesh','wound_mid')};central='fluid' if sty=='sac' else 'flesh'
    for j in range(h):
     for i in range(w):
      # Uneven hand-designed wound edge rather than a concentric square frame.
      waves=((0,0,1,1,2,2,1,1,0,0,1,2,2,1,1,0),(1,1,0,0,1,2,2,1,0,0,0,1,1,2,2,1),(0,1,1,0,0,0,1,1,2,2,2,1,0,0,1,1),(2,1,0,0,1,1,1,0,0,1,2,2,1,1,0,1),(0,0,0,1,1,2,1,0,1,1,0,0,1,2,1,0))
      wave=waves[(f['variant']+f['cube'])%len(waves)];amplitude=1 if sty in ('mask','sac') else 2
      jag=lambda t: min(amplitude,wave[(t*16//w)%16])
      dist=min(i-jag(j),w-1-i-jag(j+3),j-jag(i+5),h-1-j-jag(i+8));old=self.base.getpixel((x+i,y+j))
      if dist<3:
       col=C(outer[max(0,dist)]);self.base.putpixel((x+i,y+j),(*col[:3],old[3]))
      elif old[3] and old[:3] in converted:
       col=C(central);self.base.putpixel((x+i,y+j),(*col[:3],old[3]))
   # Pale contact caps for the exposed cartilage knots, so the surrounding
   # bone meets the graduated side band rather than raw cartilage at a cube cut.
   if self.m.id=='b018' and sty=='cartilage' and side in ('top','bottom'):
    d=ImageDraw.Draw(self.base);d.rectangle((x,y,x+w-1,y+h-1),fill=C('bone'))
    oy=4+f['variant']%3;d.line([(x+4,y+oy),(x+6,y+oy),(x+6,y+oy+2)],fill=C('bone_crack'),width=1);d.line([(x+7,y+oy+3),(x+9,y+oy+3)],fill=C('bone_light'),width=1)
   # Joint-end skin caps retain a natural connection to underlying arms.
   if self.m.id=='b017' and bone=='forearm_left' and sty=='raw' and side in ('top','bottom'):
    d=ImageDraw.Draw(self.base);d.rectangle((x,y,x+w-1,y+h-1),fill=C('skin'))
    d.line([(x+4,y+4),(x+6,y+4),(x+6,y+6)],fill=C('skin_dark'),width=1);d.line([(x+8,y+7),(x+10,y+7)],fill=C('skin_light'),width=1)
   # Sleeve/collar end colors meet exposed zombie skin in base-off state too.
   if self.m.id=='b017' and sty=='shirt' and bone in ('torso','arm_right'):
    if side in ('front','back','left','right'):
     for j in range(h):
      dist=j if bone=='torso' else h-1-j
      if dist<3:
       col=C(('skin','cloth_mid2','cloth_mid1')[dist])
       for i in range(w):self.base.putpixel((x+i,y+j),col)
    if side==('top' if bone=='torso' else 'bottom'):
     for j in range(h):
      for i in range(w):self.base.putpixel((x+i,y+j),C('skin'))
 def apply_cross_contact_edits(self):
  # In-progress contact corrections derived from actual exported-geometry probes.
  # Absolute UV coordinates stay stable while cuboid count / pack order is fixed.
  from collections import defaultdict
  path=ROOT/'analysis_rev31'/'cross_contact_edits.json'
  if not path.exists():self.cross_contact_edits=0;return
  edits=json.loads(path.read_text()).get(self.m.id,{});self.cross_contact_edits=0
  if not edits:return
  groups=defaultdict(dict)
  for f in self.layout:groups[(f['bone'],f['cube'])][f['side']]=f
  mapped={}
  for _,faces in groups.items():
   byxyz=defaultdict(list)
   for side,f in faces.items():
    x,y,w,h=f['rect'];N=w-1
    for j in range(h):
     for i in range(w):
      xyz={'front':(i,N-j,N),'back':(N-i,N-j,0),'right':(N,N-j,N-i),'left':(0,N-j,i),'top':(i,N,j),'bottom':(i,0,N-j)}[side];byxyz[xyz].append((x+i,y+j))
   for points in byxyz.values():
    for pt in points:mapped[pt]=points
  for key,tone in edits.items():
   xy=tuple(map(int,key.split(',')));assert xy in mapped
   for point in mapped[xy]:
    old=self.base.getpixel(point);self.base.putpixel(point,(*C(tone)[:3],old[3]));self.cross_contact_edits+=1
 def paint_shoulder_stitch(self):
  # A sleeve-to-skin-to-infection strip on the inner shoulder, based on the
  # cuboid's local X coordinate. This makes the visual zone continuous through
  # every one of its six UV faces, not a row copied only onto one side.
  if self.m.id!='b017':return
  for f in self.layout:
   if f['bone']!='arm_left' or f['style'] not in ('skin','infection'):continue
   x,y,w,h=f['rect'];N=w-1;side=f['side']
   for j in range(h):
    for i in range(w):
     xx={'front':i,'back':N-i,'right':N,'left':0,'top':i,'bottom':i}[side]
     if f['style']=='skin':
      tone=('shirt','shirt','cloth_mid1','cloth_mid2')[xx] if xx<4 else None
     else:
      seq=('shirt','shirt','cloth_mid1','cloth_mid2','skin','skin','skin','skin_mid','skin_flesh')
      tone=seq[xx] if xx<len(seq) else None
     if tone:self.base.putpixel((x+i,y+j),C(tone))
 def normalise_surface_bands(self):
  # Geodesic transition normalization on the complete six-face surface graph
  # of each cuboid. This does not resolve contacts between separate cuboids.
  from collections import defaultdict,deque
  cats={'skin':('skin','skin_dark','skin_light'), 'flesh':('flesh','flesh_dark','flesh_light','vein','vein_light','fluid','fluid_light'), 'bone':('bone','bone_light','bone_dark','bone_crack'), 'cartilage':('cartilage','cartilage_dark'), 'cloth':('shirt','shirt_dark','shirt_light','pants','pants_dark','pants_light')}
  lut={C(k)[:3]:category for category,keys in cats.items() for k in keys}
  definitions=[('skin','flesh',('skin_mid','skin_flesh','wound_mid'),'skin_mid','skin_flesh','skin'),('bone','cartilage',('bone_cart_mid1','bone_cart_mid2'),'bone_cart_mid1','bone_cart_mid2','bone'),('skin','cloth',('cloth_mid1','cloth_mid2'),'cloth_mid2','cloth_mid1','skin')]
  groups=defaultdict(dict)
  for f in self.layout:groups[(f['bone'],f['cube'])][f['side']]=f
  self.normalised_nodes=0
  for _,g in groups.items():
   refs=defaultdict(list);adj=defaultdict(set)
   for side,f in g.items():
    x,y,w,h=f['rect'];assert w==h;N=w-1
    def xyz(i,j):return {'front':(i,N-j,N),'back':(N-i,N-j,0),'right':(N,N-j,N-i),'left':(0,N-j,i),'top':(i,N,j),'bottom':(i,0,N-j)}[side]
    for j in range(h):
     for i in range(w):
      p=xyz(i,j);refs[p].append((x+i,y+j))
      for ii,jj in ((i+1,j),(i,j+1)):
       if ii<w and jj<h:q=xyz(ii,jj);adj[p].add(q);adj[q].add(p)
   colors={p:self.base.getpixel(points[0]) for p,points in refs.items()}
   for iteration in range(2):
    for A,B,mids,midA,midB,baseA in definitions:
     MS={C(c)[:3] for c in mids};AS={p for p,c in colors.items() if c[3] and lut.get(c[:3])==A};BS={p for p,c in colors.items() if c[3] and lut.get(c[:3])==B};MM={p for p,c in colors.items() if c[3] and c[:3] in MS}
     if not AS or not BS or not MM:continue
     admissible=AS|BS|MM;d={p:0 for p in BS};queue=deque(BS)
     while queue:
      p=queue.popleft()
      for q in adj[p]:
       if q in admissible and q not in d:d[q]=d[p]+1;queue.append(q)
     updates={}
     for p in AS|MM:
      if p not in d:continue
      depth=d[p]
      if depth==1:updates[p]=midB
      elif depth==2:updates[p]=midA
      elif p in MM:updates[p]=baseA
     for p,name in updates.items():
      new=(*C(name)[:3],colors[p][3])
      if new!=colors[p]:
       colors[p]=new;self.normalised_nodes+=1
       for xy in refs[p]:self.base.putpixel(xy,new)
 def repair_direct_material_contacts(self):
  # Conservative first pass: analyse every intra-cuboid surface pixel, including
  # shared corner edges, and insert a two-pixel blend on direct semantic contact.
  # It does not detect contacts created by intersections of different cuboids.
  from collections import defaultdict
  cats={'skin':('skin','skin_dark','skin_light'), 'flesh':('flesh','flesh_dark','flesh_light','vein','vein_light','fluid','fluid_light'), 'bone':('bone','bone_light','bone_dark','bone_crack'), 'cartilage':('cartilage','cartilage_dark'), 'cloth':('shirt','shirt_dark','shirt_light','pants','pants_dark','pants_light')}
  lut={C(k)[:3]:category for category,keys in cats.items() for k in keys}
  transitions={frozenset(('skin','flesh')):{'skin':'skin_mid','flesh':'skin_flesh'},frozenset(('bone','cartilage')):{'bone':'bone_cart_mid1','cartilage':'bone_cart_mid2'},frozenset(('cloth','skin')):{'cloth':'cloth_mid1','skin':'cloth_mid2'}}
  groups=defaultdict(dict)
  for f in self.layout:groups[(f['bone'],f['cube'])][f['side']]=f
  self.semantic_repair_nodes=0
  for _,g in groups.items():
   refs=defaultdict(list);adj=defaultdict(set)
   for side,f in g.items():
    x,y,w,h=f['rect'];assert w==h;N=w-1
    def xyz(i,j):return {'front':(i,N-j,N),'back':(N-i,N-j,0),'right':(N,N-j,N-i),'left':(0,N-j,i),'top':(i,N,j),'bottom':(i,0,N-j)}[side]
    for j in range(h):
     for i in range(w):
      p=xyz(i,j);refs[p].append((x+i,y+j))
      for ii,jj in ((i+1,j),(i,j+1)):
       if ii<w and jj<h:q=xyz(ii,jj);adj[p].add(q);adj[q].add(p)
   colors={p:self.base.getpixel(points[0]) for p,points in refs.items()}
   for p,points in refs.items():assert all(self.base.getpixel(q)==colors[p] for q in points)
   for iteration in range(3):
    marks={}
    for a,neighbors in adj.items():
     ca=lut.get(colors[a][:3]) if colors[a][3] else None
     if not ca:continue
     for b in neighbors:
      cb=lut.get(colors[b][:3]) if colors[b][3] else None
      match=transitions.get(frozenset((ca,cb)))
      if cb and ca!=cb and match:
       marks[a]=match[ca];marks[b]=match[cb]
    if not marks:break
    self.semantic_repair_nodes+=len(marks)
    for point,name in marks.items():
     new=(*C(name)[:3],colors[point][3]);colors[point]=new
     for coord in refs[point]:self.base.putpixel(coord,new)
 def ensure_minimum_detail(self):
  # Restore connected two-tone detail on uniform underlying skin caps, without
  # contaminating base material or introducing unlisted colors.
  for f in self.layout:
   x,y,w,h=f['rect'];img=self.base.crop((x,y,x+w,y+h));colors={p[:3] for p in img.get_flattened_data() if p[3]}
   if len(colors)>=3:continue
   center=self.base.getpixel((x+w//2,y+h//2))[:3];d=ImageDraw.Draw(self.base)
   tones=('skin_dark','skin_light') if center in {C(t)[:3] for t in ('skin','skin_dark','skin_light')} else ('bone_crack','bone_light') if center in {C(t)[:3] for t in ('bone','bone_dark','bone_light')} else ('flesh_dark','flesh_light')
   if f['style']=='rootlet':
    a=(*C('ground')[:3],178);b=(*C('ground_dark')[:3],178);d.line([(x+2,y+2),(x+4,y+2),(x+4,y+4)],fill=a,width=1);d.line([(x+2,y+5),(x+5,y+5)],fill=b,width=1)
   else:
    a,b=(C(t) for t in tones);d.line([(x+4,y+4),(x+6,y+4),(x+6,y+6)],fill=a,width=1);d.line([(x+5,y+7),(x+7,y+7)],fill=b,width=1)
 def resolve_identical_art(self,protect_annotations=True):
  # A connected, branching material-specific mark differentiates otherwise
  # identical islands. It never changes UV borders or annotated transitions.
  # Explicit deterministic paths, no random seed, noise or isolated pixels.
  import itertools
  protected={tuple(pt) for sample in self.transitions if ['#%02X%02X%02X'%self.base.getpixel(tuple(q))[:3] for q in sample['coords']]==sample['colors'] for pt in sample['coords']} if protect_annotations else set()
  seen=set();self.distinct_art_repairs=0
  for f in self.layout:
   x,y,w,h=f['rect'];im=self.base.crop((x,y,x+w,y+h));key=(w,h,im.tobytes())
   if key not in seen:seen.add(key);continue
   sty=f['style'];ink='bone_crack' if sty in ('bone','bone_join','cartilage') else 'ground_dark' if sty=='rootlet' else 'flesh_light' if sty in ('raw','flesh','leg_wound','mask','sac','sinew','infection','shirt_wound') else 'shirt_dark' if sty in ('shirt','cloth_skin') else 'skin_dark' if sty in ('skin','leg_mix') else 'deep'
   center=im.getpixel((w//2,h//2))[:3]
   if center in {C(t)[:3] for t in ('skin','skin_dark','skin_light')}:ink='skin_dark'
   elif center in {C(t)[:3] for t in ('cartilage','cartilage_dark')}:ink='cartilage_dark' if center==C('cartilage')[:3] else 'cartilage'
   elif center in {C(t)[:3] for t in ('flesh','flesh_dark','flesh_light')}:ink='flesh_light'
   color=C(ink)
   if sty=='rootlet':color=(*color[:3],178)
   changed=False
   for selected in itertools.combinations(range(10),5):
    steps=set(selected);xx=1 if w==8 else 4;yy=h-2 if h==8 else h-5;pts=[(xx,yy)]
    for k in range(10):
     if k in steps:xx+=1
     else:yy-=1
     pts.append((xx,yy))
    if any((x+u,y+v) in protected for u,v in pts):continue
    candidate=im.copy();ImageDraw.Draw(candidate).line(pts,fill=color,width=1);k=(w,h,candidate.tobytes())
    if k not in seen:
     self.base.paste(candidate,(x,y));seen.add(k);self.distinct_art_repairs+=1;changed=True;break
   if not changed:raise ValueError(('Cannot distinguish island without touching transitions',self.m.id,f))
 def sync_cuboid_edges(self):
  # Explicit continuous details across the front/right angle on the major
  # underlying forms; this is in addition to exact edge-pixel agreement.
  from collections import defaultdict
  d=ImageDraw.Draw(self.base);groups=defaultdict(dict)
  for f in self.layout:groups[(f['bone'],f['cube'])][f['side']]=f
  for (bone,ci),g in groups.items():
   sty=g['front']['style']; special=((self.m.id=='b017' and ((bone=='head' and sty=='skin') or (bone=='torso' and sty=='shirt'))) or (self.m.id=='b019' and ((bone=='head' and sty=='skin') or (bone=='body' and sty=='skin'))) or (self.m.id=='b018' and ((bone=='head' and sty=='bone') or (bone=='spine' and sty=='bone'))))
   if special:
    a=g['front']['rect'];b=g['right']['rect'];x,y,w,h=a;rx,ry,rw,rh=b
    col=C('bone_crack' if sty=='bone' else 'shirt_dark' if sty=='shirt' else 'skin_dark'); level=max(3,h//3)
    # A branched, continuous notch/vein; coincident edge texel at (front right, right left).
    d.line([(x+w-6,y+level-3),(x+w-4,y+level-3),(x+w-3,y+level-1),(x+w-1,y+level)],fill=col,width=1)
    d.line([(rx,ry+level),(rx+2,ry+level+1),(rx+4,ry+level+1),(rx+5,ry+level+3)],fill=col,width=1)
    d.line([(rx+2,ry+level+1),(rx+3,ry+level-1)],fill=col,width=1)
   # Group matching image-border texels by local xyz lattice coordinates.
   # All faces of this cube have the same grid dimensions.
   groups3=defaultdict(list);order={'front':0,'back':1,'right':2,'left':3,'top':4,'bottom':5}
   for side,f in g.items():
    x,y,w,h=f['rect'];assert w==h;N=w-1
    for j in range(h):
     for i in range(w):
      if i not in (0,N) and j not in (0,N):continue
      xyz={'front':(i,N-j,N),'back':(N-i,N-j,0),'right':(N,N-j,N-i),'left':(0,N-j,i),'top':(i,N,j),'bottom':(i,0,N-j)}[side]
      groups3[xyz].append((order[side],x+i,y+j))
   for xyz,locations in groups3.items():
    assert len(locations) in (2,3)
    _,sx,sy=min(locations);color=self.base.getpixel((sx,sy))
    for _,tx,ty in locations:self.base.putpixel((tx,ty),color)
 def uv(self,bone,ci,side):
  x,y,w,h=self.lookup[(bone,ci,side)]['rect'];S=self.size
  return ((x+.5)/S,(y+.5)/S,(x+w-.5)/S,(y+h-.5)/S)
 def paint(self,f,i):
  x,y,w,h=f['rect']; sty=f['style'];v=f['variant'];side=f['side'];bone=f['bone'];face=f['face'];glow=f['glow']
  base,hi,shade=TYPES[sty]; d=ImageDraw.Draw(self.base);gp=ImageDraw.Draw(self.glow)
  # Each face has its own colored island. Shapes are connected paths, not random dots.
  d.rectangle((x,y,x+w-1,y+h-1),fill=C(base))
  # Hand-authored motifs, offset by surface to prevent exact copy/paste; no randomness.
  motifs=[[(1,1),(3,1),(3,3),(5,4),(6,6)],[(1,5),(2,4),(4,4),(4,2),(6,1)],[(1,2),(2,3),(4,3),(5,5),(6,5)],[(1,6),(2,5),(2,3),(4,2),(6,2)],[(1,3),(3,2),(4,2),(5,3),(6,4)],[(1,1),(2,2),(2,4),(4,5),(6,5)],[(1,5),(3,5),(3,3),(4,2),(6,2)],[(1,2),(3,3),(3,4),(5,4),(6,5)]]
  ox=(i//8)%3-1; oy=(i//24)%3-1
  pts=[(x+max(1,min(w-2,round((a+ox)*w/8))),y+max(1,min(h-2,round((b+oy)*h/8)))) for a,b in motifs[i%8]]
  linecol=C('bone_crack') if sty=='bone' else C(shade)
  d.line(pts,fill=linecol,width=max(1,w//24));
  hi_pts=[(min(x+w-2,px+max(1,w//16)),py) for px,py in pts[:3]];d.line(hi_pts,fill=C(hi),width=1)
  if sty not in ('infection','shirt_wound','bone_join','cloth_skin','rootlet') and not (side=='front' and face in ('creeper_face','mask_face','skull_face')):
   # A continuous crease/cut with face-specific endpoints, not isolated noise.
   sy=1+(i%6)*(h-3)//5; my=1+((i//6)%6)*(h-3)//5; ey=1+((i//36)%6)*(h-3)//5
   d.line([(x+1,y+sy),(x+w//2,y+my),(x+w-2,y+ey)],fill=C(shade),width=1)
  if sty in ('infection','shirt_wound','bone_join','cloth_skin'):
   # Exact hand-specified 2-texel bridge for every pixel row of this island.
   colors={'infection':['skin','skin_mid','skin_flesh','flesh'], 'shirt_wound':['shirt','shirt_mid','wound_mid','flesh'], 'bone_join':['bone','bone_cart_mid1','bone_cart_mid2','cartilage'], 'cloth_skin':['shirt','cloth_mid1','cloth_mid2','skin']}[sty]
   for yy in range(h):
    cut=w//2 + ([0,0,1,1,0,-1,-1,0][((yy*8//h)+i)%8])*max(1,w//16)
    if sty=='shirt_wound' and (w>=16 or side=='front'):
     edge=([0,1,2,3,2,1,0,1][((yy*8//h)+i)%8]) if w>=16 else 0
     for xx in range(w):
      distance=min(xx,w-1-xx)-edge;col=colors[max(0,min(3,distance))]
      self.base.putpixel((x+xx,y+yy),C(col))
     coords=[[x+edge+k,y+yy] for k in range(4)]
     self.transitions.append({'bone':bone,'cube':f['cube'],'side':side,'coords':coords,'colors':[P[t].upper() for t in colors]})
    else:
     for xx in range(w):
      col=colors[0] if xx<cut-1 else colors[1] if xx==cut-1 else colors[2] if xx==cut else colors[3]
      self.base.putpixel((x+xx,y+yy),C(col))
     if 1<=cut<w-1:self.transitions.append({'bone':bone,'cube':f['cube'],'side':side,'coords':[[x+cut-2,y+yy],[x+cut-1,y+yy],[x+cut,y+yy],[x+cut+1,y+yy]],'colors':[P[t].upper() for t in colors]})
  if sty=='rootlet':
   # Transparent support plane, three roots, alpha 0.5–0.7.
   # The geometry itself is a narrow root rod. Alpha covers its whole island,
   # eliminating transparent padding inside its UV allocation.
   d.rectangle((x,y,x+w-1,y+h-1),fill=(*C('ground_light')[:3],178))
   y0=y+2+(i%3);x0=x+2+((i//3)%3)
   d.line([(x0,y0),(x0+1,y0),(x0+1,y0+2)],fill=(*C('ground_light')[:3],178),width=1)
   d.line([(x+1,y+h-2),(x+w-2,y+h-2)],fill=(*C('ground_dark')[:3],178),width=1)
  if bone=='head' and self.m.id=='b017' and side=='top':
   d.rectangle((x,y,x+w-1,y+max(2,h//3)),fill=C('pants_dark'))
  if self.m.id=='b017' and bone in ('leg_left','leg_right') and sty=='pants' and side=='front':
   xx=x+w//2;yy=y+h*2//3
   d.rectangle((xx-2,yy-2,xx+2,yy+2),fill=C('skin'))
   d.line([(xx-3,yy-2),(xx-1,yy-3),(xx+2,yy-2)],fill=C('pants_light'),width=1)
  if sty=='leg_mix':
   # Green limb to flesh pad, with a two-pixel intermediate band.
   ycut=y+h*2//3
   d.line((x,ycut-1,x+w-1,ycut-1),fill=C('skin'),width=1)
   d.rectangle((x,ycut+2,x+w-1,y+h-1),fill=C('flesh_dark'))
   d.line((x,ycut,x+w-1,ycut),fill=C('skin_flesh'),width=1)
   d.line((x,ycut+1,x+w-1,ycut+1),fill=C('wound_mid'),width=1)
   for xx in range(x,x+w):
    if ycut>y and ycut+2<y+h:
     self.transitions.append({'bone':bone,'cube':f['cube'],'side':side,'coords':[[xx,ycut-1],[xx,ycut],[xx,ycut+1],[xx,ycut+2]],'colors':[P['skin'].upper(),P['skin_flesh'].upper(),P['wound_mid'].upper(),P['flesh_dark'].upper()]})
  if sty=='leg_wound':
   if side in ('front','back','left','right'):
    for yy in range(h):
     tone=['skin','skin_mid','skin_flesh','flesh_dark'][min(yy,3)]
     d.line((x,y+yy,x+w-1,y+yy),fill=C(tone),width=1)
    # Connected knot, uniquely positioned on each face; stays away from edges.
    ox=2+(i%5);oy=5+((i//5)%4)
    d.line([(x+ox,y+oy),(x+ox+2,y+oy),(x+ox+2,y+oy+2),(x+ox+3,y+oy+2)],fill=C('flesh_light'),width=1)
    for xx in range(1,w-1):
     self.transitions.append({'bone':bone,'cube':f['cube'],'side':side,'coords':[[x+xx,y+k] for k in range(4)],'colors':[P[t].upper() for t in ('skin','skin_mid','skin_flesh','flesh_dark')]})
   elif side=='top':
    d.rectangle((x,y,x+w-1,y+h-1),fill=C('skin'))
    ox=2+(i%5);oy=2+((i//5)%5);d.line([(x+ox,y+oy),(x+ox+2,y+oy),(x+ox+2,y+oy+2)],fill=C('skin_dark'),width=1)
   else:
    d.rectangle((x,y,x+w-1,y+h-1),fill=C('flesh_dark'))
    ox=2+(i%5);oy=2+((i//5)%5);d.line([(x+ox,y+oy),(x+ox+2,y+oy),(x+ox+2,y+oy+2)],fill=C('flesh_light'),width=1)
  if sty=='sinew':
   # Woven ropes vary in span and thickness through separate cuboid proportions and variant.
   y0=y+h//2;steps=4+v%3
   a=[];b=[]
   for z in range(steps+1):
    xx=x+1+round((w-3)*z/steps);dy=(-1 if z%2 else 1)*max(1,h//5)
    a.append((xx,y0+dy));b.append((xx,y0-dy))
   d.line(a,fill=C('sinew_dark'),width=max(1,h//5));d.line(b,fill=C('vein_light'),width=max(1,h//8))
   for z in range(1,2+v%2):
    xx=x+round(w*z/(2+v%2));d.rectangle((xx,y0-1,xx+1,y0+1),fill=C('vein'))
  if sty=='bone':
   d.line(pts,fill=C('bone_crack'),width=1);d.line([(x+1,y+1),(x+w//3,y+1)],fill=C('bone_light'),width=1)
  if sty=='eye' and side=='front':
   d.rectangle((x+2,y+2,x+w-3,y+h-3),fill=C('glow'))
   if glow:gp.rectangle((x+2,y+2,x+w-3,y+h-3),fill=C('glow'))
  if face=='zombie_face' and side=='front':
   for ax in (2,5):
    x0=x+w*ax//8-w//10;y0=y+h//3
    d.rectangle((x0,y0,x0+w//6,y0+h//8),fill=C('deep'))
   d.line([(x+w*3//8,y+h*3//4),(x+w*5//8,y+h*3//4)],fill=C('skin_dark'),width=max(1,w//16))
  if face=='skull_face' and side=='front':
   for ax in (2,5):
    x0=x+w*ax//8-w//10;y0=y+h//3
    d.rectangle((x0,y0,x0+w//5,y0+h//5),fill=C('shadow'))
    if glow:
     d.rectangle((x0+w//12,y0+h//14,x0+w//12+1,y0+h//14+1),fill=C('glow'));gp.rectangle((x0+w//12,y0+h//14,x0+w//12+1,y0+h//14+1),fill=C('glow'))
   d.line([(x+w//2,y+h//2),(x+w//2-1,y+h*5//8)],fill=C('bone_crack'),width=1)
   for j in range(5):
    xx=x+w*(j+2)//9;d.line([(xx,y+h*3//4),(xx,y+h*7//8)],fill=C('bone_dark'),width=1)
  if face=='mask_face' and side=='front':
   for j in range(3):
    yy=y+h*(j+2)//6;d.line([(x+1,yy),(x+w-2,yy-1)],fill=C('flesh_light'),width=max(1,h//16));d.line([(x+1,yy+1),(x+w-2,yy)],fill=C('flesh_dark'),width=1)
   for ax in (2,5):
    xx=x+w*ax//8;yy=y+h*3//8;d.rectangle((xx-1,yy-1,xx+1,yy+1),fill=C('deep'))
    if glow:
     d.line((xx-1,yy,xx+1,yy),fill=C('glow2'),width=1);gp.line((xx-1,yy,xx+1,yy),fill=C('glow2'),width=1)
  # Mask contact rim is painted later in shared cuboid coordinates.
  if face=='creeper_face' and side=='front':
   # Large vanillalike creeper eyes and signature stepped mouth.
   for ax in (1,5):
    x0=x+w*ax//8;y0=y+h//4;sw=w//4;sh=h//5
    d.rectangle((x0,y0,x0+sw,y0+sh),fill=C('face_dark'))
    if glow:
     d.rectangle((x0+sw//2,y0+sh//2,x0+sw//2+1,y0+sh//2+1),fill=C('glow'));gp.rectangle((x0+sw//2,y0+sh//2,x0+sw//2+1,y0+sh//2+1),fill=C('glow'))
   # Vanilla-style inverted-V mouth occupying lower half.
   cx=x+w//2;yy=y+h*5//8;th=max(2,w//8)
   d.rectangle((cx-th//2,yy-th,cx+th//2,yy+th),fill=C('shadow'))
   d.rectangle((cx-th*2,yy,cx-th//2,yy+th*2),fill=C('shadow'))
   d.rectangle((cx+th//2,yy,cx+th*2,yy+th*2),fill=C('shadow'))
   # Red accent resides only on the separate infected jaw.
  if glow and not ((face in ('creeper_face','mask_face','skull_face')) and side=='front'):
   # Sac, whip and nerve island are separate; only their visible face contains light.
   if side=='front' or sty in ('sac','sinew'):
    color='vein_light' if sty=='sinew' else 'glow';cx=x+w//2;cy=y+h//2
    gp.line([(cx-1,cy),(cx+1,cy)],fill=C(color),width=1)
  if sty!='rootlet' and len(set(self.base.crop((x,y,x+w,y+h)).get_flattened_data()))<3:
   d.line([(x+1,y+1),(x+2,y+1)],fill=C(hi),width=1)
  self.tiles.append([bone,f['cube'],side,sty,f['rect']])


def export(m):
 binary=bytearray();views=[];access=[]
 def append(data,target=None):
  while len(binary)%4:binary.append(0)
  off=len(binary);binary.extend(data);view={'buffer':0,'byteOffset':off,'byteLength':len(data)}
  if target:view['target']=target
  views.append(view);return len(views)-1
 def floats(data,typ,dim,target=None,limits=False):
  flat=[float(x) for row in data for x in (row if isinstance(row,(list,tuple)) else (row,))]
  vi=append(struct.pack('<'+'f'*len(flat),*flat),target)
  a={'bufferView':vi,'componentType':5126,'count':len(data),'type':typ}
  if limits:
   rows=[(r,) if isinstance(r,(int,float)) else r for r in data]
   a['min']=[min(row[i] for row in rows) for i in range(dim)];a['max']=[max(row[i] for row in rows) for i in range(dim)]
  access.append(a);return len(access)-1
 def indices(data):
  vi=append(struct.pack('<'+'H'*len(data),*data),34963);access.append({'bufferView':vi,'componentType':5123,'count':len(data),'type':'SCALAR'});return len(access)-1
 glnodes=[];meshes=[]
 m.atlas=FaceAtlas(m)
 for node in m.nodes:
  px,py,pz=node['pivot'];parent=node['parent'];par=m.nodes[m.byname[parent]]['pivot'] if parent else (0,0,0)
  gn={'name':node['name'],'translation':[node['pivot'][j]-par[j] for j in range(3)]}
  restroll = {'arm_left':.14,'arm_right':-.14,'arm_blade':-.14,'arm_whip':.14}.get(node['name'],0.0)
  if restroll: gn['rotation'] = quat((0,0,restroll))
  # Partition healthy and infectious shapes by primitive, retaining exact bone names.
  groups={}
  for ci,cube in enumerate(node['cubes']):
   sty=cube[2];name=node['name']
   infectious=(sty in ('raw','flesh','sac','sinew','infection','shirt_wound','bone_join','leg_wound','eye','whip_glow','tail_glow','mask','rootlet') or name in ('mask','chest_growth') or (m.id=='b017' and name in ('arm_left','forearm_left','leg_right') and sty in ('crust','bone')))
   mi=2 if m.id=='b019' and (name in ('sac_left','sac_right','sac_back') or sty=='tail_glow') else (1 if infectious else 0)
   groups.setdefault(mi,[]).append((ci,cube))
  primitives=[]
  for material,cubes in sorted(groups.items()):
   pos=[];norm=[];uv=[];ind=[]
   for ci,(center,size,style,var,face,glow) in cubes:
    x,y,z=[center[i]-node['pivot'][i] for i in range(3)];a,b,c=[v/2 for v in size]
    # Quad corners wound counter-clockwise, viewed from outside.
    faces=[('front',(0,0,1),[(x-a,y-b,z+c),(x+a,y-b,z+c),(x+a,y+b,z+c),(x-a,y+b,z+c)]),
           ('back',(0,0,-1),[(x+a,y-b,z-c),(x-a,y-b,z-c),(x-a,y+b,z-c),(x+a,y+b,z-c)]),
           ('right',(1,0,0),[(x+a,y-b,z+c),(x+a,y-b,z-c),(x+a,y+b,z-c),(x+a,y+b,z+c)]),
           ('left',(-1,0,0),[(x-a,y-b,z-c),(x-a,y-b,z+c),(x-a,y+b,z+c),(x-a,y+b,z-c)]),
           ('top',(0,1,0),[(x-a,y+b,z+c),(x+a,y+b,z+c),(x+a,y+b,z-c),(x-a,y+b,z-c)]),
           ('bottom',(0,-1,0),[(x-a,y-b,z-c),(x+a,y-b,z-c),(x+a,y-b,z+c),(x-a,y-b,z+c)])]
    for side,n,verts in faces:
     textureface=face if side=='front' else 'side'
     # Face patterns on eyes only on the front; sac/sinew light is available around the form.
     light=glow and (side=='front' or style in ('sac','sinew'))
     u0,v0,u1,v1=m.atlas.uv(node['name'],ci,side);k=len(pos)
     pos.extend(verts);norm.extend([n]*4);uv.extend([(u0,v1),(u1,v1),(u1,v0),(u0,v0)]);ind.extend([k,k+1,k+2,k,k+2,k+3])
   if pos:
    primitives.append({'attributes':{'POSITION':floats(pos,'VEC3',3,34962,True),'NORMAL':floats(norm,'VEC3',3,34962),'TEXCOORD_0':floats(uv,'VEC2',2,34962)},'indices':indices(ind),'material':material})
  if primitives:
   meshes.append({'name':node['name']+'_mesh','primitives':primitives});gn['mesh']=len(meshes)-1
  glnodes.append(gn)
 for idx,node in enumerate(m.nodes):
  if node['parent']:
   gn=glnodes[m.byname[node['parent']]];gn.setdefault('children',[]).append(idx)
 anims=[]
 for name,T,mode in ANIMS[m.id]:
  nframes=round(T*20);ts=[i/20 for i in range(nframes+1)]
  keyframes=[controls(m.id,name,t,T) for t in ts];keys=sorted(set(k for fr in keyframes for k in fr))
  ai=floats(ts,'SCALAR',1,limits=True);samplers=[];channels=[]
  for bone,path in keys:
   if bone not in m.byname:raise ValueError((name,bone))
   data=[]
   for fr in keyframes:
    if path=='rotation':
     angles=fr.get((bone,path),(0,0,0)); restroll={'arm_left':.14,'arm_right':-.14,'arm_blade':-.14,'arm_whip':.14}.get(bone,0.0)
     data.append(quat((angles[0],angles[1],angles[2]+restroll)))
    elif path=='scale':data.append(fr.get((bone,path),(1,1,1)))
    else:
     bidx=m.byname[bone];rest=glnodes[bidx]['translation'];off=fr.get((bone,path),(0,0,0));data.append(tuple(rest[i]+off[i] for i in range(3)))
   out=floats(data,'VEC4' if path=='rotation' else 'VEC3',4 if path=='rotation' else 3)
   samplers.append({'input':ai,'output':out,'interpolation':'LINEAR'});channels.append({'sampler':len(samplers)-1,'target':{'node':m.byname[bone],'path':path}})
  anims.append({'name':name,'samplers':samplers,'channels':channels,'extras':{'fps':20,'loop':mode=='loop','duration':T}})
 def pngbytes(im):
  mem=io.BytesIO();im.save(mem,format='PNG');return mem.getvalue()
 m.atlas.base.save(OUT/(m.id+'.png'));m.atlas.glow.save(OUT/(m.id+'_glow.png'))
 views_image=[append(pngbytes(im)) for im in (m.atlas.base,m.atlas.glow)]
 doc={'asset':{'version':'2.0','generator':'Carnis TZ3 Python authoring (not Tabula)'},'scene':0,'scenes':[{'nodes':[m.byname['root']]}],
      'nodes':glnodes,'meshes':meshes,'animations':anims,
      'materials':[
       {'name':'healthy_base','pbrMetallicRoughness':{'baseColorTexture':{'index':0},'metallicFactor':0,'roughnessFactor':.85},'alphaMode':'BLEND','emissiveTexture':{'index':1},'emissiveFactor':[1,1,1]},
       {'name':'infection_overlay','pbrMetallicRoughness':{'baseColorTexture':{'index':0},'metallicFactor':0,'roughnessFactor':.85},'alphaMode':'BLEND','emissiveTexture':{'index':1},'emissiveFactor':[1,1,1]},
       {'name':'sac_charge_runtime','pbrMetallicRoughness':{'baseColorTexture':{'index':0},'metallicFactor':0,'roughnessFactor':.85},'alphaMode':'BLEND','emissiveTexture':{'index':1},'emissiveFactor':[0,0,0]}],
      'textures':[{'sampler':0,'source':0},{'sampler':0,'source':1}],
      'samplers':[{'magFilter':9728,'minFilter':9728,'wrapS':33071,'wrapT':33071}],
      'images':[{'bufferView':views_image[0],'mimeType':'image/png','name':m.id},{'bufferView':views_image[1],'mimeType':'image/png','name':m.id+'_glow'}],
      'buffers':[{'byteLength':len(binary)}],'bufferViews':views,'accessors':access}
 if m.id != 'b019': doc['materials'].pop()
 raw=json.dumps(doc,separators=(',',':'),ensure_ascii=False).encode();raw+=b' '*((-len(raw))%4);binary.extend(b'\0'*((-len(binary))%4))
 glb=struct.pack('<4sII',b'glTF',2,12+8+len(raw)+8+len(binary))+struct.pack('<I4s',len(raw),b'JSON')+raw+struct.pack('<I4s',len(binary),b'BIN\0')+binary
 (OUT/(m.id+'.glb')).write_bytes(glb)
 return doc

def rest_bounds(m):
 """AABB of vertices in articulated rest pose (x,y,z), including bone roll."""
 frames=[]; points=[]
 for n in m.nodes:
  p=n['pivot']; parent=n['parent']; pp=m.nodes[m.byname[parent]]['pivot'] if parent else (0.,0.,0.)
  if parent: ox,oy,oz,ang=frames[m.byname[parent]]
  else: ox,oy,oz,ang=0.,0.,0.,0.
  dx,dy,dz=(p[i]-pp[i] for i in range(3)); cc,ss=math.cos(ang),math.sin(ang)
  ox,oy,oz=ox+cc*dx-ss*dy,oy+ss*dx+cc*dy,oz+dz
  ang += {'arm_left':.14,'arm_right':-.14,'arm_blade':-.14,'arm_whip':.14}.get(n['name'],0.)
  frames.append((ox,oy,oz,ang));cc,ss=math.cos(ang),math.sin(ang)
  for center,size,*_ in n['cubes']:
   for sx in (-.5,.5):
    for sy in (-.5,.5):
     for sz in (-.5,.5):
      x,y,z=(center[i]-p[i]+size[i]*v for i,v in enumerate((sx,sy,sz)))
      points.append((ox+cc*x-ss*y,oy+ss*x+cc*y,oz+z))
 return [[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)]

def fit_rest(m):
 """Fit rest pose into strict centered hitbox; not a motion-volume guarantee."""
 height={'b017':1.95,'b018':1.99,'b019':1.70}[m.id]
 allowed=[(-.2995,.2995),(.0001,height-.0005),(-.2995,.2995)]
 for iteration in range(12):
  changed=False
  for axis,(lo,hi) in enumerate(allowed):
   a,b=rest_bounds(m)[axis]; target=hi-lo; width=b-a
   if width<=target+1e-7 and a>=lo-1e-7 and b<=hi+1e-7:continue
   factor=min(1.,target/width*.999); offset=(lo-factor*a) if axis==1 else ((lo+hi)/2-factor*(a+b)/2)
   for node in m.nodes:
    if node['parent'] is not None:
     p=list(node['pivot']);p[axis]=p[axis]*factor+offset;node['pivot']=tuple(p)
    new=[]
    for center,size,style,var,face,glow in node['cubes']:
     center=list(center);size=list(size);center[axis]=center[axis]*factor+offset;size[axis]*=factor
     new.append((tuple(center),tuple(size),style,var,face,glow))
    node['cubes']=new
   changed=True
  if not changed:break
 # B019's body translation channel uses an absolute node position. Pin its
 # accepted rest pivot so the attack key buffer remains byte-for-byte unchanged.
 if m.id=='b019':
  body=m.nodes[m.byname['body']];bp=list(body['pivot']);bp[2]=.024499999999999966;body['pivot']=tuple(bp)
 bounds=rest_bounds(m)
 assert all(bounds[i][0]>=lo-1e-5 and bounds[i][1]<=hi+1e-5 for i,(lo,hi) in enumerate(allowed)),(m.id,bounds)
 return bounds

def write_animation_json(m):
 """Flat contract names in top-level animations; channel values derived from GLB controls."""
 result={'format_version':'1.8.0','animations':{}}
 for name,T,mode in ANIMS[m.id]:
  frames=[controls(m.id,name,i/20,T) for i in range(round(T*20)+1)]
  keys=sorted(set(k for f in frames for k in f));bones={}
  for bone,path in keys:
   track={}
   for i,fr in enumerate(frames):
    value=fr.get((bone,path),(1,1,1) if path=='scale' else (0,0,0))
    if path=='rotation':value=[round(math.degrees(v),5) for v in value]
    elif path=='translation':value=[round(v*16,5) for v in value]
    else:value=[round(v,5) for v in value]
    track[f'{i/20:.2f}']=value
   bones.setdefault(bone,{})['position' if path=='translation' else path]=track
  result['animations'][name]={'loop':mode=='loop','animation_length':T,'bones':bones}
 (OUT/(m.id+'.animation.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')

def revise(m):
 """Replace the rejected geometry while retaining the approved named hierarchy."""
 fit_rest(m)
 for n in m.nodes:n['cubes']=[]
 m.cubes=[]
 c=m.cube
 if m.id=='b017':
  c('torso',(-.034,1.22,0),(.27,.59,.19),'shirt',0)
  c('torso',(.025,1.27,.101),(.20,.30,.012),'shirt_wound',1)
  c('head',(-.034,1.68,0),(.29,.32,.24),'skin',1,'zombie_face')
  c('jaw',(-.034,1.52,.064),(.23,.06,.12),'skin',3)
  # Single shell face carries rags, slits and horizontal ridges in unique pixels.
  c('mask',(-.034,1.70,.20),(.26,.25,.15),'mask',0,'mask_face',True)
  c('mask',(-.10,1.89,.08),(.08,.11,.10),'sac',1,'side',True)
  c('mask',(.03,1.90,.08),(.09,.11,.10),'sac',2,'side',True)
  c('chest_growth',(.025,1.27,.13),(.075,.16,.075),'raw',1,'side',True)
  c('arm_right',(-.18,1.30,0),(.095,.26,.13),'shirt',1)
  c('forearm_right',(-.18,1.035,.0),(.085,.31,.12),'skin',1)
  c('arm_left',(.15,1.30,0),(.075,.24,.105),'skin',4)
  c('arm_left',(.15,1.32,0),(.13,.22,.15),'infection',1)
  c('forearm_left',(.17,1.045,0),(.075,.32,.105),'skin',4)
  c('forearm_left',(.17,1.02,0),(.15,.28,.15),'raw',2,'side',True)
  # Bulging out of the outer silhouette; points to the right of the arm.
  c('forearm_left',(.245,.90,.02),(.085,.16,.14),'crust',1)
  # Paired unequal talons: a clear notched silhouette rather than a flat patch.
  c('forearm_left',(.215,.795,.035),(.035,.11,.08),'crust',2)
  c('forearm_left',(.275,.77,.035),(.035,.16,.08),'crust',3)
  for side,x in [('left',.025),('right',-.093)]:
   c('leg_'+side,(x,.52,0),(.11,.76,.15),'pants',1 if side=='left' else 2)
   c('foot_'+side,(x,.085,.025),(.11,.13,.21),'pants',2)
   c('foot_'+side,(x,.008,.105),(.014,.016,.10),'rootlet',0)
   c('foot_'+side,(x-.03,.0082,.115),(.065,.0158,.014),'rootlet',1)
   c('foot_'+side,(x+.025,.0084,.085),(.06,.0158,.014),'rootlet',2)
  # Previous bone-colored injury is deliberately absent.
 elif m.id=='b018':
  c('pelvis',(.008,.9,0),(.21,.12,.13),'bone',1)
  c('spine',(.008,1.28,-.015),(.055,.52,.07),'bone',0)
  c('spine',(.008,1.05,-.015),(.09,.08,.075),'cartilage',1)
  c('head',(.008,1.76,-.005),(.22,.36,.20),'bone',1,'skull_face',False)
  for ex in (-.055,.055):c('head',(.008+ex,1.79,.101),(.035,.04,.012),'eye',1,'side',True)
  c('jaw',(.008,1.59,.065),(.19,.06,.12),'bone',2,'jaw_face')
  for i,y in enumerate([1.45,1.31,1.17],1):
   for side,sgn in [('left',1),('right',-1)]:
    k=[1.,.82,.64][i-1];c('rib_'+side+'_'+str(i),(.008+sgn*.075,y,.02),(.14*k,.055-(i-1)*.009,.12),'bone',i)
  # Removed a fully buried cartilage cuboid; the six rib bones remain.
  # Distinct lengths, thickness and rhythm: top = two long sections,
  # mid = offset knot, bottom = shorter fork.
  for n,y,w,h,z,v in [('sinew_top',1.405,.22,.055,.10,0),('sinew_mid',1.265,.17,.07,.112,1),('sinew_bot',1.125,.12,.042,.108,2)]:
   c(n,(.008,y,z),(w,h,.05),'sinew',v,'side',True)
  c('sinew_top',(-.05,1.405,.14),(.035,.075,.035),'sinew',1,'side',True)
  c('sinew_mid',(.04,1.265,.15),(.045,.085,.035),'sinew',2,'side',True)
  c('sinew_bot',(-.025,1.12,.14),(.035,.06,.035),'sinew',3,'side',True)
  c('arm_blade',(-.14,1.34,0),(.065,.27,.08),'bone',2)
  c('forearm_blade',(-.15,1.03,0),(.07,.30,.08),'bone',3)
  c('forearm_blade',(-.16,.84,.02),(.11,.14,.07),'bone',4,'blade_face')
  c('arm_whip',(.15,1.34,0),(.065,.27,.08),'bone',1)
  for n,y,w in [('whip_seg1',1.10,.07),('whip_seg2',.87,.05),('whip_seg3',.65,.035)]:
   c(n,(.155,y,0),(w*.60,.23,w*.60),'bone',2)
   c(n,(.155,y,0),(w,.229,w),'whip_glow',1,'side',True)
  for side,x in [('left',.06),('right',-.045)]:
   c('leg_'+side,(x,.50,0),(.055,.74,.075),'bone',2)
   c('leg_'+side,(x,.50,.004),(.08,.085,.08),'cartilage',1)
   c('foot_'+side,(x,.07,.025),(.085,.12,.19),'bone',2)
   c('foot_'+side,(x,.008,.09),(.012,.016,.09),'rootlet',0)
   c('foot_'+side,(x-.022,.0082,.10),(.05,.0158,.012),'rootlet',1)
   c('foot_'+side,(x+.02,.0084,.075),(.05,.0158,.012),'rootlet',2)
 else:
  c('body',(0,.76,0),(.36,.66,.27),'skin',0)
  c('body',(.07,.78,.138),(.20,.30,.006),'infection',1)
  # A true near-cubic head: its whole front is a single painted island.
  c('head',(0,1.385,0),(.56,.56,.56),'skin',0,'creeper_face',False)
  for ex in (-.14,.14):c('head',(ex,1.47,.282),(.06,.06,.012),'eye',1,'side',True)
  c('head',(.18,1.55,.286),(.12,.10,.012),'raw',1)
  c('jaw',(0,1.245,.27),(.10,.04,.04),'flesh',1)
  c('sac_left',(.125,1.00,-.21),(.11,.17,.15),'sac',1,'side',True)
  c('sac_right',(-.125,1.00,-.21),(.11,.17,.15),'sac',2,'side',True)
  c('sac_back',(0,.79,-.21),(.20,.22,.15),'sac',3,'side',True)
  # Stagger two anatomical side rows in depth so their six projections separate
  # at 45 degrees while all individual leg bones/pivots and animations stay intact.
  leg_z={1:.23,2:.06,3:.085,4:-.085,5:-.06,6:-.23}
  for i in range(1,7):
   n=m.nodes[m.byname['leg_'+str(i)]];oldx,py,_=n['pivot'];x=math.copysign(.19,oldx);z=leg_z[i];n['pivot']=(x,py,z);sx=.085 if i<=2 else .065
   c('leg_'+str(i),(x,.225,z),(sx,.41,.043),'skin',i%5)
   # Hip volumes bridge each leg into the body in the rest pose.
   inner=max(-.11,min(.11,z));c('leg_'+str(i),(x,.405,(z+inner)/2),(sx,.08,abs(z-inner)+.06),'skin',(i+1)%5)
   c('leg_'+str(i),(x,.104,z),(sx+.004,.13,.047),'leg_wound',i%5)
   rz=min(.235,z+.04)
   c('leg_'+str(i),(x,.008,rz),(.012,.016,.10),'rootlet',0)
   c('leg_'+str(i),(x-.026,.0082,rz+.02),(.06,.0158,.012),'rootlet',1)
   c('leg_'+str(i),(x+.024,.0084,rz-.015),(.055,.0158,.012),'rootlet',2)
  c('tail',(0,.60,-.225),(.05,.055,.12),'skin',1)
  c('tail',(0,.59,-.29),(.03,.04,.02),'tail_glow',1,'side',True)
 return m


if __name__=='__main__':
 models=[revise(humanoid('b017')),revise(humanoid('b018')),revise(creeper())]
 for m in models:
  bounds=fit_rest(m);write_animation_json(m)
  doc=export(m);print(m.id,'bones',len(m.nodes),'cubes',len(m.cubes),'tiles',len(m.atlas.tiles),'animations',len(doc['animations']))
  data={'id':m.id,'label':m.label,'bones':[{'name':n,'role':r} for n,r in m.meta],'animations':[{'name':n,'duration':t,'mode':mode} for n,t,mode in ANIMS[m.id]],'tiles':m.atlas.tiles,'uv_layout':m.atlas.layout,'transition_samples':m.atlas.transitions,'transition_invalidated_by_seams':len(m.atlas.transition_invalidated),'distinct_art_repairs':m.atlas.distinct_art_repairs,'semantic_repair_nodes':m.atlas.semantic_repair_nodes,'normalised_nodes':m.atlas.normalised_nodes,'cross_contact_edits':m.atlas.cross_contact_edits,'uv_unused_texels':m.atlas.unused,'rest_bounds':bounds,'hitbox':[0.6,{'b017':1.95,'b018':1.99,'b019':1.70}[m.id],0.6]}
  (OUT/(m.id+'_data.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
