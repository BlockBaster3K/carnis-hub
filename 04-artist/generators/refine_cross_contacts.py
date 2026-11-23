#!/usr/bin/env python3
"""Accumulate explicit UV corrections for sampled direct inter-cuboid contacts.
Only repairs width 0 or 1 cases, never treats unknown colors as verified.
Caller regenerates and repeats diagnostics; coverage remains incomplete.
"""
from pathlib import Path
from collections import Counter
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent));import entities_tz3_rev31_work as E
P=E.ROOT/'analysis_rev31'/'cross_contact_edits.json';all=json.loads(P.read_text()) if P.exists() else {}
def tones(pair):
 p=frozenset(pair)
 if p=={'skin','flesh'}:return {'skin':'skin_mid','flesh':'skin_flesh'}
 if p=={'skin','cloth'}:return {'cloth':'cloth_mid1','skin':'cloth_mid2'}
 if p=={'bone','cartilage'}:return {'bone':'bone_cart_mid1','cartilage':'bone_cart_mid2'}
 raise ValueError(pair)
for id in ('b017','b018','b019'):
 d=json.loads((E.OUT/(id+'_geometry_contact_audit.json')).read_text());edits=all.setdefault(id,{});added=0;conflicts=0;skip=Counter()
 for rec in d['failures']:
  if rec['reason']!='width' or rec['width'] not in (0,1):skip[rec['reason']]+=1;continue
  A,B=rec['classes'];mapping=tones((A,B));sides=[('a',A),('b',B)]
  if rec['width']==1:
   middle=[c[:3] for side in ('a','b') for xy,c in rec[side][:-1]]
   if not middle:skip['missing midpoint']+=1;continue
   m=tuple(middle[0]);sides=[('b',B)] if m==E.C(mapping[A])[:3] else [('a',A)] if m==E.C(mapping[B])[:3] else []
  for side,cat in sides:
   xy=rec[side][-1][0];k=','.join(map(str,xy));tone=mapping[cat]
   if k in edits:
    if edits[k]!=tone:conflicts+=1
   else:edits[k]=tone;added+=1
 print(id,'new edits',added,'all',len(edits),'conflicts',conflicts,'unhandled',dict(skip))
P.write_text(json.dumps(all,ensure_ascii=False,indent=2))
