# -*- coding: utf-8 -*-
"""
audit_valores.py — Auditor de valores numéricos para skills do CDZ.
Detecta skills com valores zerados ou suspeitos.
"""
import sys
import json
import re
from pathlib import Path
from parser_w3a import _extrair_w3a_bytes
from wc3obj import parse_object_file


def carregar_herois():
    json_path = Path("codigo_heroi.json")
    if json_path.exists():
        with open(json_path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def main():
    mapa_path = sys.argv[1] if len(sys.argv) > 1 else \
        "C:/Users/thabr/OneDrive/Documentos/Warcraft III/Maps/sacredwar/X_Hero_Reborn_TESTE_TODOS_HEROIS.w3x"
    print(f"Auditando valores numéricos no mapa: {mapa_path}")

    herois_map = carregar_herois()
    data = _extrair_w3a_bytes(mapa_path)
    parsed = parse_object_file(data, 'w3a')

    indexado = {}
    for obj in parsed['original']:
        codigo = obj['old_id']
        if codigo and codigo != '\x00\x00\x00\x00':
            indexado[codigo] = obj
    for obj in parsed['custom']:
        codigo = obj['new_id']
        if codigo and codigo != '\x00\x00\x00\x00':
            indexado[codigo] = obj

    resultados = []
    nao_encontrados = []

    for cod, heroi in herois_map.items():
        obj = indexado.get(cod)
        if not obj:
            nao_encontrados.append((cod, heroi))
            continue

        mods = obj.get('mods', [])
        campos = {}
        for m in mods:
            f = m['field']
            lvl = m.get('level', 0)
            val = m['value']
            if f not in campos:
                campos[f] = {}
            campos[f][lvl] = val

        avisos = []

        # 1. Efk1 / Efk2 = 0 em todos os níveis
        for efk in ['Efk1', 'Efk2']:
            if efk in campos:
                valores = [v for lvl, v in campos[efk].items() if lvl > 0]
                if valores and all(v == 0.0 or v == 0 for v in valores):
                    avisos.append(f"{efk} zerado em todos os níveis")

        # 2. acdn = 0 (cooldown zero)
        if 'acdn' in campos:
            valores = [v for lvl, v in campos['acdn'].items() if lvl > 0]
            if valores and all(v == 0.0 or v == 0 for v in valores):
                avisos.append("Cooldown (acdn) zerado")

        # 3. amcs = 0 (custo de mana zero)
        if 'amcs' in campos:
            valores = [v for lvl, v in campos['amcs'].items() if lvl > 0]
            if valores and all(v == 0.0 or v == 0 for v in valores):
                avisos.append("Custo de mana (amcs) zerado")

        # 4. adur = 0 mas aub1 menciona duração
        dur_zero = False
        if 'adur' in campos:
            valores = [v for lvl, v in campos['adur'].items() if lvl > 0]
            if not valores or all(v == 0.0 or v == 0 for v in valores):
                dur_zero = True
        else:
            dur_zero = True

        if dur_zero:
            texto_aub1 = " ".join([str(v) for lvl, v in campos.get('aub1', {}).items() if lvl > 0])
            if re.search(r'(duration|seconds?|duraç|segund)', texto_aub1, re.IGNORECASE):
                avisos.append("Duração (adur) zerada mas aub1 menciona duração")

        # 5. aare = 0 mas aub1 menciona área
        aare_zero = False
        if 'aare' in campos:
            valores = [v for lvl, v in campos['aare'].items() if lvl > 0]
            if not valores or all(v == 0.0 or v == 0 for v in valores):
                aare_zero = True
        else:
            aare_zero = True

        if aare_zero:
            texto_aub1 = " ".join([str(v) for lvl, v in campos.get('aub1', {}).items() if lvl > 0])
            if re.search(r'(area|radius|surrounding|target area|área|area)', texto_aub1, re.IGNORECASE):
                avisos.append("Área (aare) zerada mas aub1 menciona área")

        # 6. Todos os níveis com o MESMO valor em campos numéricos por nível
        for campo_num in ['amcs', 'acdn', 'aare']:
            if campo_num in campos:
                lvls = {lvl: v for lvl, v in campos[campo_num].items() if lvl > 0}
                if len(lvls) > 1:
                    valores_unicos = set(lvls.values())
                    if len(valores_unicos) == 1:
                        avisos.append(f"Campo {campo_num} idêntico em todos os níveis ({list(valores_unicos)[0]})")

        if avisos:
            resultados.append({
                'codigo': cod,
                'heroi': heroi,
                'anam': campos.get('anam', {}).get(0, 'Desconhecido'),
                'avisos': avisos
            })

    resultados.sort(key=lambda x: len(x['avisos']), reverse=True)

    print(f"\nSkills CDZ no mapeamento: {len(herois_map)}")
    print(f"Skills encontradas no mapa: {len(herois_map) - len(nao_encontrados)}")
    print(f"Skills NAO encontradas: {len(nao_encontrados)}")
    print(f"Skills com avisos numéricos: {len(resultados)}")
    print("\n--- TOP 20 SKILLS COM MAIS AVISOS NUMÉRICOS ---")
    for r in resultados[:20]:
        print(f"[{r['codigo']}] {r['heroi']} — {r['anam']} ({len(r['avisos'])} avisos):")
        for av in r['avisos']:
            print(f"  - {av}")

    saida_dir = Path("saida")
    saida_dir.mkdir(exist_ok=True)
    txt_path = saida_dir / "audit_valores.txt"

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("=== RELATÓRIO DE AUDITORIA DE VALORES NUMÉRICOS ===\n")
        f.write(f"Total auditadas: {len(herois_map)} | Com avisos: {len(resultados)}\n")
        f.write(f"Nao encontradas: {len(nao_encontrados)}\n\n")
        if nao_encontrados:
            f.write("### NAO ENCONTRADAS\n")
            for cod, heroi in nao_encontrados:
                f.write(f"  {cod} ({heroi})\n")
            f.write("\n")
        for r in resultados:
            f.write(f"[{r['codigo']}] {r['heroi']} — {r['anam']}\n")
            for av in r['avisos']:
                f.write(f"  • {av}\n")
            f.write("\n")

    print(f"\nRelatório completo salvo em: {txt_path}")


if __name__ == '__main__':
    main()
