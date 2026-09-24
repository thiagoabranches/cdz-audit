"""verificar_mapa.py — imprime tamanho e SHA256 de um .w3x.

Uso: python verificar_mapa.py caminho/do/mapa.w3x
"""
import hashlib
import os
import sys

if len(sys.argv) < 2:
    print("Uso: python verificar_mapa.py caminho/do/mapa.w3x")
    sys.exit(1)

caminho = sys.argv[1]

if not os.path.exists(caminho):
    print(f"Arquivo não encontrado: {caminho}")
    sys.exit(1)

tamanho = os.path.getsize(caminho)
sha = hashlib.sha256(open(caminho, 'rb').read()).hexdigest()

print(f"Arquivo: {caminho}")
print(f"Tamanho: {tamanho} bytes")
print(f"SHA256:  {sha}")
