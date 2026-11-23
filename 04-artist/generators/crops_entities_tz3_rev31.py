#!/usr/bin/env python3
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
D=Path(__file__).resolve().parents[1]/'deliverables/tz3_phase_3_1_rev31'
OLD=D.parent/'tz3_phase_3_1_rev3'
def crop(src,box,out,scale=3):
 im=Image.open(src).convert('RGB').crop(box);im=im.resize((im.width*scale,im.height*scale),Image.Resampling.NEAREST);im.save(D/out,quality=93,subsampling=0)
crop(D/'b019_front.png',(95,145,320,345),'crop_b019_face.jpg',2)
crop(D/'b017_side.png',(110,75,270,235),'crop_b017_mask_side.jpg',2)
crop(D/'b017_front.png',(135,205,300,340),'crop_b017_torso_transition.jpg',3)
crop(D/'b018_front.png',(145,205,270,360),'crop_b018_ribs.jpg',3)
crop(D/'b019_front.png',(85,515,325,665),'crop_roots.jpg',2)
# Same viewpoint, same crop; previous figure was a pale bone cuboid.
a=Image.open(OLD/'b017_front.png').convert('RGB').crop((135,400,240,560)).resize((315,480),Image.Resampling.NEAREST)
b=Image.open(D/'b017_front.png').convert('RGB').crop((135,400,240,560)).resize((315,480),Image.Resampling.NEAREST)
out=Image.new('RGB',(650,530),(25,19,21));out.paste(a,(5,45));out.paste(b,(330,45));draw=ImageDraw.Draw(out)
try:f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',20)
except:f=ImageFont.load_default()
draw.text((10,12),'REV3 — ДО',font=f,fill='#F0D5D0');draw.text((335,12),'REV3.1 — ПОСЛЕ',font=f,fill='#F0D5D0')
out.save(D/'crop_b017_thigh_before_after.jpg',quality=93,subsampling=0)
print('6 crops saved')
