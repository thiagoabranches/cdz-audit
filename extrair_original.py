# -*- coding: utf-8 -*-
"""Extrai herois + skills do X-Hero ORIGINAL (sem CDZ)."""
import sys, json
from pathlib import Path
from wc3obj import parse_object_file
from decrypt_mpq import ler_arquivo

MAPA = 'X_Hero_Reborn_1_3_FIX.w3x'

# Extrai via decrypt_mpq (funciona em MPQ encriptado)
w3a_data, _ = ler_arquivo(MAPA, 'war3map.w3a')
w3u_data, _ = ler_arquivo(MAPA, 'war3map.w3u')

w3a = parse_object_file(w3a_data, 'w3a')
w3u = parse_object_file(w3u_data, 'w3u')

def mods_dict(obj):
    out = {}
    for m in obj.get('mods', []):
        f = m['field']
        lvl = m.get('level', 0) or 0
        out.setdefault(f, {})[lvl] = m.get('value')
    return out

# Indexa skills
skills = {}
for obj in w3a['original'] + w3a['custom']:
    cod = (obj.get('new_id') or '').replace('\x00','') or (obj.get('old_id') or '').replace('\x00','')
    if not cod: continue
    md = mods_dict(obj)
    nome = md.get('anam', {}).get(0, '?')
    base = (obj.get('old_id') or '').replace('\x00','')
    skills[cod] = {
        'codigo': cod,
        'nome': nome if isinstance(nome, str) else '?',
        'base': base,
        'atp1': {str(k): (v if isinstance(v, str) else str(v)[:80]) for k, v in md.get('atp1', {}).items()},
        'aub1_nv1': (md.get('aub1', {}).get(1, '') or '')[:200] if isinstance(md.get('aub1', {}).get(1, ''), str) else '',
        'mana': {str(k): v for k, v in md.get('amcs', {}).items()},
        'cooldown': {str(k): v for k, v in md.get('acdn', {}).items()},
        'duracao': {str(k): v for k, v in md.get('adur', {}).items()},
        'area': {str(k): v for k, v in md.get('aare', {}).items()},
        'dano': {str(k): v for k, v in md.get('Efk1', {}).items()},
        'niveis': max([int(k) for k in md.get('atp1', {}).keys() if isinstance(k, int)] + [0]),
    }

# Herois (todos que tem uhab/uabi + stats)
herois = []
for obj in w3u['original'] + w3u['custom']:
    c = (obj.get('new_id') or '').replace('\x00','') or (obj.get('old_id') or '').replace('\x00','')
    if not c: continue
    md = mods_dict(obj)
    uhab = md.get('uhab', {}).get(0, '')
    uabi = md.get('uabi', {}).get(0, '')
    tem_stats = any(k in md for k in ['ustr', 'uagi', 'uint', 'ustp'])
    if not (uhab or uabi) or not tem_stats:
        continue

    unam = md.get('unam', {}).get(0, '?')
    if not isinstance(unam, str): unam = '?'
    upra = md.get('upra', {}).get(0)
    upra_nome = {0: 'STR', 1: 'INT', 2: 'AGI'}.get(upra, '?')

    uhab_str = uhab if isinstance(uhab, str) else ''
    uabi_str = uabi if isinstance(uabi, str) else ''
    todas = []
    if uhab_str:
        todas += [s.strip() for s in uhab_str.split(',') if s.strip()]
    if uabi_str:
        for s in uabi_str.split(','):
            s = s.strip()
            if s and s not in todas:
                todas.append(s)

    herois.append({
        'codigo': c,
        'nome': unam,
        'atributo': upra_nome,
        'hp_nv1': md.get('uhpm', {}).get(0),
        'str_base': md.get('ustr', {}).get(0),
        'agi_base': md.get('uagi', {}).get(0),
        'int_base': md.get('uint', {}).get(0),
        'str_gain': md.get('ustp', {}).get(0),
        'agi_gain': md.get('uagp', {}).get(0),
        'int_gain': md.get('uinp', {}).get(0),
        'modelo': md.get('umdl', {}).get(0),
        'icone': md.get('uico', {}).get(0),
        'uhab': uhab_str,
        'uabi': uabi_str,
        'skills': [skills.get(sc, {'codigo': sc, 'erro': 'nao encontrada'}) for sc in todas],
    })

Path('saida').mkdir(exist_ok=True)
with open('saida/herois_original.json', 'w', encoding='utf-8') as f:
    json.dump(herois, f, ensure_ascii=False, indent=2)

print(f"Herois extraidos: {len(herois)}")
print(f"Total skills: {sum(len(h['skills']) for h in herois)}")
print(f"Salvo: saida/herois_original.json")
print()
for h in herois[:20]:
    print(f"  {h['codigo']} | {h['nome']} | {h['atributo']} | {len(h['skills'])} skills")
if len(herois) > 20:
    print(f"  ... e mais {len(herois) - 20}")
