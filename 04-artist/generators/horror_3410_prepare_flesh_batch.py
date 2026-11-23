#!/usr/bin/env python3
"""Install and package the 16 revised full-cube flesh materials. No LOCK writes.
Checks actual rotations and variants used in generated blockstates. Numeric seam
metrics are reported honestly; perceptual continuity and runtime are not proven.
"""
from pathlib import Path
from PIL import Image
import hashlib,json,shutil,zipfile
from itertools import product
import numpy as np
R=Path(__file__).resolve().parents[1];A=R/'project_3_4_10/src/main/resources/assets/carnis';O=R/'analysis_horror_3410';C=O/'candidate_flesh_16';D=R/'deliverables/horror_3410_blocks_p1';families=('living_flesh','ossified_flesh','charred_flesh','fireproof_flesh');D.mkdir(parents=True,exist_ok=True)
locks=json.loads((O/'LOCK_9_baseline.json').read_text());baseline={r['path']:r for r in json.loads((O/'inventar_3410_baseline.json').read_text())}
def check_lock():
 for q in locks:
  p=A/q['path'];assert p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==q['sha256'],q['path']
check_lock();records=[];images={};forbidden={(0,0,0),(255,255,255),(255,0,0),(0,255,0),(0,0,255)}
for fam in families:
 for i in range(4):
  name=f'{fam}_{i}.png';src=C/name;im=Image.open(src);assert im.mode=='RGBA' and im.size==(64,64);colors=im.getcolors(4096);assert all(c[3]==255 and c[:3] not in forbidden for _,c in colors)
  images[(fam,i)]=np.asarray(im.convert('RGB'),dtype=float);old=baseline['textures/block/'+name];out=A/'textures/block'/name
  # Source filenames are exact matches in the target archive, not a rename guess.
  assert out.is_file();shutil.copyfile(src,out)
  dst=D/'src/main/resources/assets/carnis/textures/block'/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
  raw=out.read_bytes();records.append({'path':'src/main/resources/assets/carnis/textures/block/'+name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'resolution':[64,64],'rgba':'RGBA/alpha255','previous_dimensions':[old['width'],old['height']],'previous_sha256':old['sha256']})
check_lock();tests={}
for fam in families:
 maps=[(i,k,np.rot90(images[(fam,i)],k)) for i in range(4) for k in range(4)];scores=[]
 for (i,k,a),(j,l,b) in product(maps,repeat=2):
  xbase=(np.abs(a[:,1:]-a[:,:-1]).mean()+np.abs(b[:,1:]-b[:,:-1]).mean())/2;ybase=(np.abs(a[1:]-a[:-1]).mean()+np.abs(b[1:]-b[:-1]).mean())/2
  rx=float(np.abs(a[:,-1]-b[:,0]).mean()/max(1e-8,xbase));ry=float(np.abs(a[-1]-b[0]).mean()/max(1e-8,ybase));scores.append({'a':[i,k*90],'b':[j,l*90],'horizontal':round(rx,5),'vertical':round(ry,5)})
 assert max(max(r['horizontal'],r['vertical']) for r in scores)<2
 tests[fam]={'pair_combinations':len(scores),'max_horizontal':max(r['horizontal'] for r in scores),'max_vertical':max(r['vertical'] for r in scores),'pairs_ge_2':sum(r['horizontal']>=2 or r['vertical']>=2 for r in scores),'measure':'mean absolute RGB difference across seam divided by mean internal RGB difference in same axis; model rotations 0/90/180/270; not a perceptual or Minecraft test'}
 # Every file differs exactly, including the four right-angle orientations.
 for i,j in product(range(4),repeat=2):
  if i>=j:continue
  a=images[(fam,i)];b=images[(fam,j)];assert all(not np.array_equal(a,np.rot90(b,k)) for k in range(4))
