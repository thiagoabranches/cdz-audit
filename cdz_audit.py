"""
cdz_audit -- auditor de skills do CDZ.
Uso: python cdz_audit.py mapa.w3x
Saida: saida/audit_report.html + saida/audit_errors.txt
Zero edicao -- so leitura.
"""
import json
import sys
import hashlib
import os
from pathlib import Path
from parser_w3a import extrair_skills

BASE_DIR = Path(__file__).parent


def carregar_referencia():
    with open(BASE_DIR / "reference.json", encoding="utf-8") as f:
        return json.load(f)


def comparar(skills: dict, referencia: dict) -> list:
    """
    Retorna lista de dicts:
    { codigo, personagem, campo, nivel, esperado, atual, status }
    Status: OK / ERRO / ATENCAO

    Regra: se o campo esperado for None (reference incompleta),
    pula essa checagem. Só valida o que tem referência preenchida.
    """
    linhas = []

    for codigo, ref in referencia.items():
        personagem = ref.get('personagem', '?')
        esperado_nome = ref.get('atp1_esperado')
        alev_esperado = ref.get('alev')
        hotkey_esperado = ref.get('hotkey')

        skill = skills.get(codigo)

        if skill is None or skill.get('erro'):
            linhas.append({
                'codigo': codigo, 'personagem': personagem, 'campo': '(codigo)',
                'nivel': '-', 'esperado': esperado_nome, 'atual': 'CODIGO NAO ENCONTRADO NO MAPA',
                'status': 'ERRO',
            })
            continue

        # --- anam: so checa se tiver esperado_nome ---
        if esperado_nome is not None:
            anam_atual = skill.get('anam')
            status_anam = 'OK' if anam_atual == esperado_nome else 'ERRO'
            linhas.append({
                'codigo': codigo, 'personagem': personagem, 'campo': 'anam',
                'nivel': '-', 'esperado': esperado_nome, 'atual': anam_atual,
                'status': status_anam,
            })

        # --- alev: so checa se tiver alev_esperado ---
        nivel_max_real = skill.get('nivel_max_real', 1)
        if alev_esperado is not None:
            status_alev = 'OK' if nivel_max_real == alev_esperado else 'ATENCAO'
            linhas.append({
                'codigo': codigo, 'personagem': personagem, 'campo': 'alev (nivel real com dado)',
                'nivel': '-', 'esperado': alev_esperado, 'atual': nivel_max_real,
                'status': status_alev,
            })

        # --- hotkey: so checa se tiver hotkey_esperado ---
        hotkey_atual = skill.get('hotkey_detectado')
        if hotkey_esperado is not None:
            status_hk = 'OK' if hotkey_atual == hotkey_esperado else 'ERRO'
            linhas.append({
                'codigo': codigo, 'personagem': personagem, 'campo': 'hotkey',
                'nivel': '-', 'esperado': hotkey_esperado, 'atual': hotkey_atual,
                'status': status_hk,
            })

        # --- atp1: so checa se tiver esperado_nome ---
        if esperado_nome is not None:
            n_niveis_checar = max(alev_esperado or 1, nivel_max_real)
            for lvl in range(1, n_niveis_checar + 1):
                atual = skill.get('atp1', {}).get(lvl)
                if atual is None or not str(atual).strip():
                    status = 'ATENCAO'
                    atual_display = '(vazio)'
                elif esperado_nome in atual:
                    status = 'OK'
                    atual_display = atual
                else:
                    status = 'ERRO'
                    atual_display = atual
                linhas.append({
                    'codigo': codigo, 'personagem': personagem, 'campo': 'atp1',
                    'nivel': lvl, 'esperado': f'contem "{esperado_nome}"',
                    'atual': atual_display, 'status': status,
                })

        # --- aub1: so checa se tiver esperado_nome (senao nao sabemos o que esperar) ---
        if esperado_nome is not None:
            n_niveis_checar = max(alev_esperado or 1, nivel_max_real)
            for lvl in range(1, n_niveis_checar + 1):
                atual = skill.get('aub1', {}).get(lvl)
                if atual is None or not str(atual).strip():
                    status = 'ATENCAO'
                    atual_display = '(vazio)'
                else:
                    status = 'OK'
                    atual_display = (atual[:80] + '...') if len(atual) > 80 else atual
                linhas.append({
                    'codigo': codigo, 'personagem': personagem, 'campo': 'aub1',
                    'nivel': lvl, 'esperado': '(preenchido, nao vazio)',
                    'atual': atual_display, 'status': status,
                })

        # --- arut / aret: so checa se tiver esperado_nome ---
        if esperado_nome is not None:
            for campo in ('arut', 'aret'):
                valor = skill.get(campo)
                if valor:
                    primeira_palavra = esperado_nome.split()[0].lower()
                    if primeira_palavra not in valor.lower():
                        linhas.append({
                            'codigo': codigo, 'personagem': personagem, 'campo': campo,
                            'nivel': '-', 'esperado': f'relacionado a "{esperado_nome}"',
                            'atual': valor[:80], 'status': 'ATENCAO',
                        })

    return linhas


