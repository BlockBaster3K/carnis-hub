#!/usr/bin/env python3
"""Carnis TZ-3 phase 3.1. Procedural assembly of manually positioned cuboids,
hand-authored pixel swatches, bones, and 20 fps keyframes into glTF 2.0 GLB.
No Tabula or Blockbench. 1 glTF unit = 1 Minecraft block.
"""
import math, json, struct, io, base64, zipfile
from pathlib import Path
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'deliverables/tz3_phase_3_1_rev2';OUT.mkdir(parents=True,exist_ok=True)
P={'flesh':'#8B2020','flesh_light':'#A63030','flesh_dark':'#6B1818','shadow':'#2A1515','deep':'#1A0F0F','vein':'#B84040','vein_light':'#D05050','bone':'#D4C8A0','bone_dark':'#A89870','fluid':'#7A3040','fluid_light':'#C04050','glow':'#FF4040','glow2':'#FF6040','ground':'#582A27','ground_light':'#622F2B','ground_dark':'#46201E', 'skin':'#596C4A', 'skin_dark':'#3C4E36', 'skin_light':'#758661', 'shirt':'#39534C', 'shirt_dark':'#273B34', 'shirt_light':'#587065', 'pants':'#49403F', 'pants_dark':'#302927', 'pants_light':'#685652'}
def C(k):
 h=P[k].lstrip('#');return tuple(int(h[i:i+2],16) for i in (0,2,4))+(255,)
# Five manually placed pixel-art marks per tile, same palette across entities.
STROKES=[[(1,1),(2,1),(2,2),(4,4),(5,4),(5,5)],[(1,4),(2,4),(3,3),(4,3),(5,2)],[(1,2),(2,2),(3,3),(4,3),(5,4)],[(1,1),(1,2),(2,3),(4,5),(5,5)],[(1,5),(2,4),(3,4),(4,3),(5,3)]]
TYPES={
 'flesh':('flesh_dark','flesh','shadow'), 'raw':('flesh','flesh_light','flesh_dark'),
 'crust':('shadow','flesh_dark','deep'), 'bone':('bone_dark','bone','shadow'),
 'sinew':('flesh_dark','vein','shadow'), 'sac':('fluid','fluid_light','shadow'),
 'mask':('shadow','flesh_dark','bone_dark'), 'rootlet':('ground','ground_light','ground_dark'),
 'skin':('skin','skin_light','skin_dark'), 'shirt':('shirt','shirt_light','shirt_dark'),
 'pants':('pants','pants_light','pants_dark'), 'eye':('deep','glow','shadow')}
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
 'eye':["bbbbbbbb","bbbbbbbb","bbllllbb","bbllllbb","bbbbbbbb","bbbbbbbb","bbbbbbbb","bbbbbbbb"]}
