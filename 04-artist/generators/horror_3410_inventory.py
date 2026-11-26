#!/usr/bin/env python3
"""Lossless source inventory and contact sheets for the 3.4.10 revision."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from collections import Counter
import json,hashlib,math
R=Path(__file__).resolve().parents[1];A=R/'project_3_4_10/src/main/resources/assets/carnis';O=R/'analysis_horror_3410';O.mkdir(exist_ok=True)
folders=['textures/block','textures/item','textures/entity','textures/models/armor','textures/gui','textures/particle','textures/mob_effect','textures/hallucination','textures/misc','geo','models/block','models/item','animations','blockstates']
rows=[]
for folder in folders:
 for p in sorted((A/folder).rglob('*')):
  if not p.is_file():continue
  d={'path':p.relative_to(A).as_posix(),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
  if p.suffix=='.png':
   im=Image.open(p);d.update({'width':im.width,'height':im.height,'mode':im.mode})
  rows.append(d)
(O/'inventar_3410_baseline.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',12)
for category in ['block','item','entity','models/armor','gui','particle','mob_effect','hallucination','misc']:
 files=sorted((A/'textures'/category).glob('*.png'))
 if not files:continue
 columns=5;cw=190;ch=190;sheet=Image.new('RGB',(columns*cw,math.ceil(len(files)/columns)*ch),(31,25,27));d=ImageDraw.Draw(sheet)
 for i,p in enumerate(files):
  x=i%columns*cw;y=i//columns*ch;im=Image.open(p).convert('RGBA');w,h=im.size
  # Animation strips: present every frame in miniatures, never mistake strip for one tile.
  if category=='block' and h>w and h%w==0 and p.with_name(p.name+'.mcmeta').exists():
   frames=h//w;s=min(152//min(frames,4),116//w);s=max(2,s);thumb=Image.new('RGBA',(w*s*frames,w*s),(0,0,0,0))
   for k in range(frames):thumb.paste(im.crop((0,k*w,w,(k+1)*w)).resize((w*s,w*s),Image.Resampling.NEAREST),(k*w*s,0))
  else:
   s=min(152/w,130/h);thumb=im.resize((max(1,int(w*s)),max(1,int(h*s))),Image.Resampling.NEAREST)
  x0=x+(cw-thumb.width)//2;y0=y+35+(130-thumb.height)//2
  # Flat mid-dark swatch preserves visibility of cutout alpha.
  d.rectangle((x0,y0,x0+thumb.width-1,y0+thumb.height-1),fill=(54,44,46));sheet.paste(thumb,(x0,y0),thumb)
  d.text((x+4,y+4),p.name,font=font,fill=(235,220,220));d.text((x+4,y+171),str(im.size),font=font,fill=(170,155,155))
 sheet.save(O/('sheet_'+category.replace('/','_')+'.png'))
print('source assets',len(rows),'PNG',sum('width' in r for r in rows),'categories',Counter(r['path'].split('/')[1] if r['path'].startswith('textures/') else r['path'].split('/')[0] for r in rows))
