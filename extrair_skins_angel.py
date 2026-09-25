# -*- coding: utf-8 -*-
"""Extrai skins dos heróis do Angel Arena."""
import sys, json
from pathlib import Path
from wc3obj import parse_object_file

with open('w3u_angel/war3map.w3u', 'rb') as f:
    w3u = parse_object_file(f.read(), 'w3u')

def mods_dict(obj):
    out = {}
    for m in obj.get('mods', []):
        f = m['field']
        lvl = m.get('level', 0) or 0
        out.setdefault(f, {})[lvl] = m.get('value')
    return out

# Todos os heróis (com uhab ou uabi + stats)
herois = []
for obj in w3u['original'] + w3u['custom']:
    cod = (obj.get('new_id') or '').replace('\x00','') or (obj.get('old_id') or '').replace('\x00','')
    if not cod: continue
    md = mods_dict(obj)
    uhab = md.get('uhab', {}).get(0, '')
    uabi = md.get('uabi', {}).get(0, '')
    tem_stats = any(k in md for k in ['ustr', 'uagi', 'uint', 'ustp'])
    if not (uhab or uabi) or not tem_stats: continue
    
    unam = md.get('unam', {}).get(0, '?')
    if not isinstance(unam, str): unam = '?'
    umdl = md.get('umdl', {}).get(0, '')
    
    herois.append({
        'codigo': cod,
        'base_nativa': (obj.get('old_id') or '').replace('\x00',''),
        'nome': unam.strip(),
        'modelo': str(umdl) if umdl else '',
        'icone': str(md.get('uico', {}).get(0, '') or ''),
        'portrait': str(md.get('uPor', {}).get(0, '') or ''),
        'scorescreen': str(md.get('ussi', {}).get(0, '') or ''),
    })

Path('saida').mkdir(exist_ok=True)
with open('saida/skins_angel.json', 'w', encoding='utf-8') as f:
    json.dump(herois, f, ensure_ascii=False, indent=2)

print(f"Total herois: {len(herois)}")
print()
# Só modelos CUSTOM (não nativos WC3)
print("=== MODELOS CUSTOM (potencialmente reusaveis) ===")
custom_count = 0
for h in herois:
    m = h['modelo']
    if m and ('war3map' in m.lower() or 'imported' in m.lower() or '.mdx' in m.lower()):
        print(f"  {h['codigo']:6s} | {h['nome'][:30]:30s} | {m}")
        custom_count += 1
print(f"\nTotal custom: {custom_count}")
