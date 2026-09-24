# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '.')
from wc3obj import parse_object_file
from pathlib import Path

# Carrega tudo
with open('w3u/war3map.w3a', 'rb') as f:
    w3a = parse_object_file(f.read(), 'w3a')
with open('w3u/war3map.w3u', 'rb') as f:
    w3u = parse_object_file(f.read(), 'w3u')

# Indexa skills
skills = {}
for obj in w3a['original'] + w3a['custom']:
    cod = (obj.get('new_id') or '').replace('\x00','')
    if not cod:
        cod = (obj.get('old_id') or '').replace('\x00','')
    if not cod: continue
    mods = {m['field']: m['value'] for m in obj['mods'] if m.get('level',0) == 0}
    anam = mods.get('anam','')
    if not isinstance(anam, str): anam = ''
    base = (obj.get('old_id') or '').replace('\x00','')
    skills[cod] = {'anam': anam.strip(), 'base': base}

# Indexa por NOME (só A4XX)
por_nome_a4 = {}
for cod, info in skills.items():
    if not cod.startswith('A4'): continue
    n = info['anam']
    if n:
        por_nome_a4.setdefault(n, []).append((cod, info['base']))

# Mapa herói antigo → código novo
MAP = {
    'Hpal': ('Mu', 'N400'), 'Hmkg': ('Shion', 'N401'),
    'Harf': ('Aldebaran', 'N402'), 'Edem': ('Saga', 'N403'),
    'Udre': ('DeathMask', 'N404'), 'H009': ('Aioria', 'N405'),
    'Oshd': ('Shaka', 'N406'), 'Otch': ('Dohko', 'N407'),
    'N00W': ('Milo', 'N408'), 'Hvwd': ('Aioros', 'N409'),
    'Obla': ('Shura', 'N40A'), 'Hjai': ('Kamus', 'N40B'),
    'Hvsh': ('Afrodite', 'N40C'), 'H002': ('Seiya', 'N40D'),
    'Ulic': ('Hyoga', 'N40E'), 'Ogrh': ('Shiryu', 'N40F'),
    'Nklj': ('Ikki', 'N410'), 'Ucrl': ('Shun', 'N411'),
    'Ewar': ('Shina', 'N412'), 'Npbm': ('Geki', 'N413'),
    'Nbst': ('Orpheu', 'N414'), 'Hblm': ('Siegfried', 'N415'),
    'Emoo': ('Sorento', 'N416'),
}

# Indexa heróis — pega uhab E uabi (sem preferir)
herois = {}
for obj in w3u['original'] + w3u['custom']:
    cod = (obj.get('new_id') or '').replace('\x00','')
    if not cod:
        cod = (obj.get('old_id') or '').replace('\x00','')
    if not cod: continue
    mods = {m['field']: m['value'] for m in obj['mods'] if m.get('level',0) == 0}
    uhab = mods.get('uhab')
    uabi = mods.get('uabi')
    if isinstance(uhab, str) and uhab.strip():
        herois[cod] = {'uhab': uhab.strip(), 'uabi': uabi if isinstance(uabi, str) else ''}
    elif isinstance(uabi, str) and uabi.strip():
        herois[cod] = {'uhab': '', 'uabi': uabi.strip()}

# Gera arquivo
saida = Path('saida')
saida.mkdir(exist_ok=True)

with open(saida / 'pares_nome.txt', 'w', encoding='utf-8') as f:
    total_pares = 0
    total_sem_par = 0

    for antigo, (nome, novo) in MAP.items():
        f.write(f"=== {nome} ({antigo} → {novo}) ===\n")

        if antigo not in herois:
            f.write(f"  ⚠️  NÃO ENCONTRADO no w3u\n\n")
            continue

        h = herois[antigo]
        f.write(f"  uhab: {h['uhab'] or '(vazio)'}\n")
        f.write(f"  uabi: {h['uabi'] or '(vazio)'}\n")

        # Junta uhab + uabi pra mapear
        todos = []
        if h['uhab']:
            todos += [c.strip() for c in h['uhab'].split(',') if c.strip()]
        if h['uabi']:
            for c in h['uabi'].split(','):
                c = c.strip()
                if c and c not in todos:
                    todos.append(c)

        for sc in todos:
            info = skills.get(sc, {})
            nome_atual = info.get('anam', '?')
            base_atual = info.get('base', '?')
            par = por_nome_a4.get(nome_atual, [])
            if par:
                total_pares += 1
                f.write(f"  ✅ {sc} ({nome_atual}) base={base_atual}\n")
                for p_cod, p_base in par:
                    f.write(f"       → {p_cod} base={p_base}\n")
            else:
                total_sem_par += 1
                f.write(f"  ❌ {sc} ({nome_atual}) base={base_atual} — SEM PAR\n")
        f.write("\n")

    f.write(f"\n\n=== TOTAIS ===\n")
    f.write(f"Pares claros: {total_pares}\n")
    f.write(f"Sem par:      {total_sem_par}\n")

print(f"Gerado saida/pares_nome.txt")
print(f"  Pares: {total_pares}")
print(f"  Sem par: {total_sem_par}")