class Atlas:
 def __init__(self):
  self.base=Image.new('RGBA',(64,64),(0,0,0,0));self.glow=Image.new('RGBA',(64,64),(0,0,0,255));self.cache={};self.tiles=[]
 def tile(self,style,variant=0,face='side',glow=False):
  key=(style,variant%5,face,glow)
  if key in self.cache:return self.cache[key]
  idx=len(self.tiles);assert idx<64,(idx,key)
  x=(idx%8)*8;y=(idx//8)*8
  a,b,d=TYPES[style];im=Image.new('RGBA',(8,8),C(a));pix=im.load()
  pattern=PATTERNS[style]
  assert len(pattern)==8 and all(len(row)==8 for row in pattern)
  tone={'b':a,'l':b,'d':d}
  for yy,row in enumerate(pattern):
   for xx,ch in enumerate(row):pix[xx,yy]=C(tone[ch])
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
     r,g,b,alpha=pix[xx,yy];pix[xx,yy]=(r,g,b, 70 if yy==7 else 150 if yy==6 else 255)
  self.base.paste(im,(x,y))
  if glow:
   gp=self.glow.load()
   if face in ('mask_face','zombie_face','skull_face','creeper_face') or style=='eye':
    for u,v in ([(2,2),(3,2),(4,2),(5,2),(2,3),(3,3),(4,3),(5,3)] if style=='eye' else [(1,2),(5,2)]):gp[x+u,y+v]=C('glow')
    if face=='mask_face':
     for u,v in [(1,0),(5,0)]:gp[x+u,y+v]=C('glow2')
   elif style=='sac':
    for u,v in [(2,2),(2,3),(5,4)]:gp[x+u,y+v]=C('glow')
   elif style=='sinew':
    for u,v in [(2,2),(3,3),(4,4)]:gp[x+u,y+v]=C('glow')
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
  c('head',(-.10,1.68,.124),(.08,.17,.012),'skin',2)
  c('jaw',(0,1.54,.08),(.26,.075,.12),'skin',3)
  # Mask is an actual assembly standing about 0.14 blocks (2.2 px) in front of the skull.
  for center,size in [((0,1.84,.195),(.28,.07,.13)),((-.12,1.73,.20),(.06,.20,.13)),((.12,1.73,.20),(.06,.20,.13)),((0,1.69,.205),(.055,.17,.14)),((.045,1.61,.20),(.18,.06,.13))]:c('mask',center,size,'mask',1)
  for x in [-.067,.067]:c('mask',(x,1.75,.235),(.05,.045,.035),'eye',0,'side',True)
  c('mask',(-.09,1.90,.08),(.10,.13,.12),'sac',1,'side',True)
  c('mask',(.075,1.91,.10),(.12,.15,.13),'sac',3,'side',True)
  c('chest_growth',(.10,1.30,.16),(.15,.22,.12),'raw',3)
  c('chest_growth',(.15,1.37,.20),(.11,.11,.09),'sac',1)
  c('chest_growth',(.025,1.25,.18),(.07,.12,.08),'sinew',2)
  # Healthy right arm remains visibly green; left is > 2x thicker with distinct protrusions.
  c('arm_right',(-.235,1.34,0),(.12,.27,.15),'shirt',2)
  c('forearm_right',(-.238,1.04,.01),(.11,.29,.14),'skin',0)
  c('forearm_right',(-.238,.89,.01),(.115,.09,.15),'skin',2)
  c('arm_left',(.25,1.34,0),(.205,.29,.19),'raw',2)
  c('arm_left',(.34,1.39,-.01),(.13,.15,.17),'sac',2)
  c('arm_left',(.28,1.47,.06),(.13,.12,.16),'crust',1)
  c('forearm_left',(.275,1.03,.01),(.20,.32,.18),'raw',3)
  c('forearm_left',(.35,1.06,.03),(.12,.15,.13),'crust',2)
  c('forearm_left',(.30,.87,.04),(.20,.10,.19),'flesh',2)
  for z in [-.025,.035,.095]:c('forearm_left',(.31,.79,z),(.038,.14,.034),'bone',1)
  for side,sgn in [('left',1),('right',-1)]:
   c('leg_'+side,(sgn*.095,.52,0),(.16,.78,.16),'pants',0)
   c('leg_'+side,(sgn*.095,.33,.085),(.11,.17,.025),'skin',1)
   if side=='right':
    c('leg_right',(-.10,.57,.105),(.17,.34,.06),'crust',2)
    c('leg_right',(-.17,.51,.10),(.08,.16,.09),'raw',1)
    c('leg_right',(-.12,.72,.12),(.10,.07,.07),'bone',2)
   c('foot_'+side,(sgn*.095,.08,.035),(.16,.13,.23),'pants',2)
   for i in range(2):c('foot_'+side,(sgn*.095+(-.04+i*.08),.018,.08),(.025,.05,.19),'rootlet',i)
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
  for y in [1.08,1.19,1.30,1.41,1.52]:c('spine',(0,y,-.025),(.11,.055,.09),'bone',2)
  # Skull: cranium, cheeks and separate jaw; dark recessed sockets and teeth are real pieces.
  c('head',(0,1.78,-.02),(.27,.34,.20),'bone',0)
  c('head',(0,1.91,.075),(.28,.08,.07),'bone',1)
  for x in [-.105,.105]:c('head',(x,1.73,.082),(.06,.19,.07),'bone',2)
  for x in [-.062,.062]:
   c('head',(x,1.79,.092),(.07,.08,.035),'crust',0)
   c('head',(x,1.79,.113),(.035,.035,.018),'eye',0,'side',True)
  c('head',(0,1.70,.10),(.035,.07,.04),'bone',1)
  c('jaw',(0,1.60,.06),(.23,.055,.13),'bone',0)
  for x in [-.075,-.025,.025,.075]:c('jaw',(x,1.63,.135),(.025,.045,.018),'bone',2)
  for i,y in enumerate([1.45,1.31,1.17],1):
   for side,sgn in [('left',1),('right',-1)]:
    n='rib_'+side+'_'+str(i)
    c(n,(sgn*.105,y,0),(.15,.045,.11),'bone',0)
    c(n,(sgn*.17,y-.035,.025),(.045,.10,.12),'bone',1)
    c(n,(sgn*.135,y-.07,.087),(.10,.04,.045),'bone',0)
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
  c('arm_whip',(.235,1.35,0),(.09,.27,.10),'flesh',1)
  for n,y,size in [('whip_seg1',1.10,.085),('whip_seg2',.87,.065),('whip_seg3',.65,.045)]:
   c(n,(.25,y,0),(size,.23,size),'sinew',2)
   c(n,(.25,y+.05,.025),(size*1.15,.045,size*1.1),'flesh',2)
  for side,sgn in [('left',1),('right',-1)]:
   c('leg_'+side,(sgn*.09,.50,0),(.075,.75,.085),'bone',2)
   for y in [.80,.50,.20]:c('leg_'+side,(sgn*.09,y,0),(.13,.095,.12),'bone',1)
   c('foot_'+side,(sgn*.09,.07,.03),(.13,.11,.21),'bone',3)
   c('foot_'+side,(sgn*.09,.02,.10),(.035,.05,.18),'rootlet',2)
 return m

def creeper():
 m=Model('b019','Заражённый крипер');b=m.bone;c=m.cube
 b('root',None,(0,0,0),'корень')
 b('body','root',(0,.40,0),'низкое удлинённое тело, сохранившаяся кожа и заражение')
 b('head','body',(0,1.22,.34),'широкая плоская голова и глаза');b('jaw','head',(0,1.30,.49),'ротовая щель')
 b('sac_left','body',(.12,1.20,-.20),'левый спинной мешок');b('sac_right','body',(-.12,1.18,-.25),'правый спинной мешок');b('sac_back','body',(0,1.11,-.46),'задний мешок')
 positions=[(-.29,.43),(.29,.27),(-.29,.10),(.29,-.08),(-.29,-.25),(.29,-.42)]
 for i,(x,z) in enumerate(positions,1):b('leg_'+str(i),'root',(x,.46,z),'шестиногая походка: '+('передняя пара' if i<=2 else 'средняя пара' if i<=4 else 'задняя пара'))
 b('tail','body',(0,.62,-.46),'хвостовой отросток')
 # Body extends along z: width .46, depth .92. Head width .64, leg pairs spaced apart along z.
 # Layered volumes interrupt the box silhouette without introducing sloping n-gons.
 c('body',(0,.80,-.02),(.36,.64,.94),'skin',0)
 c('body',(0,.82,.29),(.44,.70,.30),'skin',1)
 c('body',(0,.83,-.02),(.48,.78,.32),'skin',2)
 c('body',(0,.79,-.31),(.40,.66,.28),'skin',1)
 c('body',(.10,.83,-.03),(.30,.63,.31),'raw',1)
 c('body',(.08,.78,-.30),(.26,.52,.25),'flesh',1)
 c('body',(.10,.84,.27),(.26,.53,.25),'flesh',3)
 c('body',(0,1.18,-.06),(.42,.17,.58),'flesh',2)
 c('body',(.23,.82,-.12),(.11,.33,.25),'sac',2)
 c('body',(-.23,1.04,.15),(.10,.24,.23),'crust',2)
 c('head',(0,1.47,.40),(.64,.38,.29),'skin',0)
 # Creeper face: separate square eye sockets and signature long narrow mouth.
 for x in [-.16,.16]:
  c('head',(x,1.51,.555),(.14,.105,.04),'crust',1)
  c('head',(x,1.51,.581),(.06,.05,.022),'eye',1,'side',True)
 c('head',(0,1.39,.56),(.14,.12,.04),'crust',1)
 for x in [-.105,.105]:c('head',(x,1.355,.56),(.065,.10,.04),'crust',1)
 c('head',(.23,1.59,.52),(.16,.12,.08),'raw',2)
 c('jaw',(0,1.29,.54),(.25,.045,.055),'flesh',2)
 # Raised, separated dorsal sacs, readily visible from profile.
 c('sac_left',(.13,1.27,-.10),(.22,.25,.30),'sac',1,'side',True)
 c('sac_left',(.19,1.34,-.14),(.11,.13,.15),'raw',1)
 c('sac_right',(-.13,1.25,-.22),(.21,.23,.29),'sac',3,'side',True)
 c('sac_back',(0,1.15,-.48),(.29,.26,.25),'sac',4,'side',True)
 c('sac_back',(0,1.23,-.55),(.15,.13,.15),'raw',2)
 for i,(x,z) in enumerate(positions,1):
  sx=.15 if i<=2 else .12; sy=.42 if i<=2 else .38
  c('leg_'+str(i),(x,.25,z),(sx,sy,.12),'skin' if i in (1,4,5) else 'crust',i%5)
  c('leg_'+str(i),(x,.065,z+.02),(sx+.04,.12,.145),'skin' if i in (1,4,5) else 'raw',i%5)
  c('leg_'+str(i),(x,.018,z+.04),(.035,.05,.12),'rootlet',i%5)
 c('tail',(0,.56,-.60),(.10,.13,.30),'flesh',1)
 c('tail',(0,.53,-.75),(.055,.08,.16),'crust',2)
 return m


# Key pose controls expressed in radians for rotations, rest values 0/1.
def controls(kind,anim,t,T):
 phase=2*math.pi*t/T; w=math.sin(phase); vals={}
 def r(n,axis,v): vals[(n,'rotation')]=tuple(v if i==axis else 0.0 for i in range(3))
 def s(n,x,y,z):vals[(n,'scale')]=(x,y,z)
 def tr(n,x,y,z):vals[(n,'translation')]=(x,y,z)
 if anim in ('idle','bone_rattle'):
  r('head',2,.035*w);s('torso' if kind=='b017' else 'ribcage' if kind=='b018' else 'body',1+.015*w,1+.01*w,1+.015*w)
  if anim=='bone_rattle':r('ribcage',2,.09*math.sin(phase*4));r('jaw',0,.07*math.sin(phase*4))
 elif anim in ('walk','crawl'):
  if kind=='b019':
   for i in range(1,7):r('leg_'+str(i),0,.32*math.sin(phase+(0 if i in [1,4,5] else math.pi)))
   r('body',2,.035*w)
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
    for i in (1,2,3):r('whip_seg'+str(i),0,.7*math.sin(math.pi*max(0,min(1,t/T-(i-1)*.10))))
  else:r('head',0,-.5*z);tr('body',0,0,.07*z)
 elif anim=='hurt':
  z=math.sin(math.pi*t/T);r('body' if kind=='b019' else 'torso' if kind=='b017' else 'spine',2,.18*z)
 elif anim=='death':
  z=t/T;r('root',2,1.35*z);tr('root',0,-.1*z,0)
  if kind=='b019':r('head',0,.25*z)
  else:r('head',0,.25*z)
 elif anim=='mask_twitch':r('mask',2,.14*math.sin(2*math.pi*t/T));r('jaw',0,.13*math.sin(math.pi*t/T))
 elif anim in ('fuse','sac_charge'):
  z=t/T if anim=='sac_charge' else .5+.5*math.sin(phase*3)
  for n in ('sac_left','sac_right','sac_back'):s(n,1+.26*z,1+.26*z,1+.26*z)
  r('body',2,.035*math.sin(phase*4))
 elif anim=='detonate':
  z=math.sin(math.pi*t/T);s('body',1+.28*z,1+.18*z,1+.28*z)
  for n in ('sac_left','sac_right','sac_back'):s(n,1+.6*z,1+.6*z,1+.6*z)
  tr('root',0,.10*z,0)
 return vals
ANIMS={
 'b017':[('idle',3,'loop'),('walk',.8,'loop'),('attack',.4,'once'),('hurt',.2,'once'),('death',1.5,'once'),('mask_twitch',.15,'once')],
 'b018':[('idle',3,'loop'),('walk',.8,'loop'),('attack',.4,'once'),('hurt',.2,'once'),('death',1.5,'once'),('whip_attack',.4,'once'),('bone_rattle',2,'loop')],
 'b019':[('idle',3,'loop'),('walk',.8,'loop'),('attack',.4,'once'),('hurt',.2,'once'),('death',1.5,'once'),('crawl',.8,'loop'),('fuse',1,'loop'),('sac_charge',1,'once'),('detonate',.5,'once')],
}
def quat(e):
 x,y,z=[v/2 for v in e];sx,cx=math.sin(x),math.cos(x);sy,cy=math.sin(y),math.cos(y);sz,cz=math.sin(z),math.cos(z)
 return (sx*cy*cz-cx*sy*sz,cx*sy*cz+sx*cy*sz,cx*cy*sz-sx*sy*cz,cx*cy*cz+sx*sy*sz)
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
 for node in m.nodes:
  px,py,pz=node['pivot'];parent=node['parent'];par=m.nodes[m.byname[parent]]['pivot'] if parent else (0,0,0)
  gn={'name':node['name'],'translation':[node['pivot'][j]-par[j] for j in range(3)]}
  restroll = {'arm_left':.14,'arm_right':-.14,'arm_blade':-.14,'arm_whip':.14}.get(node['name'],0.0)
  if restroll: gn['rotation'] = quat((0,0,restroll))
  pos=[];norm=[];uv=[];ind=[]
  for center,size,style,var,face,glow in node['cubes']:
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
    tile=m.atlas.tile(style,var,textureface,light);u0,v0,u1,v1=m.atlas.uv(tile)
    # Proportional UV extent: square texels, no geometric aspect-ratio stretch.
    fw,fh = ((size[0],size[1]) if side in ('front','back') else (size[2],size[1]) if side in ('left','right') else (size[0],size[2]))
    factor=max(fw,fh);uc=(u0+u1)/2;vc=(v0+v1)/2;us=(u1-u0)*(fw/factor)/2;vs=(v1-v0)*(fh/factor)/2
    u0,u1=uc-us,uc+us;v0,v1=vc-vs,vc+vs;k=len(pos)
    pos.extend(verts);norm.extend([n]*4);uv.extend([(u0,v1),(u1,v1),(u1,v0),(u0,v0)]);ind.extend([k,k+1,k+2,k,k+2,k+3])
  if pos:
   prim={'attributes':{'POSITION':floats(pos,'VEC3',3,34962,True),'NORMAL':floats(norm,'VEC3',3,34962),'TEXCOORD_0':floats(uv,'VEC2',2,34962)},'indices':indices(ind),'material':1 if m.id=='b019' and node['name'] in ('sac_left','sac_right','sac_back') else 0}
   meshes.append({'name':node['name']+'_mesh','primitives':[prim]});gn['mesh']=len(meshes)-1
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
      'materials':[{'name':'flesh_emissive','pbrMetallicRoughness':{'baseColorTexture':{'index':0},'metallicFactor':0,'roughnessFactor':.85},'alphaMode':'BLEND','doubleSided':False,'emissiveTexture':{'index':1},'emissiveFactor':[1,1,1]}, {'name':'sac_charge_runtime','pbrMetallicRoughness':{'baseColorTexture':{'index':0},'metallicFactor':0,'roughnessFactor':.85},'alphaMode':'BLEND','doubleSided':False,'emissiveTexture':{'index':1},'emissiveFactor':[0,0,0]}],
      'textures':[{'sampler':0,'source':0},{'sampler':0,'source':1}],
      'samplers':[{'magFilter':9728,'minFilter':9728,'wrapS':33071,'wrapT':33071}],
      'images':[{'bufferView':views_image[0],'mimeType':'image/png','name':m.id},{'bufferView':views_image[1],'mimeType':'image/png','name':m.id+'_glow'}],
      'buffers':[{'byteLength':len(binary)}],'bufferViews':views,'accessors':access}
 if m.id != 'b019': doc['materials'].pop()
 raw=json.dumps(doc,separators=(',',':'),ensure_ascii=False).encode();raw+=b' '*((-len(raw))%4);binary.extend(b'\0'*((-len(binary))%4))
 glb=struct.pack('<4sII',b'glTF',2,12+8+len(raw)+8+len(binary))+struct.pack('<I4s',len(raw),b'JSON')+raw+struct.pack('<I4s',len(binary),b'BIN\0')+binary
 (OUT/(m.id+'.glb')).write_bytes(glb)
 return doc

if __name__=='__main__':
 models=[humanoid('b017'),humanoid('b018'),creeper()]
 for m in models:
  doc=export(m);print(m.id,'bones',len(m.nodes),'cubes',len(m.cubes),'tiles',len(m.atlas.tiles),'animations',len(doc['animations']))
  data={'id':m.id,'label':m.label,'bones':[{'name':n,'role':r} for n,r in m.meta],'animations':[{'name':n,'duration':t,'mode':mode} for n,t,mode in ANIMS[m.id]],'tiles':m.atlas.tiles}
  (OUT/(m.id+'_data.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
