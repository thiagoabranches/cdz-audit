# -*- coding: utf-8 -*-
"""Exporta dados completos dos herois CDZ do X-Hero."""
import json
from pathlib import Path

from wc3obj import parse_object_file
from decrypt_mpq import ler_arquivo

MAPA = 'mapa.w3x'

# Carrega w3a + w3u usando a rota de descriptografia MPQ do projeto.
w3a_data, _ = ler_arquivo(MAPA, 'war3map.w3a')
w3u_data, _ = ler_arquivo(MAPA, 'war3map.w3u')

w3a = parse_object_file(w3a_data, 'w3a')
w3u = parse_object_file(w3u_data, 'w3u')

def mods_dict(obj):
    out = {}
    for m in obj.get('mods', []):
        f_ = m['field']
        lvl = m.get('level', 0) or 0
        out.setdefault(f_, {})[lvl] = m.get('value')
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
        'nome_editor': nome if isinstance(nome, str) else '?',
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

# Herois CDZ
HEROIS = {
    'Hpal': ('Mu', 'INT'), 'Hmkg': ('Shion', 'INT'), 'Harf': ('Aldebaran', 'STR'),
    'Edem': ('Saga', 'INT'), 'Udre': ('DeathMask', 'INT'), 'H009': ('Aioria', 'AGI'),
    'Oshd': ('Shaka', 'INT'), 'Otch': ('Dohko', 'STR'), 'N00W': ('Milo', 'AGI'),
    'Hvwd': ('Aioros', 'AGI'), 'Obla': ('Shura', 'STR'), 'Hjai': ('Kamus', 'INT'),
    'Hvsh': ('Afrodite', 'INT'), 'H002': ('Seiya', 'AGI'), 'Ulic': ('Hyoga', 'INT'),
    'Ogrh': ('Shiryu', 'STR'), 'Nklj': ('Ikki', 'STR'), 'Ucrl': ('Shun', 'INT'),
    'Ewar': ('Shina', 'AGI'), 'Npbm': ('Geki', 'STR'), 'Nbst': ('Orpheu', 'INT'),
    'Hblm': ('Siegfried', 'STR'), 'Emoo': ('Sorento', 'INT'), 'H000': ('Marin', 'AGI'),
    'Hamg': ('Kiki', 'INT'), 'Ekee': ('Hakurei', 'INT'),
}

resultado = []
for cod, (nome, upra) in HEROIS.items():
    for obj in w3u['original'] + w3u['custom']:
        c = (obj.get('new_id') or '').replace('\x00','') or (obj.get('old_id') or '').replace('\x00','')
        if c != cod: continue
        md = mods_dict(obj)
        uhab = md.get('uhab', {}).get(0, '') or md.get('uabi', {}).get(0, '')
        if not isinstance(uhab, str): uhab = ''
        skills_list = [s.strip() for s in uhab.split(',') if s.strip()]
        
        hero = {
            'codigo': cod,
            'nome': nome,
            'atributo': upra,
            'hp_nv1': md.get('uhpm', {}).get(0),
            'str_base': md.get('ustr', {}).get(0),
            'agi_base': md.get('uagi', {}).get(0),
            'int_base': md.get('uint', {}).get(0),
            'str_gain': md.get('ustp', {}).get(0),
            'agi_gain': md.get('uagp', {}).get(0),
            'int_gain': md.get('uinp', {}).get(0),
            'modelo': md.get('umdl', {}).get(0),
            'icone': md.get('uico', {}).get(0),
            'uhab': uhab,
            'skills': [skills.get(sc, {'codigo': sc, 'erro': 'nao encontrada'}) for sc in skills_list],
        }
        resultado.append(hero)
        break

Path('saida').mkdir(exist_ok=True)
with open('saida/herois_cdz.json', 'w', encoding='utf-8') as f:
    json.dump(resultado, f, ensure_ascii=False, indent=2)

print(f"JSON gerado: {len(resultado)} herois")
print(f"Total skills: {sum(len(h['skills']) for h in resultado)}")
print(f"Arquivo: saida/herois_cdz.json")
