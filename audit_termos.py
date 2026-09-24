# -*- coding: utf-8 -*-
"""
Auditor de termos nativos em campos aub1/atp1 de skills CDZ.
Roda standalone: python audit_termos.py <caminho.w3x>
"""
import sys, os, json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import parser_w3a

# categorias que geram ERRO (nomes de personagem/substituto claro)
CATEGORIAS_ERRO = {'personagem'}


def carregar_termos(caminho='termos_nativos.json'):
    with open(caminho, encoding='utf-8') as f:
        d = json.load(f); return d['termos'], d.get('whitelist_codigos', [])


def _contem(termo, texto, case_sensitive):
    if not texto:
        return False
    if case_sensitive:
        return termo in texto
    return termo.lower() in texto.lower()


def _normalizar(valor):
    """aub1/atp1 podem vir como dict {nivel: texto} ou str."""
    if valor is None:
        return {}
    if isinstance(valor, dict):
        return valor
    if isinstance(valor, str):
        return {'-': valor}
    return {}


def varrer(skills, termos, whitelist=None):
    whitelist = whitelist or []
    """Retorna lista de achados:
    [{codigo, campo, nivel, termo, substituto, categoria, trecho}]"""
    achados = []
    for codigo, info in skills.items():
        if codigo in whitelist:
            continue
        for campo in ('aub1', 'atp1'):
            valores = _normalizar(info.get(campo))
            for nivel, texto in valores.items():
                for t in termos:
                    if _contem(t['termo'], texto, t.get('case_sensitive', False)):
                        achados.append({
                            'codigo': codigo,
                            'campo': campo,
                            'nivel': nivel,
                            'termo': t['termo'],
                            'substituto': t.get('substituto', '?'),
                            'categoria': t.get('categoria', '?'),
                            'trecho': texto[:120] if texto else '',
                        })
    return achados


def gerar_relatorio(achados):
    """Agrupa por severidade e herói."""
    erros = [a for a in achados if a['categoria'] in CATEGORIAS_ERRO]
    atencao = [a for a in achados if a['categoria'] not in CATEGORIAS_ERRO]
    return erros, atencao


def main():
    if len(sys.argv) < 2:
        print("Uso: python audit_termos.py <caminho.w3x>")
        sys.exit(1)
    caminho = sys.argv[1]

    print(f"Mapa: {caminho}")
    termos, whitelist = carregar_termos()
    print(f"Termos carregados: {len(termos)}")

    print("Lendo skills via parser_w3a...")
    skills = parser_w3a.extrair_skills(caminho)
    print(f"Skills: {len(skills)}")
    print()

    achados = varrer(skills, termos, whitelist)
    erros, atencao = gerar_relatorio(achados)

    saida = Path(__file__).parent / 'saida'
    saida.mkdir(exist_ok=True)
    txt = saida / 'audit_termos.txt'

    with open(txt, 'w', encoding='utf-8') as f:
        f.write(f"=== ERROS ({len(erros)}) — categoria: personagem ===\n\n")
        for a in erros:
            f.write(f"[{a['codigo']}] {a['campo']} nv{a['nivel']} | "
                    f"'{a['termo']}' → deveria '{a['substituto']}'\n")
            f.write(f"    {a['trecho']}...\n\n")

        f.write(f"\n=== ATENÇÃO ({len(atencao)}) — outras categorias ===\n\n")
        for a in atencao:
            f.write(f"[{a['codigo']}] {a['campo']} nv{a['nivel']} | "
                    f"'{a['termo']}' → deveria '{a['substituto']}' [{a['categoria']}]\n")
            f.write(f"    {a['trecho']}...\n\n")

    print(f"Pronto. {len(erros)} erros, {len(atencao)} atenção.")
    print(f"Relatorio: {txt}")

    # Resumo por herói
    por_heroi = {}
    for a in erros:
        # pega herói via reference.json ou deixa codigo
        cod = a['codigo']
        por_heroi.setdefault(cod, 0)
        por_heroi[cod] += 1

    print()
    print("=== Top 15 códigos com mais ERROS ===")
    for cod, n in sorted(por_heroi.items(), key=lambda x: -x[1])[:15]:
        print(f"  {cod}: {n} casos")


if __name__ == '__main__':
    main()
