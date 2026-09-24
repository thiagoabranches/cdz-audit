# -*- coding: utf-8 -*-
"""
Gera dashboard.html consolidando os 4 relatórios de auditoria.
Uso: python gerar_dashboard.py
"""
import json, re
from pathlib import Path
from datetime import datetime

SAIDA = Path('saida')
DASH = Path('dashboard.html')


def parse_auditoria(path):
    """Le saida/audit_errors.txt"""
    linhas = []
    if not path.exists():
        return linhas
    with open(path, encoding='utf-8') as f:
        for ln in f:
            ln = ln.strip()
            if not ln or ln.startswith('='):
                continue
            m = re.match(r'^\[(ERRO|ATENCAO)\]\s+(\S+)\s+\(([^)]+)\)\s+(.*)$', ln)
            if not m:
                continue
            status, cod, heroi, resto = m.groups()
            campo = re.search(r'campo=(\S+(?:\s+\([^)]+\))?)', resto)
            nivel = re.search(r'nivel=(\S+)', resto)
            esp = re.search(r"esperado=(.*?)\s+atual=", resto)
            atu = re.search(r"atual=(.*)$", resto)
            linhas.append({
                'status': status,
                'codigo': cod,
                'heroi': heroi,
                'campo': campo.group(1) if campo else '?',
                'nivel': nivel.group(1) if nivel else '-',
                'esperado': esp.group(1).strip().strip("'\"") if esp else '?',
                'atual': atu.group(1).strip().strip("'\"") if atu else '?',
            })
    return linhas


def parse_lote4(path):
    """Le saida/audit_termos.txt (duas seções: ERROS / ATENÇÃO)"""
    linhas = []
    if not path.exists():
        return linhas
    secao = None
    with open(path, encoding='utf-8') as f:
        for ln in f:
            ln = ln.rstrip()
            if ln.startswith('=== ERROS'):
                secao = 'ERRO'
                continue
            if ln.startswith('=== ATENÇÃO'):
                secao = 'ATENCAO'
                continue
            if not secao:
                continue
            m = re.match(r"^\[(\S+)\]\s+(\w+)\s+nv(\S+)\s+\|\s+'([^']+)'\s+.*?deveria\s+'([^']+)'", ln)
            if m:
                cod, campo, nivel, termo, subst = m.groups()
                linhas.append({
                    'status': secao,
                    'codigo': cod,
                    'campo': campo,
                    'nivel': nivel,
                    'termo': termo,
                    'substituto': subst,
                })
    return linhas


def parse_bases(path):
    """Le saida/audit_bases.txt — extrai só a seção SUSPEITAS"""
    linhas = []
    if not path.exists():
        return linhas
    secao = None
    with open(path, encoding='utf-8') as f:
        for ln in f:
            ln = ln.rstrip()
            if ln.startswith('=== BASES SUSPEITAS'):
                secao = 'suspeitas'
                continue
            if ln.startswith('==='):
                secao = None
                continue
            # linha original (antes do rstrip) preserva indentação
            if secao == 'suspeitas' and ln.startswith('  ') and '|' in ln:
                m = re.match(r'^\s*(\S+)\s+\(([^)]+)\)\s+\|\s+base=(\S+)\s+\(([^)]+)\)', ln)
                if m:
                    cod, heroi, base, fam = m.groups()
                    linhas.append({
                        'codigo': cod,
                        'heroi': heroi,
                        'base': base,
                        'familia': fam,
                    })
    return linhas


def parse_categoria(path):
    """Le saida/audit_categoria.txt"""
    linhas = []
    if not path.exists():
        return linhas
    with open(path, encoding='utf-8') as f:
        linhas_arq = f.read().split('\n\n')
    for bloco in linhas_arq:
        bloco = bloco.strip()
        if not bloco:
            continue
        # primeiro linha: "🔴 Nome (COD) | unam='...'"
        m = re.match(r'^([✅🔴❓])\s+(.+?)\s+\((\S+)\)', bloco)
        if not m:
            continue
        status, nome, cod = m.groups()
        atual_m = re.search(r'atual=(\S+)\s+esperado=(\S+)', bloco)
        stats_m = re.search(r'stats:\s+STR=(\S+)\s+AGI=(\S+)\s+INT=(\S+)', bloco)
        origem_m = re.search(r'origem:\s+(.+)', bloco)
        linhas.append({
            'status': status,
            'nome': nome,
            'codigo': cod,
            'atual': atual_m.group(1) if atual_m else '?',
            'esperado': atual_m.group(2) if atual_m else '?',
            'stats_str': stats_m.group(1) if stats_m else '?',
            'stats_agi': stats_m.group(2) if stats_m else '?',
            'stats_int': stats_m.group(3) if stats_m else '?',
            'origem': origem_m.group(1) if origem_m else '?',
        })
    return linhas


