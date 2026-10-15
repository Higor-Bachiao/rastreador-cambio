"""Gera o gráfico em SVG (sem dependências) com um painel por moeda."""
from datetime import date

from .coleta import MOEDAS, Historico, serie

NOMES = {"usd": "Dólar (USD)", "eur": "Euro (EUR)", "btc": "Bitcoin (BTC)"}
CORES = {"usd": "#3fb950", "eur": "#58a6ff", "btc": "#f2cc60"}
SUBIU, CAIU = "#3fb950", "#f85149"

LARGURA = 820
ALTURA_PAINEL = 170
MARGEM = 16
FONTE = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"


def formatar_brl(valor: float, casas: int) -> str:
    texto = f"{valor:,.{casas}f}"
    return "R$ " + texto.replace(",", "_").replace(".", ",").replace("_", ".")


def casas(moeda: str) -> int:
    return 0 if moeda == "btc" else 4


def data_curta(iso: str) -> str:
    d = date.fromisoformat(iso)
    return f"{d.day:02d}/{d.month:02d}"


def painel(moeda: str, pontos: list[tuple[str, float]], topo: int, dias: int) -> str:
    x0, x1 = MARGEM + 70, LARGURA - MARGEM - 16
    y0, y1 = topo + 52, topo + ALTURA_PAINEL - 42
    valores = [v for _, v in pontos]
    menor, maior = min(valores), max(valores)
    faixa = (maior - menor) or 1
    passo = (x1 - x0) / max(len(pontos) - 1, 1)
    coords = [(x0 + i * passo, y1 - (v - menor) / faixa * (y1 - y0)) for i, v in enumerate(valores)]
    linha = " ".join(f"{x:.1f},{y:.1f}" for x, y in coords)
    area = f"M{coords[0][0]:.1f},{y1} L{linha.replace(' ', ' L')} L{coords[-1][0]:.1f},{y1} Z"

    atual = valores[-1]
    variacao = (atual / valores[0] - 1) * 100
    cor_var = SUBIU if variacao >= 0 else CAIU
    seta = "▲" if variacao >= 0 else "▼"
    cor = CORES[moeda]
    c = casas(moeda)
    ult_x, ult_y = coords[-1]

    return f'''
<g>
  <rect x="{MARGEM}" y="{topo}" width="{LARGURA - 2 * MARGEM}" height="{ALTURA_PAINEL - 10}" rx="8" fill="#161b22" stroke="#30363d"/>
  <text x="{MARGEM + 16}" y="{topo + 28}" class="titulo">{NOMES[moeda]}</text>
  <text x="{LARGURA - MARGEM - 16}" y="{topo + 28}" class="titulo" text-anchor="end">{formatar_brl(atual, c)}
    <tspan fill="{cor_var}" font-size="13"> {seta} {f"{abs(variacao):.2f}".replace(".", ",")}% em {dias} dias</tspan></text>
  <text x="{x0 - 8}" y="{y0 + 4}" class="eixo" text-anchor="end">{formatar_brl(maior, c if c == 0 else 2)}</text>
  <text x="{x0 - 8}" y="{y1 + 4}" class="eixo" text-anchor="end">{formatar_brl(menor, c if c == 0 else 2)}</text>
  <line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}" stroke="#30363d" stroke-dasharray="3 4"/>
  <line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="#30363d"/>
  <path d="{area}" fill="url(#grad-{moeda})"/>
  <polyline points="{linha}" fill="none" stroke="{cor}" stroke-width="2" stroke-linejoin="round"/>
  <circle cx="{ult_x:.1f}" cy="{ult_y:.1f}" r="4" fill="{cor}"><animate attributeName="r" values="4;7;4" dur="2s" repeatCount="indefinite"/></circle>
  <text x="{x0}" y="{y1 + 18}" class="eixo">{data_curta(pontos[0][0])}</text>
  <text x="{x1}" y="{y1 + 18}" class="eixo" text-anchor="end">{data_curta(pontos[-1][0])}</text>
</g>'''


def gerar_svg(historico: Historico, dias: int = 90) -> str:
    paineis, gradientes = [], []
    # mesma janela de datas para todas as moedas (o câmbio não tem cotação no fim de semana)
    inicio = date.fromordinal(date.fromisoformat(max(historico)).toordinal() - dias).isoformat()
    for moeda in MOEDAS:
        pontos = [p for p in serie(historico, moeda) if p[0] >= inicio]
        if len(pontos) < 2:
            continue
        cor = CORES[moeda]
        gradientes.append(
            f'<linearGradient id="grad-{moeda}" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{cor}" stop-opacity=".35"/>'
            f'<stop offset="1" stop-color="{cor}" stop-opacity="0"/></linearGradient>'
        )
        paineis.append(painel(moeda, pontos, MARGEM + len(paineis) * ALTURA_PAINEL, dias))
    altura = 2 * MARGEM + len(paineis) * ALTURA_PAINEL - 10
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {LARGURA} {altura}" width="{LARGURA}" height="{altura}">
<defs>{"".join(gradientes)}</defs>
<style>
text{{font-family:{FONTE};fill:#e6edf3}}
.titulo{{font-size:16px;font-weight:600}}
.eixo{{font-size:11px;fill:#8b949e}}
</style>
<rect width="{LARGURA}" height="{altura}" rx="12" fill="#0d1117"/>
{"".join(paineis)}
</svg>
'''
