#!/usr/bin/env python3
"""Patch contact into skin-side plane, retaining the other material unchanged.
Does not certify contact visibility or completeness. Requires geometry audit JSON.
"""
from pathlib import Path
from collections import Counter
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent));import entities_tz3_rev31_work as E
P=E.ROOT/'analysis_rev31'/'cross_contact_edits.json';all=json.loads(P.read_text()) if P.exists() else {}
skin={E.C(t)[:3] for t in ('skin','skin_dark','skin_light')}
for ident in ('b017','b018','b019'):
 d=json.loads((E.OUT/(ident+'_geometry_contact_audit.json')).read_text());edits=all.setdefault(ident,{});added=0;skip=Counter()
 for rec in d['failures']:
  if rec['reason']!='width' or rec['width']!=0 or 'skin' not in rec['classes']:skip[(rec['reason'],rec['width'])]+=1;continue
  other=next(c for c in rec['classes'] if c!='skin');side='a' if rec['classes'][0]=='skin' else 'b';probe=rec[side+'_probe'];matches=[(xy,c) for xy,c in probe if tuple(c[:3]) in skin]
  if len(matches)<3:skip['not enough skin texels']+=1;continue
  # First two surface samples on skin side: material-side tone then skin-side tone.
  palette={'cloth':('cloth_mid1','cloth_mid2'),'flesh':('skin_flesh','skin_mid')}.get(other)
  if not palette:skip['unhandled pair']+=1;continue
  for (xy,c),tone in zip(matches[:2],palette):
   key=','.join(map(str,xy))
   if key in edits and edits[key]!=tone:skip['conflicting edit']+=1;continue
   if key not in edits:edits[key]=tone;added+=1
 print(ident,'new',added,'total',len(edits),'skipped',dict(skip))
P.write_text(json.dumps(all,ensure_ascii=False,indent=2))
