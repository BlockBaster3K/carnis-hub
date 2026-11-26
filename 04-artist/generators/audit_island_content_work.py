#!/usr/bin/env python3
"""Count island texels, modal colors and nonmodal texels (not artistic value)."""
from collections import Counter
from pathlib import Path
from PIL import Image
import json
D=Path(__file__).resolve().parents[1]/'analysis_rev31'/'work_models'
for ident in ('b017','b018','b019'):
 data=json.loads((D/(ident+'_data.json')).read_text());im=Image.open(D/(ident+'.png')).convert('RGBA');records=[]
 for f in data['uv_layout']:
  x,y,w,h=f['rect'];counts=Counter(im.crop((x,y,x+w,y+h)).get_flattened_data());c,n=counts.most_common(1)[0];total=w*h
  records.append({'bone':f['bone'],'cube':f['cube'],'side':f['side'],'style':f['style'],'rect':f['rect'],'texels':total,'transparent':sum(v for col,v in counts.items() if col[3]==0),'unique_rgba':len(counts),'modal_rgba':list(c),'modal_count':n,'nonmodal_count':total-n,'modal_percent':round(100*n/total,3)})
 result={'islands':len(records),'allocated_texels':sum(r['texels'] for r in records),'transparent_texels':sum(r['transparent'] for r in records),'nonmodal_texels':sum(r['nonmodal_count'] for r in records),'modal_texels':sum(r['modal_count'] for r in records),'islands_over_90pct_modal':sum(r['modal_percent']>90 for r in records),'islands_over_95pct_modal':sum(r['modal_percent']>95 for r in records),'records':records,'scope':'Modal color is not synonymous with blank or useless; non-modal pixels do not prove meaningful unique art. Artfulness and semantic emptiness require visual review.'}
 (D/(ident+'_island_content_audit.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2));print(ident,'allocated',result['allocated_texels'],'transparent',result['transparent_texels'],'nonmodal',result['nonmodal_texels'],'>90% modal',result['islands_over_90pct_modal'],'>95%',result['islands_over_95pct_modal'])
