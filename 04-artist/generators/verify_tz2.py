#!/usr/bin/env python3
"""Проверка автономных скриптов, палитр, альфы и простых преобразований базы."""
from pathlib import Path
from PIL import Image, ImageChops
import importlib.util,json,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[1]; A=ROOT/'src/main/resources/assets/carnis/textures/block'
items=json.loads((ROOT/'deliverables/tz2_metrics.json').read_text(encoding='utf-8'))
for x in items:
 n=x['name'];base=Image.open(A/(x['base']+'.png')).convert('RGBA');dest=Image.open(A/(n+'.png'))
 assert dest.mode=='RGBA' and dest.size==(16,16) and all(c[3]==255 for c in dest.getdata()), n
 assert set(dest.getdata())==set(base.getdata()),n
 with tempfile.TemporaryDirectory() as d:
  out=Path(d)/'test.png';subprocess.run([sys.executable,str(ROOT/'deliverables/scripts'/(n+'.py')),str(out)],check=True,stdout=subprocess.DEVNULL)
  produced=Image.open(out).convert('RGBA');assert dest.tobytes()==produced.tobytes(),n
 # Все повороты и отражения, с циклическими сдвигами.
 trans=[base,base.transpose(Image.Transpose.ROTATE_90),base.transpose(Image.Transpose.ROTATE_180),base.transpose(Image.Transpose.ROTATE_270),base.transpose(Image.Transpose.FLIP_LEFT_RIGHT),base.transpose(Image.Transpose.FLIP_TOP_BOTTOM),base.transpose(Image.Transpose.TRANSPOSE),base.transpose(Image.Transpose.TRANSVERSE)]
 assert all(ImageChops.offset(t,dx,dy).tobytes()!=dest.tobytes() for t in trans for dx in range(16) for dy in range(16)),n
 print(n,'OK')
print('Проверено:',len(items))
