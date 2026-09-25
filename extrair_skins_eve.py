# -*- coding: utf-8 -*-
import sys, json
from pathlib import Path
from wc3obj import parse_object_file

with open('w3u_eve/war3map.w3u', 'rb') as f:
    w3u = parse_object_file(f.read(), 'w3u')

def mods_dict(obj):
    out = {}
    for m in obj.get('mods', []):
        f = m['field']
        lvl = m.get('level', 0) or 0
        out.setdefault(f, {})[lvl] = m.get('value')
    return out

# Análise
herois = []
todos_modelos = set()
for obj in w3u['original'] + w3u['custom']:
    cod = (obj.get('new_id') or '').replace('\x00','') or (obj.get('old_id') or '').replace('\x00','')
    if not cod: continue
    md = mods_dict(obj)
    umdl = md.get('umdl', {}).get(0, '')
    uhab = md.get('uhab', {}).get(0, '')
    
    if umdl:
        todos_modelos.add(str(umdl))
    
    if uhab:
        unam = md.get('unam', {}).get(0, '?')
        if not isinstance(unam, str): unam = '?'
        herois.append({
            'codigo': cod,
            'nome': unam.strip(),
            'modelo': str(umdl) if umdl else '',
            'icone': str(md.get('uico', {}).get(0, '') or ''),
        })

Path('saida').mkdir(exist_ok=True)
with open('saida/skins_eve.json', 'w', encoding='utf-8') as f:
    json.dump(herois, f, ensure_ascii=False, indent=2)

print(f"Total herois: {len(herois)}")
print(f"Total modelos unicos: {len(todos_modelos)}")
print()

# Custom
print("=== MODELOS CUSTOM ===")
custom = sorted(set(m for m in todos_modelos if 'war3map' in m.lower() or 'imported' in m.lower()))
for m in custom:
    print(f"  {m}")
print(f"\nTotal custom: {len(custom)}")
print()

# Procura Anasterian
print("=== PROCURA: Anasterian / Sunstrider ===")
achou = [m for m in todos_modelos if 'anasterian' in m.lower() or 'sunstrider' in m.lower()]
if achou:
    for m in achou: print(f"  ✅ {m}")
else:
    print("  ❌ Nao encontrado")
print()

# Procura termos CDZ relacionados
print("=== PROCURA: termos CDZ (saint, armor, gold, clothe) ===")
for termo in ['saint', 'armor', 'gold', 'clothe', 'saintia', 'athena']:
    achados = [m for m in todos_modelos if termo in m.lower()]
    if achados:
        print(f"  {termo}:")
        for m in achados[:5]:
            print(f"    {m}")