(D/'MANIFEST.json').write_text(json.dumps({'files':records,'seam_tests':tests},ensure_ascii=False,indent=2),encoding='utf8')
lines=['# Carnis 3.4.10 — биохоррор, блоки: партия 1','', '## Передано','', '16 текстур четырёх семей: `living_flesh_0–3`, `ossified_flesh_0–3`, `charred_flesh_0–3`, `fireproof_flesh_0–3`. Пути внутри архива совпадают с деревом 3.4.10. Это часть категории блоков, а не все 51 PNG и не завершение общего заказа.','', 'Исходные 16×16 RGB заменены 64×64 RGBA с непрозрачной альфой: увеличение разрешения необходимо выбранному подробному материалу и явно отличается от прежнего 16×16 pixel-art задания. Не утверждается, что старая партия ТЗ-1/2 внезапно сменила требования. Имена и файлы моделей/блокстейтов не изменены; источники нормированных UV визуально не перестраивались.','', '## Художественная оценка и ограничения','', 'По оценке Художника четыре семейства приближены к новой планке: влажные связки и мембраны; костные включения; обугленные провалы без лавы; тёмная термостойкая ткань. Видимые повторения крупных форм на большой стене всё ещё возможны, особенно у вариантов одного сгенерированного исходника: разнообразие — ограничение этой партии, а не доказательство отсутствия повторов. Фактический вид в Minecraft и влияние разрешения на производительность не проверены; окончательная художественная приёмка за Архом.','', 'AI-созданные стилизованные исходники, после чего детерминированно взяты разные области, проведена периодизация и согласование кромок; случайный шум и random.seed не применялись. Четыре варианта семейства не являются точными вращениями друг друга, но часть использует разные фрагменты одного исходника.','', '## Автопроверки','', '- Все 16: 64×64 RGBA, alpha 255, нет точных чистых #000000/#FFFFFF или RGB-первичных; имена существуют в 3.4.10.','- Для каждого семейства проверены все 256 упорядоченных сочетаний 4 вариантов и 4 поворотов с каждой стороны. Метрика: средний абсолютный RGB-перепад через кромку / средний внутренний RGB-перепад той же оси. Во всех случаях <2. Это не доказывает смысловую непрерывность рисунка или скрытность повторов.','- 9 LOCK-файлов сердца до и после записи совпали по SHA-256. Других PNG текущей категории не меняли.','- Не проверено в Minecraft/Forge; геометрию, Java, модели и blockstates не меняли.','', '## Проверка стыков (max по 256 парам, X / Y)','']
for fam,t in tests.items():lines.append(f"- `{fam}`: {t['max_horizontal']:.3f} / {t['max_vertical']:.3f}")
lines+=['', '## Файлы, размер и SHA-256','']
for q in records:lines.append(f"- `{q['path']}` · {q['bytes']} байт · 64×64 · `{q['sha256']}`")
lines+=['','## Дальше','', 'Оставшиеся 33 незамороженные PNG блоков: плоские сосуды/тиры, biomass, hive-детали, nerve, spore, sinew, stomach и жидкость. У tainted_sludge рендерер применяет tint `0xFF8A1A22` к серой текстуре; это учитывать, не закрашивать её вслепую. Затем предметы, существа/geo, armor/gui/particle/effect/hallucination/misc. Сердце — неизменный LOCK.']
status='\n'.join(lines)+'\n';(D/'STATUS.md').write_text(status,encoding='utf8');(R/'deliverables/STATUS_3.4.10_horror_blocks_p1.md').write_text(status,encoding='utf8')
zpath=R/'deliverables/Carnis_3.4.10_horror_blocks_p1.zip'
with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted(D.rglob('*')):
  if f.is_file():z.write(f,f.relative_to(D))
with zipfile.ZipFile(zpath) as z:
 assert z.testzip() is None
 for r in records:assert hashlib.sha256(z.read(r['path'])).hexdigest()==r['sha256']
check_lock();print('batch',len(records),'lock verified 9/9','zip bytes',zpath.stat().st_size,'sha256',hashlib.sha256(zpath.read_bytes()).hexdigest());print(json.dumps(tests,ensure_ascii=False,indent=2))
