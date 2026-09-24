# -*- coding: utf-8 -*-
"""
Auditor de CATEGORIA (upra) dos heróis CDZ.
Chave: código real (Hpal, Hmkg, etc). Não depende de nome.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from wc3obj import parse_object_file

W3U_PATH = 'w3u/war3map.w3u'

# Código real → (nome amigável, atributo esperado)
# Fonte: tabela de nomes vinda do cru + design CDZ
HEROIS = {
    # código    nome              esperado
    'Hpal':   ('Aries Mu',         'INT'),
    'Hmkg':   ('Aries Shion',      'INT'),
    'Harf':   ('Taurus Aldebaran', 'STR'),
    'Edem':   ('Gemini Saga',      'INT'),
    'Udre':   ('Cancer DeathMask', 'INT'),
    'H009':   ('Leo Aioria',       'AGI'),
    'Oshd':   ('Virgo Shaka',      'INT'),
    'Otch':   ('Libra Dohko',      'STR'),
    'N00W':   ('Scorpio Milo',     'AGI'),
    'Hvwd':   ('Sagittarius Aioros','AGI'),
    'Obla':   ('Capricorn Shura',  'STR'),
    'Hjai':   ('Aquarius Kamus',   'INT'),
    'Ulic':   ('Cygnus Hyoga',     'INT'),
    'Ogrh':   ('Dragon Shiryu',    'STR'),
    'Ucrl':   ('Andromeda Shun',   'INT'),
    'Nbst':   ('Lyra Orpheu',      'INT'),
    'H002':   ('Pegasus Seiya',    'AGI'),
    'Hvsh':   ('Pisces Afrodite',  'INT'),
    'H000':   ('Marin of Eagle',   'AGI'),
    'Nklj':   ('Phoenix Ikki',     'STR'),
    'Hblm':   ('Dubhe Siegfried',  'STR'),
    'Ekee':   ('Hakurei Spirit',   'INT'),
    'Npbm':   ('Bear Geki',        'STR'),
    'Hamg':   ('Kiki',             'INT'),
    'Ewar':   ('Ophiuchus Shina',  'AGI'),
    'Emoo':   ('Sierene Sorento',  'INT'),
}

# Base WC3 nativa → primary attribute
NATIVE_PRIM = {
    'Hpal': 'STR', 'Hmkg': 'STR', 'Hblm': 'INT', 'Hamg': 'INT',
    'Harf': 'STR', 'Obla': 'AGI', 'Oshd': 'STR', 'Otch': 'STR',
    'Ogrh': 'STR', 'Hvwd': 'AGI', 'Edem': 'AGI', 'Ekee': 'INT',
    'Emoo': 'AGI', 'Ucrl': 'STR', 'Udre': 'AGI', 'Ulic': 'INT',
    'Udea': 'STR', 'Nbst': 'STR', 'Hvsh': 'AGI', 'Npbm': 'STR',
    'Nklj': 'STR',  # Ikki (custom — precisa confirmar)
    'H009': 'INT',
    'H002': 'AGI',  # Seiya
    'H000': 'AGI',  # Marin
    'Ewar': 'AGI',  # Shina
    'N00W': 'AGI',  # Milo
}


def codigo_de(obj):
    new_id = (obj.get('new_id') or '').replace('\x00', '')
    old_id = (obj.get('old_id') or '').replace('\x00', '')
    return new_id if new_id else old_id


def get_mods_dict(obj):
    out = {}
    for m in obj.get('mods', []):
        f = m.get('field')
        if not f:
            continue
        if f not in out:
            out[f] = m.get('value')
    return out


def main():
    with open(W3U_PATH, 'rb') as f:
        data = f.read()
    parsed = parse_object_file(data, 'w3u')
    todos = parsed['original'] + parsed['custom']

    # Indexa por código (preferindo objeto com stats completos)
    por_codigo = {}
    for obj in todos:
        cod = codigo_de(obj)
        if not cod:
            continue
        m = get_mods_dict(obj)
        # Prioriza quem tem stats
        tem_stats = m.get('ustr') is not None or m.get('uagi') is not None
        if cod not in por_codigo:
            por_codigo[cod] = (m, tem_stats)
        else:
            _, ja_tem = por_codigo[cod]
            if tem_stats and not ja_tem:
                por_codigo[cod] = (m, tem_stats)

    # Analise
    ok = erros = sem = 0
    linhas = []

    for cod, (nome_amigavel, esperado) in HEROIS.items():
        if cod not in por_codigo:
            linhas.append((nome_amigavel, cod, '?', esperado, '❓'))
            sem += 1
            continue

        m, _ = por_codigo[cod]
        upra = m.get('upra')
        unam = m.get('unam', '?')

        if upra is not None:
            atual = str(upra).strip()
            origem = 'explicito (upra)'
        else:
            atual = NATIVE_PRIM.get(cod, '?')
            origem = f'inherited ({cod})'

        match = '✅' if atual == esperado else '🔴'
        if atual == esperado:
            ok += 1
        else:
            erros += 1

        linhas.append((nome_amigavel, cod, atual, esperado, match, origem,
                       m.get('ustr'), m.get('uagi'), m.get('uint'),
                       m.get('ustp'), m.get('uagp'), m.get('uinp'), unam))

    # Console
    print("=== CATEGORIA DE HEROI CDZ (por codigo) ===\n")
    print(f"{'HERÓI':<22} {'COD':<6} {'ATUAL':<6} {'ESPERADO':<9} {'':<3} ORIGEM")
    print("-" * 80)
    for l in linhas:
        if len(l) == 5:
            print(f"{l[0]:<22} {l[1]:<6} {l[2]:<6} {l[3]:<9} {l[4]:<3} NAO ENCONTRADO")
        else:
            nome, cod, atual, esp, m, origem = l[:6]
            print(f"{nome:<22} {cod:<6} {atual:<6} {esp:<9} {m:<3} {origem}")

    # Saida
    saida = Path(__file__).parent / 'saida'
    saida.mkdir(exist_ok=True)
    with open(saida / 'audit_categoria.txt', 'w', encoding='utf-8') as f:
        f.write("=== CATEGORIA DE HEROI CDZ ===\n\n")
        for l in linhas:
            if len(l) == 5:
                f.write(f"❓ {l[0]} ({l[1]}) NAO ENCONTRADO — esperado {l[3]}\n\n")
                continue
            nome, cod, atual, esp, m, origem = l[:6]
            unam = l[12]
            f.write(f"{m} {nome} ({cod}) | unam={unam!r}\n")
            f.write(f"    atual={atual} esperado={esp}\n")
            f.write(f"    origem: {origem}\n")
            f.write(f"    stats: STR={l[6]} AGI={l[7]} INT={l[8]}\n")
            f.write(f"    ganho: +{l[9]}/+{l[10]}/+{l[11]}\n\n")

    print()
    print(f"✅ OK: {ok} | 🔴 Errados: {erros} | ❓ Não achados: {sem}")


if __name__ == '__main__':
    main()
