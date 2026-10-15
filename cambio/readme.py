"""Atualiza a tabela de cotações do README entre os marcadores."""
import re
from datetime import date

from .coleta import MOEDAS, Historico, serie
from .grafico import NOMES, casas, formatar_brl

INICIO = "<!-- COTACOES:INICIO -->"
FIM = "<!-- COTACOES:FIM -->"


def variacao(pontos: list[tuple[str, float]], dias: int) -> str:
    """Variação do último valor contra o último registro de `dias` atrás ou antes."""
    data_atual, atual = pontos[-1]
    limite = date.fromordinal(date.fromisoformat(data_atual).toordinal() - dias).isoformat()
    anteriores = [v for d, v in pontos if d <= limite]
    if not anteriores:
        return "—"
    pct = (atual / anteriores[-1] - 1) * 100
    return f"{'🟢 ▲' if pct >= 0 else '🔴 ▼'} {abs(pct):.2f}%".replace(".", ",")


def tabela(historico: Historico) -> str:
    linhas = ["| Moeda | Cotação | 1 dia | 7 dias | 30 dias |", "|---|---:|---:|---:|---:|"]
    datas = []
    for moeda in MOEDAS:
        pontos = serie(historico, moeda)
        if not pontos:
            continue
        datas.append(pontos[-1][0])
        linhas.append(
            f"| {NOMES[moeda]} | {formatar_brl(pontos[-1][1], casas(moeda))} | "
            f"{variacao(pontos, 1)} | {variacao(pontos, 7)} | {variacao(pontos, 30)} |"
        )
    atualizado = date.fromisoformat(max(datas)).strftime("%d/%m/%Y")
    return "\n".join(linhas) + f"\n\n<sub>Última atualização: {atualizado} · Fonte: AwesomeAPI</sub>"


def atualizar(texto: str, historico: Historico) -> str:
    padrao = re.compile(re.escape(INICIO) + ".*?" + re.escape(FIM), re.S)
    return padrao.sub(lambda _: f"{INICIO}\n{tabela(historico)}\n{FIM}", texto)
