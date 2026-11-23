#!/usr/bin/env python3
"""Демонстрационные стены 4×4 по готовым PNG. Фиксированные раскладки, без random."""
from pathlib import Path
from PIL import Image, ImageDraw
import sys, importlib.util, html, base64
ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'src/main/resources/assets/carnis/textures/block'
sys.path.insert(0, str(ROOT/'generators'))
sys.path.insert(0, str(ROOT/'tools'))
import variants
families=[]
for name,_,_ in variants.VARIANTS:
    base=name.rsplit('_',1)[0]
    if not families or families[-1][0]!=base: families.append((base,[]))
    families[-1][1].append(name)
layouts={
 2:[[0,1,0,0],[1,0,1,1],[0,1,1,0],[0,0,1,0]],
 3:[[0,1,2,0],[2,0,1,2],[1,2,0,1],[0,1,2,0]],
 4:[[0,1,2,3],[2,3,0,1],[1,0,3,2],[3,2,1,0]],
}
wallimages=[]
for base, vs in families:
    names=[base]+vs
    ims=[Image.open(ASSETS/(n+'.png')).convert('RGBA') for n in names]
    wall=Image.new('RGBA',(256,256))
    for y,row in enumerate(layouts[len(names)]):
        for x,i in enumerate(row): wall.paste(ims[i].resize((64,64),Image.Resampling.NEAREST),(x*64,y*64))
    wall.save(ROOT/'previews'/('wall_'+base+'.png'))
    wallimages.append((base,names,wall))
sheet=Image.new('RGB',(4*268,4*288),(24,20,22));d=ImageDraw.Draw(sheet)
for i,(base,names,wall) in enumerate(wallimages):
    x=(i%4)*268;y=(i//4)*288
    d.text((x+4,y+2),base,fill=(232,213,215));sheet.paste(wall.convert('RGB'),(x+4,y+21))
sheet.save(ROOT/'deliverables/Стены_ТЗ-2.png')
def encode(path): return base64.b64encode(path.read_bytes()).decode('ascii')
content='''<!doctype html><html lang="ru"><meta charset="utf-8"><title>Carnis — ТЗ-2</title><style>body{background:#191416;color:#e6d9d5;font:16px/1.5 system-ui;margin:2em auto;max-width:1150px;padding:0 1em}h1,h2{color:#e1a7a2}p{max-width:70ch}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(256px,1fr));gap:25px}figure{margin:0;background:#2b2123;padding:10px;border-radius:6px}img{width:256px;height:256px;max-width:100%;image-rendering:pixelated}figcaption{font-size:14px;overflow-wrap:anywhere}small{color:#c9b4b0}</style><h1>Carnis · Варианты блоков</h1><p>Контрольные стены 4×4: в каждой смешаны базовая текстура и её новые варианты. Раскладки вручную заданы и воспроизводимы; это не проверка случайных раскладок. Видимые повторы и заметные мотивы см. в отчёте.</p><div class="grid">'''
for base,names,_ in wallimages:
    content+='<figure><h2>'+html.escape(base)+'</h2><img alt="Стена '+html.escape(base)+'" src="data:image/png;base64,'+encode(ROOT/'previews'/('wall_'+base+'.png'))+'"><figcaption>'+html.escape(', '.join(names))+'</figcaption></figure>'
content+='</div></html>'
(ROOT/'deliverables/preview_ТЗ-2.html').write_text(content,encoding='utf-8')
print('Готово:',len(families),'стен')
