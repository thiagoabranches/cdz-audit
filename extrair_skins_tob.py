# -*- coding: utf-8 -*-
"""Extrai skins/modelos dos heróis do Tides of Blood."""
import sys, json
from pathlib import Path
from wc3obj import parse_object_file

with open('w3u_tob/war3map.w3u', 'rb') as f:
    w3u = parse_object_file(f.read(), 'w3u')

def mods_dict(obj):
    out = {}
    for m in obj.get('mods', []):
        f = m['field']
        lvl = m.get('level', 0) or 0
        out.setdefault(f, {})[lvl] = m.get('value')
    return out

herois = []
for obj in w3u['original'] + w3u['custom']:
    cod = (obj.get('new_id') or '').replace('\x00','') or (obj.get('old_id') or '').replace('\x00','')
    if not cod: continue
    md = mods_dict(obj)
    uhab = md.get('uhab', {}).get(0, '')
    if not uhab: continue  # só heróis
    
    herois.append({
        'codigo': cod,
        'base_nativa': (obj.get('old_id') or '').replace('\x00',''),
        'nome': md.get('unam', {}).get(0),
        'nome_proprio': md.get('upro', {}).get(0),
        'modelo': md.get('umdl', {}).get(0),
        'icone': md.get('uico', {}).get(0),
        'portrait': md.get('uPor', {}).get(0),
        'scorescreen': md.get('ussi', {}).get(0),
        'uhab': uhab if isinstance(uhab, str) else '',
    })

Path('saida').mkdir(exist_ok=True)
with open('saida/skins_tob.json', 'w', encoding='utf-8') as f:
    json.dump(herois, f, ensure_ascii=False, indent=2)

print(f"Herois do TOB: {len(herois)}")
print()
for h in herois:
    print(f"=== {h['codigo']} | {h['nome']} ===")
    print(f"  Base:     {h['base_nativa']}")
    print(f"  Modelo:   {h['modelo']}")
    print(f"  Icone:    {h['icone']}")
    print(f"  Portrait: {h['portrait']}")
    print()