def gerar_html(linhas: list, caminho_saida: Path):
    try:
        from jinja2 import Template
    except ImportError:
        print("Jinja2 nao instalado -- rodando 'pip install jinja2 --break-system-packages'")
        import subprocess
        subprocess.run(['pip', 'install', 'jinja2', '--break-system-packages'], check=True)
        from jinja2 import Template

    with open(BASE_DIR / 'templates' / 'report.html', encoding='utf-8') as f:
        template = Template(f.read())

    personagens = sorted(set(l['personagem'] for l in linhas))
    total_erro = sum(1 for l in linhas if l['status'] == 'ERRO')
    total_atencao = sum(1 for l in linhas if l['status'] == 'ATENCAO')
    total_ok = sum(1 for l in linhas if l['status'] == 'OK')

    html = template.render(
        linhas=linhas, personagens=personagens,
        total_erro=total_erro, total_atencao=total_atencao, total_ok=total_ok,
        total=len(linhas),
    )
    caminho_saida.write_text(html, encoding='utf-8')


def gerar_txt(linhas: list, caminho_saida: Path):
    erros = [l for l in linhas if l['status'] in ('ERRO', 'ATENCAO')]
    out = []
    for l in erros:
        out.append(
            f"[{l['status']}] {l['codigo']} ({l['personagem']}) campo={l['campo']} "
            f"nivel={l['nivel']} esperado={l['esperado']!r} atual={l['atual']!r}"
        )
    caminho_saida.write_text('\n'.join(out), encoding='utf-8')


def main():
    if len(sys.argv) < 2:
        print("Uso: python cdz_audit.py mapa.w3x")
        sys.exit(1)

    mapa_path = sys.argv[1]

    # Verificação de integridade do mapa
    _tamanho = os.path.getsize(mapa_path)
    _sha = hashlib.sha256(open(mapa_path, 'rb').read()).hexdigest()
    print(f"Mapa: {mapa_path}")
    print(f"Tamanho: {_tamanho} bytes")
    print(f"SHA256: {_sha}")
    print("")

    referencia = carregar_referencia()
    codigos = list(referencia.keys())

    print(f"Lendo {len(codigos)} codigos de {mapa_path}...")
    skills = extrair_skills(mapa_path, codigos)

    print("Comparando contra reference.json...")
    linhas = comparar(skills, referencia)

    saida_dir = BASE_DIR / 'saida'
    saida_dir.mkdir(exist_ok=True)

    gerar_html(linhas, saida_dir / 'audit_report.html')
    gerar_txt(linhas, saida_dir / 'audit_errors.txt')

    total_erro = sum(1 for l in linhas if l['status'] == 'ERRO')
    total_atencao = sum(1 for l in linhas if l['status'] == 'ATENCAO')
    print(f"Pronto. {len(linhas)} checagens: {total_erro} erro(s), {total_atencao} atencao(oes).")
    print(f"Relatorio: {saida_dir / 'audit_report.html'}")
    print(f"Lista de erros: {saida_dir / 'audit_errors.txt'}")


if __name__ == '__main__':
    main()