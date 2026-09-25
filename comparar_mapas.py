# -*- coding: utf-8 -*-
"""Compara 2 mapas X-Hero (baseline vs Claude)."""
import sys
from pathlib import Path
sys.path.insert(0, '.')
from wc3obj import parse_object_file
from decrypt_mpq import ler_arquivo


def skills_dict(caminho):
    try:
        data, _ = ler_arquivo(caminho, 'war3map.w3a')
        if not data:
            print(f"ERRO: w3a não encontrado em {caminho}")
            return {}
        p = parse_object_file(data, 'w3a')
        out = {}
        for obj in p['original'] + p['custom']:
            cod = (obj.get('new_id') or '').replace('\x00','') or (obj.get('old_id') or '').replace('\x00','')
            if not cod: continue
            mods = {}
            for m in obj['mods']:
                f = m['field']
                lvl = m.get('level', 0) or 0
                mods.setdefault(f, {})[lvl] = m.get('value')
            out[cod] = {
                'base': (obj.get('old_id') or '').replace('\x00',''),
                'anam': mods.get('anam', {}).get(0),
                'mods': mods,
            }
        return out
    except Exception as e:
        print(f"ERRO: {e}")
        return {}


def main():
    if len(sys.argv) < 3:
        print("Uso: python comparar_mapas.py <mapa1.w3x> <mapa2.w3x>")
        sys.exit(1)

    print(f"Lendo {sys.argv[1]}...")
    m1 = skills_dict(sys.argv[1])
    print(f"  Skills: {len(m1)}")

    print(f"Lendo {sys.argv[2]}...")
    m2 = skills_dict(sys.argv[2])
    print(f"  Skills: {len(m2)}")
    print()

    comuns = sorted(set(m1) & set(m2))
    so_m1 = sorted(set(m1) - set(m2))
    so_m2 = sorted(set(m2) - set(m1))

    print(f"=== Skills comuns: {len(comuns)} ===")
    print(f"=== Só no MAPA 1: {len(so_m1)} ===")
    print(f"=== Só no MAPA 2: {len(so_m2)} ===")
    print()

    if so_m1:
        print("=== Só no MAPA 1 (baseline) ===")
        for c in so_m1[:30]:
            print(f"  {c} | base={m1[c]['base']} | {m1[c]['anam']}")
        if len(so_m1) > 30:
            print(f"  ... +{len(so_m1)-30}")
        print()

    if so_m2:
        print("=== Só no MAPA 2 (Claude) ===")
        for c in so_m2[:30]:
            print(f"  {c} | base={m2[c]['base']} | {m2[c]['anam']}")
        if len(so_m2) > 30:
            print(f"  ... +{len(so_m2)-30}")
        print()

    print("=== DIFERENÇAS EM SKILLS COMUNS ===")
    difs = 0
    for c in comuns:
        dif_campos = []
        if m1[c]['base'] != m2[c]['base']:
            dif_campos.append(f"base: {m1[c]['base']} → {m2[c]['base']}")
        if m1[c]['anam'] != m2[c]['anam']:
            dif_campos.append(f"anam: {m1[c]['anam']} → {m2[c]['anam']}")
        
        for f in set(list(m1[c]['mods'].keys()) + list(m2[c]['mods'].keys())):
            v1 = m1[c]['mods'].get(f, {})
            v2 = m2[c]['mods'].get(f, {})
            if v1 != v2:
                n1 = len([k for k in v1.keys() if k > 0])
                n2 = len([k for k in v2.keys() if k > 0])
                if n1 != n2:
                    dif_campos.append(f"  campo {f}: {n1} níveis → {n2} níveis")
                else:
                    dif_campos.append(f"  campo {f}: VALORES mudaram")
        
        if dif_campos:
            difs += 1
            print(f"\n[{c}]")
            for d in dif_campos[:10]:
                print(f"  {d}")
            if len(dif_campos) > 10:
                print(f"  ... +{len(dif_campos)-10} mudanças")

    print(f"\n\n=== Total skills com diferenças: {difs} ===")


if __name__ == '__main__':
    main()