def gerar_html(dados):
    html = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>Dashboard CDZ — X Hero Reborn</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, "Segoe UI", Roboto, sans-serif;
    background: #0d1117; color: #e6edf3;
    line-height: 1.5; font-size: 14px;
  }
  header {
    background: #161b22; border-bottom: 1px solid #30363d;
    padding: 16px 24px; position: sticky; top: 0; z-index: 10;
  }
  h1 { font-size: 18px; margin-bottom: 4px; }
  .meta { font-size: 12px; color: #8b949e; }
  .meta code { color: #58a6ff; font-size: 11px; }

  .resumo {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 12px; padding: 20px 24px;
  }
  .card {
    background: #161b22; border: 1px solid #30363d; border-radius: 8px;
    padding: 16px; cursor: pointer; transition: all .15s;
  }
  .card:hover { border-color: #58a6ff; }
  .card.ativo { border-color: #58a6ff; background: #1f242c; }
  .card .label { font-size: 12px; color: #8b949e; margin-bottom: 6px; }
  .card .num { font-size: 26px; font-weight: 600; }
  .card .num.vermelho { color: #f85149; }
  .card .num.amarelo { color: #d29922; }
  .card .num.verde { color: #3fb950; }
  .card .sub { font-size: 11px; color: #6e7681; margin-top: 4px; }

  .tabs {
    display: flex; gap: 4px; padding: 0 24px; border-bottom: 1px solid #30363d;
    overflow-x: auto;
  }
  .tab {
    padding: 10px 16px; cursor: pointer; color: #8b949e;
    border-bottom: 2px solid transparent; white-space: nowrap;
    font-size: 13px;
  }
  .tab:hover { color: #e6edf3; }
  .tab.ativo { color: #58a6ff; border-bottom-color: #58a6ff; }

  .conteudo { padding: 16px 24px 40px; }
  .filtros {
    display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap;
  }
  .filtros input, .filtros select {
    background: #0d1117; border: 1px solid #30363d; color: #e6edf3;
    padding: 8px 12px; border-radius: 6px; font-size: 13px;
    font-family: inherit;
  }
  .filtros input { flex: 1; min-width: 200px; }
  .filtros input:focus, .filtros select:focus { outline: none; border-color: #58a6ff; }

  table { width: 100%; border-collapse: collapse; }
  th, td {
    text-align: left; padding: 8px 12px;
    border-bottom: 1px solid #21262d; font-size: 13px;
    vertical-align: top;
  }
  th {
    background: #161b22; color: #8b949e; font-weight: 500;
    font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;
    position: sticky; top: 65px; z-index: 5;
  }
  tr:hover td { background: #161b22; }
  tr.linha-erro td:first-child { border-left: 3px solid #f85149; }
  tr.linha-atencao td:first-child { border-left: 3px solid #d29922; }
  tr.linha-ok td:first-child { border-left: 3px solid #3fb950; }

  .tag {
    display: inline-block; padding: 1px 8px; border-radius: 10px;
    font-size: 11px; font-weight: 500;
  }
  .tag-erro { background: rgba(248,81,73,.15); color: #f85149; }
  .tag-atencao { background: rgba(210,153,34,.15); color: #d29922; }
  .tag-ok { background: rgba(63,185,80,.15); color: #3fb950; }
  .tag-neutro { background: #21262d; color: #8b949e; }

  .codigo { font-family: "SF Mono", Consolas, monospace; color: #79c0ff; font-size: 12px; }
  .mono { font-family: "SF Mono", Consolas, monospace; font-size: 12px; color: #8b949e; }
  .heroi { color: #d2a8ff; }
  .termo { color: #f85149; }
  .subst { color: #3fb950; }

  .vazio { padding: 40px; text-align: center; color: #6e7681; }
  .contador { color: #8b949e; font-size: 12px; margin-bottom: 8px; }
</style>
</head>
<body>
<header>
  <h1>Dashboard CDZ — X Hero Reborn</h1>
  <div class="meta">
    Mapa: <code>X_Hero_Reborn_TESTE_TODOS_HEROIS.w3x</code> ·
    SHA256: <code>b1b6835929fe...</code> ·
    Gerado em <span id="data-geracao"></span>
  </div>
</header>

<div class="resumo" id="resumo"></div>
<div class="tabs" id="tabs"></div>
<div class="conteudo" id="conteudo"></div>

<script>
const DADOS = ''' + json.dumps(dados, ensure_ascii=False) + ''';

// Configuração das seções
const SECOES = {
  auditoria_base: {
    titulo: 'Auditoria Base',
    arquivo: 'saida/audit_errors.txt',
    render: renderAuditoriaBase,
  },
  lote4: {
    titulo: 'Lote 4 — Termo Nativo',
    arquivo: 'saida/audit_termos.txt',
    render: renderLote4,
  },
  bases: {
    titulo: 'Bases Erradas',
    arquivo: 'saida/audit_bases.txt',
    render: renderBases,
  },
  categoria: {
    titulo: 'Categoria (upra)',
    arquivo: 'saida/audit_categoria.txt',
    render: renderCategoria,
  },
};

let secaoAtiva = 'auditoria_base';

function contarStatus(arr, campo='status') {
  let e=0, a=0, o=0;
  for (const x of arr) {
    const s = x[campo];
    if (s === 'ERRO' || s === '🔴') e++;
    else if (s === 'ATENCAO' || s === '⚠️') a++;
    else if (s === 'OK' || s === '✅') o++;
  }
  return { e, a, o };
}

function renderResumo() {
  const div = document.getElementById('resumo');
  const ab = contarStatus(DADOS.auditoria_base);
  const l4 = contarStatus(DADOS.lote4);
  const bs = { total: DADOS.bases.length };
  const ct = contarStatus(DADOS.categoria, 'status');

  div.innerHTML = `
    <div class="card" onclick="mudarSecao('auditoria_base')">
      <div class="label">Auditoria Base</div>
      <div class="num ${ab.e>0?'vermelho':'verde'}">${ab.e}</div>
      <div class="sub">erro(s) · ${ab.a} atenção(ões)</div>
    </div>
    <div class="card" onclick="mudarSecao('lote4')">
      <div class="label">Lote 4 — Termo Nativo</div>
      <div class="num vermelho">${l4.e}</div>
      <div class="sub">erro(s) · ${l4.a} atenção(ões)</div>
    </div>
    <div class="card" onclick="mudarSecao('bases')">
      <div class="label">Bases Erradas</div>
      <div class="num vermelho">${bs.total}</div>
      <div class="sub">skill(s) com base suspeita</div>
    </div>
    <div class="card" onclick="mudarSecao('categoria')">
      <div class="label">Categoria (upra)</div>
      <div class="num ${ct.e>0?'vermelho':'verde'}">${ct.e}</div>
      <div class="sub">errado(s) · ${ct.o} ok</div>
    </div>
  `;
}

function renderTabs() {
  const div = document.getElementById('tabs');
  div.innerHTML = Object.entries(SECOES).map(([k, s]) =>
    `<div class="tab ${k===secaoAtiva?'ativo':''}" onclick="mudarSecao('${k}')">${s.titulo}</div>`
  ).join('');
}

function mudarSecao(k) {
  secaoAtiva = k;
  renderTabs();
  renderConteudo();
}

function renderConteudo() {
  const div = document.getElementById('conteudo');
  const arr = DADOS[secaoAtiva] || [];
  const fn = SECOES[secaoAtiva].render;

  div.innerHTML = `
    <div class="filtros">
      <input type="text" id="busca" placeholder="Buscar código ou herói..." oninput="aplicarFiltro()">
    </div>
    <div class="contador" id="contador"></div>
    <div id="tabela-container">${fn(arr)}</div>
  `;
  aplicarFiltro();
}

function aplicarFiltro() {
  const termo = (document.getElementById('busca')?.value || '').toLowerCase();
  const tabela = document.getElementById('tabela-container');
  const linhas = tabela.querySelectorAll('tbody tr');
  let vis = 0;
  linhas.forEach(tr => {
    const texto = tr.textContent.toLowerCase();
    const bate = !termo || texto.includes(termo);
    tr.style.display = bate ? '' : 'none';
    if (bate) vis++;
  });
  document.getElementById('contador').textContent = `${vis} de ${linhas.length} linhas`;
}

function renderAuditoriaBase(arr) {
  if (!arr.length) return '<div class="vazio">Sem dados</div>';
  return `<table>
    <thead><tr>
      <th>Status</th><th>Código</th><th>Herói</th><th>Campo</th>
      <th>Nível</th><th>Esperado</th><th>Atual</th>
    </tr></thead>
    <tbody>
    ${arr.map(l => `
      <tr class="${l.status==='ERRO'?'linha-erro':'linha-atencao'}">
        <td><span class="tag ${l.status==='ERRO'?'tag-erro':'tag-atencao'}">${l.status}</span></td>
        <td class="codigo">${l.codigo}</td>
        <td class="heroi">${l.heroi}</td>
        <td>${l.campo}</td>
        <td class="mono">${l.nivel}</td>
        <td class="mono">${escapeHtml(l.esperado)}</td>
        <td class="mono">${escapeHtml(l.atual)}</td>
      </tr>`).join('')}
    </tbody>
  </table>`;
}

function renderLote4(arr) {
  if (!arr.length) return '<div class="vazio">Sem dados</div>';
  return `<table>
    <thead><tr>
      <th>Status</th><th>Código</th><th>Campo</th><th>Nível</th>
      <th>Termo Nativo</th><th>Substituto</th>
    </tr></thead>
    <tbody>
    ${arr.map(l => `
      <tr class="${l.status==='ERRO'?'linha-erro':'linha-atencao'}">
        <td><span class="tag ${l.status==='ERRO'?'tag-erro':'tag-atencao'}">${l.status}</span></td>
        <td class="codigo">${l.codigo}</td>
        <td>${l.campo}</td>
        <td class="mono">nv${l.nivel}</td>
        <td class="termo">${escapeHtml(l.termo)}</td>
        <td class="subst">${escapeHtml(l.substituto)}</td>
      </tr>`).join('')}
    </tbody>
  </table>`;
}

function renderBases(arr) {
  if (!arr.length) return '<div class="vazio">Sem dados</div>';
  return `<table>
    <thead><tr>
      <th>Código</th><th>Herói</th><th>Base</th><th>Família</th>
    </tr></thead>
    <tbody>
    ${arr.map(l => `
      <tr class="linha-erro">
        <td class="codigo">${l.codigo}</td>
        <td class="heroi">${l.heroi}</td>
        <td class="codigo">${l.base}</td>
        <td class="mono">${escapeHtml(l.familia)}</td>
      </tr>`).join('')}
    </tbody>
  </table>`;
}

function renderCategoria(arr) {
  if (!arr.length) return '<div class="vazio">Sem dados</div>';
  return `<table>
    <thead><tr>
      <th>Status</th><th>Herói</th><th>Código</th>
      <th>Atual</th><th>Esperado</th><th>STR/AGI/INT</th><th>Origem</th>
    </tr></thead>
    <tbody>
    ${arr.map(l => {
      const cls = l.status === '✅' ? 'linha-ok' : (l.status === '🔴' ? 'linha-erro' : 'linha-atencao');
      const tag = l.status === '✅' ? 'tag-ok' : (l.status === '🔴' ? 'tag-erro' : 'tag-neutro');
      return `
      <tr class="${cls}">
        <td><span class="tag ${tag}">${l.status}</span></td>
        <td class="heroi">${escapeHtml(l.nome)}</td>
        <td class="codigo">${l.codigo}</td>
        <td class="mono">${l.atual}</td>
        <td class="mono">${l.esperado}</td>
        <td class="mono">${l.stats_str}/${l.stats_agi}/${l.stats_int}</td>
        <td class="mono">${escapeHtml(l.origem)}</td>
      </tr>`;
    }).join('')}
    </tbody>
  </table>`;
}

function escapeHtml(s) {
  if (s === null || s === undefined) return '';
  return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}

// Data de geração
document.getElementById('data-geracao').textContent = DADOS.__gerado || '?';

// Init
renderResumo();
renderTabs();
renderConteudo();
</script>
</body>
</html>'''
    return html


def main():
    print("Lendo relatórios...")
    dados = {
        '__gerado': datetime.now().strftime('%d/%m/%Y %H:%M'),
        'auditoria_base': parse_auditoria(SAIDA / 'audit_errors.txt'),
        'lote4': parse_lote4(SAIDA / 'audit_termos.txt'),
        'bases': parse_bases(SAIDA / 'audit_bases.txt'),
        'categoria': parse_categoria(SAIDA / 'audit_categoria.txt'),
    }
    print(f"  auditoria_base: {len(dados['auditoria_base'])} linhas")
    print(f"  lote4:          {len(dados['lote4'])} linhas")
    print(f"  bases:          {len(dados['bases'])} linhas")
    print(f"  categoria:      {len(dados['categoria'])} linhas")

    print("Gerando dashboard.html...")
    html = gerar_html(dados)
    with open(DASH, 'w', encoding='utf-8') as f:
        f.write(html)

    tam = DASH.stat().st_size
    print(f"OK: {DASH} ({tam:,} bytes)")
    print()
    print(f"Abre no navegador:")
    print(f"  file:///{DASH.resolve()}")


if __name__ == '__main__':
    main()
