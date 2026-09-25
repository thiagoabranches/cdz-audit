# -*- coding: utf-8 -*-
"""Compara skills do X-Hero original vs X-Hero CDZ, por herói."""
import json
from pathlib import Path

with open('saida/herois_original.json', encoding='utf-8') as f:
    orig = json.load(f)
with open('saida/herois_cdz.json', encoding='utf-8') as f:
    cdz = json.load(f)

orig_map = {h['codigo']: h for h in orig}
cdz_map = {h['codigo']: h for h in cdz}
comuns = sorted(set(orig_map) & set(cdz_map))

saida = Path('saida')
saida.mkdir(exist_ok=True)


def nome_skill(s):
    if not isinstance(s, dict):
        return '?'
    return s.get('nome_editor') or s.get('nome') or s.get('codigo') or '?'

with open(saida / 'comparativo_orig_vs_cdz.txt', 'w', encoding='utf-8') as f:
    f.write("=== COMPARATIVO X-HERO ORIGINAL vs X-HERO CDZ ===\n")
    f.write(f"Herois em comum: {len(comuns)}\n\n")

    for cod in comuns:
        o = orig_map[cod]
        c = cdz_map[cod]

        f.write(f"\n{'='*70}\n")
        f.write(f"### {cod}\n")
        f.write(f"  ORIGINAL: {o.get('nome', '?')} | {o.get('atributo', '?')}\n")
        f.write(f"  CDZ:      {c.get('nome', '?')} | {c.get('atributo', '?')}\n")
        f.write(f"  Skills originais: {len(o.get('skills', []))}\n")
        f.write(f"  Skills CDZ:       {len(c.get('skills', []))}\n")

        f.write(f"\n  --- ORIGINAL ({len(o.get('skills', []))} skills) ---\n")
        for s in o.get('skills', []):
            if s.get('erro'):
                f.write(f"    [???] {s.get('codigo', '?')} — NAO ENCONTRADA\n")
                continue
            nv = s.get('niveis', 0)
            mana = s.get('mana', {})
            cd = s.get('cooldown', {})
            mana_str = f"{mana.get('1', '?')}→{mana.get('8', mana.get('4', '?'))}" if mana else "—"
            cd_str = f"{cd.get('1', '?')}→{cd.get('8', cd.get('4', '?'))}" if cd else "—"
            f.write(f"    [{s.get('codigo', '?')}] {nome_skill(s)} | base={s.get('base', '?')} | nv={nv} | mana={mana_str} | cd={cd_str}\n")

        f.write(f"\n  --- CDZ ({len(c.get('skills', []))} skills) ---\n")
        for s in c.get('skills', []):
            if s.get('erro'):
                f.write(f"    [???] {s.get('codigo', '?')} — NAO ENCONTRADA\n")
                continue
            nv = s.get('niveis', 0)
            mana = s.get('mana', {})
            cd = s.get('cooldown', {})
            mana_str = f"{mana.get('1', '?')}→{mana.get('8', mana.get('4', '?'))}" if mana else "—"
            cd_str = f"{cd.get('1', '?')}→{cd.get('8', cd.get('4', '?'))}" if cd else "—"
            f.write(f"    [{s.get('codigo', '?')}] {nome_skill(s)} | base={s.get('base', '?')} | nv={nv} | mana={mana_str} | cd={cd_str}\n")

        orig_codes = set(s['codigo'] for s in o.get('skills', []) if not s.get('erro'))
        cdz_codes = set(s['codigo'] for s in c.get('skills', []) if not s.get('erro'))
        mantidas = orig_codes & cdz_codes
        removidas = orig_codes - cdz_codes
        adicionadas = cdz_codes - orig_codes

        f.write(f"\n  ANÁLISE:\n")
        f.write(f"    Skills mantidas (mesmo código): {len(mantidas)}\n")
        if mantidas:
            f.write(f"      {sorted(mantidas)}\n")
        f.write(f"    Skills removidas: {len(removidas)}\n")
        if removidas:
            f.write(f"      {sorted(removidas)}\n")
        f.write(f"    Skills adicionadas (CDZ): {len(adicionadas)}\n")
        if adicionadas:
            f.write(f"      {sorted(adicionadas)}\n")

    f.write(f"\n\n{'='*70}\n")
    f.write("RESUMO GLOBAL\n")
    total_mantidas = sum(len(set(s['codigo'] for s in orig_map[c].get('skills', []) if not s.get('erro')) & set(s['codigo'] for s in cdz_map[c].get('skills', []) if not s.get('erro'))) for c in comuns)
    total_removidas = sum(len(set(s['codigo'] for s in orig_map[c].get('skills', []) if not s.get('erro')) - set(s['codigo'] for s in cdz_map[c].get('skills', []) if not s.get('erro'))) for c in comuns)
    total_adicionadas = sum(len(set(s['codigo'] for s in cdz_map[c].get('skills', []) if not s.get('erro')) - set(s['codigo'] for s in orig_map[c].get('skills', []) if not s.get('erro'))) for c in comuns)
    f.write(f"  Skills mantidas:    {total_mantidas}\n")
    f.write(f"  Skills removidas:   {total_removidas}\n")
    f.write(f"  Skills adicionadas: {total_adicionadas}\n")

print(f"Comparativo gerado: saida/comparativo_orig_vs_cdz.txt")
print(f"Herois comparados: {len(comuns)}")

with open(saida / 'comparativo_orig_vs_cdz.txt', encoding='utf-8') as f:
    print(f.read()[:3500])
