# -*- coding: utf-8 -*-
"""editar_skill.py — Edita skill do w3a com método de 5 passos."""
import sys, copy, argparse
from pathlib import Path
from wc3obj import parse_object_file, write_object_file

W3A_PATH = Path('w3u/war3map.w3a')


def carregar_w3a():
    with open(W3A_PATH, 'rb') as f:
        return parse_object_file(f.read(), 'w3a')


def achar_skill(parsed, codigo):
    for obj in parsed['custom']:
        new_id = (obj.get('new_id') or '').replace('\x00','')
        if new_id == codigo:
            return obj
    return None


def mods_por_campo(obj):
    out = {}
    for m in obj.get('mods', []):
        f = m['field']
        lvl = m.get('level', 0) or 0
        out.setdefault(f, {})[lvl] = m
    return out


def mostrar_diff(antes, depois):
    a = mods_por_campo(antes)
    d = mods_por_campo(depois)
    ca, cd = set(a.keys()), set(d.keys())

    if antes.get('old_id') != depois.get('old_id'):
        print(f"  old_id: {antes.get('old_id')!r} → {depois.get('old_id')!r}")

    for c in sorted(cd - ca):
        print(f"  + ADICIONADO {c}:")
        for lvl in sorted(d[c].keys()):
            print(f"      nv{lvl}: {d[c][lvl].get('value')!r}")

    for c in sorted(ca - cd):
        print(f"  - REMOVIDO {c}")

    for c in sorted(ca & cd):
        for lvl in sorted(set(a[c]) | set(d[c])):
            va = a[c].get(lvl, {}).get('value')
            vd = d[c].get(lvl, {}).get('value')
            if va != vd:
                print(f"  ~ MUDOU {c} nv{lvl}: {va!r} → {vd!r}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument('codigo')
    p.add_argument('--nova-base')
    p.add_argument('--copiar-de')
    p.add_argument('--remover', default='')
    p.add_argument('--dry-run', action='store_true', default=True)
    p.add_argument('--apply', action='store_true')
    args = p.parse_args()

    parsed = carregar_w3a()
    skill = achar_skill(parsed, args.codigo)
    if not skill:
        print(f"ERRO: {args.codigo} nao encontrada")
        sys.exit(1)

    antes = copy.deepcopy(skill)

    if args.nova_base:
        skill['old_id'] = args.nova_base

    if args.copiar_de:
        fonte = achar_skill(parsed, args.copiar_de)
        if fonte:
            cf = set(mods_por_campo(fonte).keys())
            ca = set(mods_por_campo(skill).keys())
            for c in cf - ca:
                for lvl, m in mods_por_campo(fonte)[c].items():
                    skill['mods'].append(dict(m))

    if args.remover:
        alvos = [x.strip() for x in args.remover.split(',') if x.strip()]
        skill['mods'] = [m for m in skill['mods'] if m['field'] not in alvos]

    print(f"=== DRY-RUN: {args.codigo} ===\n")
    mostrar_diff(antes, skill)

    if args.apply:
        novo = write_object_file(parsed, 'w3a')
        Path('saida/w3a_novo.bin').parent.mkdir(exist_ok=True)
        Path('saida/w3a_novo.bin').write_bytes(novo)
        print(f"\nW3A novo: saida/w3a_novo.bin ({len(novo)} bytes)")
    else:
        print("\n(dry-run — use --apply pra gravar)")


if __name__ == '__main__':
    main()
