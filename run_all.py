# -*- coding: utf-8 -*-
"""
Roda TODAS as auditorias de uma vez.
Uso: python run_all.py <caminho.w3x>
"""
import sys, subprocess
from pathlib import Path


def run(cmd):
    print(f"\n$ {' '.join(cmd)}")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.stdout:
        print(r.stdout)
    if r.stderr:
        print(r.stderr)
    return r.returncode


def main():
    if len(sys.argv) < 2:
        print("Uso: python run_all.py <caminho.w3x>")
        sys.exit(1)
    mapa = sys.argv[1]

    print("=" * 60)
    print(f"Auditoria completa: {mapa}")
    print("=" * 60)

    print("\n>>> 1/6 Decriptando w3u/w3h/w3q/w3t...")
    run([sys.executable, 'decrypt_mpq.py', mapa])

    print("\n>>> 2/6 Auditoria base...")
    run([sys.executable, 'cdz_audit.py', mapa])

    print("\n>>> 3/6 Lote 4 (termos nativos)...")
    run([sys.executable, 'audit_termos.py', mapa])

    print("\n>>> 4/6 Bases erradas...")
    run([sys.executable, 'audit_bases.py', mapa])

    print("\n>>> 5/6 Categoria (upra)...")
    run([sys.executable, 'audit_categoria.py'])

    print("\n>>> 6/6 Gerando dashboard...")
    run([sys.executable, 'gerar_dashboard.py'])

    print("\n" + "=" * 60)
    print("OK. Veja dashboard.html e saida/")
    print("=" * 60)


if __name__ == '__main__':
    main()
