#!/usr/bin/env python3
"""Экспорт ТЗ-2: 21 отдельная карта в автономные Pillow-скрипты и PNG.
Цвета сверяются именно с реально использованными пикселями базового PNG.
Никакой случайности; экспорт выполняется из корня проекта или по полному пути.
"""
from pathlib import Path
import importlib.util, sys, json, collections
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from carnis_px import seam_metric
spec=importlib.util.spec_from_file_location('variants_source', ROOT/'generators/variants.py')
v=importlib.util.module_from_spec(spec); spec.loader.exec_module(v)
ASSETS=ROOT/'src/main/resources/assets/carnis/textures/block'
SCRIPTS=ROOT/'deliverables/scripts'
ASSETS.mkdir(parents=True,exist_ok=True);SCRIPTS.mkdir(parents=True,exist_ok=True)
entries=[]
for name,pal,fn in v.VARIANTS:
    base=name.rsplit('_',1)[0]
    with Image.open(ASSETS/(base+'.png')) as im:
        basecolors={c[:3] for c in im.convert('RGBA').getdata()}
    grid=[[pal[ch] for ch in r] for r in fn()]
    # Когда тон существует в палитре семейства, но отсутствует в данном
    # базовом тайле, заменяем его ближайшим из реально использованных.
    nearest=lambda c, colors:min(colors,key=lambda x:(sum((x[i]-c[i])**2 for i in range(3)),x))
    replacements={c:nearest(c,basecolors) for row in grid for c in row if c not in basecolors}
    grid=[[replacements.get(c,c) for c in row] for row in grid]
    added=[]
    missing=sorted(basecolors-set(c for row in grid for c in row))
    for c in missing:
        counts=collections.Counter(c1 for row in grid for c1 in row)
        # Ближайший тон — осмысленный переход; пиксель внутри, не на стыке.
        candidate_colors=sorted((x for x in counts if counts[x]>1),key=lambda x:(sum((x[i]-c[i])**2 for i in range(3)),x))
        chosen=None
        for near in candidate_colors:
            candidates=[]
            for y in range(2,14):
                for x in range(2,14):
                    if grid[y][x]!=near: continue
                    old=grid[y][x];grid[y][x]=c
                    h,vert=seam_metric(grid);grid[y][x]=old
                    if max(h,vert)<2:
                        # Предпочесть соседство более светлого/тёмного цвета,
                        # чтобы сохранить осмысленный блик/переход.
                        contrast=sum(grid[y+dy][x+dx]!=near for dx,dy in ((0,1),(1,0),(0,-1),(-1,0)))
                        candidates.append((-contrast, y, x))
            if candidates:
                _,y,x=min(candidates); chosen=(x,y); break
        if chosen is None: raise ValueError(f'не найдено место для {name} {c}')
        x,y=chosen;grid[y][x]=c;added.append((x,y,c))
    assert set(c for row in grid for c in row)==basecolors
    metric=seam_metric(grid)
    assert max(metric)<2,(name,metric)
    im=Image.new('RGBA',(16,16)); im.putdata([(*c,255) for row in grid for c in row]); im.save(ASSETS/(name+'.png'))
    codes=[''.join(f'{r:02X}{g:02X}{b:02X}' for r,g,b in row) for row in grid]
    desc=(fn.__doc__ or 'Отдельная композиция исходного материала.').strip()
    out='''#!/usr/bin/env python3
"""%s.png — %s
Carnis · 16×16 RGBA · карта пикселей, без случайности.
Путь: src/main/resources/assets/carnis/textures/block/%s.png
Запуск: python3 %s.py [путь_выходного_PNG]; требуется Pillow.
"""
import sys
from PIL import Image
ROWS = %r

def build():
    im = Image.new('RGBA', (16, 16))
    for y, row in enumerate(ROWS):
        assert len(row) == 16 * 6
        for x in range(16):
            h = row[x*6:x*6+6]
            im.putpixel((x,y), (int(h[0:2],16),int(h[2:4],16),int(h[4:6],16),255))
    return im

if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv)>1 else '%s.png'
    build().save(path)
    print(path)
'''%(name,desc,name,name,codes,name)
    (SCRIPTS/(name+'.py')).write_text(out,encoding='utf-8')
    entries.append(dict(name=name,base=base,description=desc,seam=metric,colors=len(basecolors),replacements={str(k):x for k,x in replacements.items()},added=added))
    print(name,metric,'colors',len(basecolors),'replace',len(replacements),'added',len(added))
(ROOT/'deliverables/tz2_metrics.json').write_text(json.dumps(entries,ensure_ascii=False,indent=2),encoding='utf-8')
