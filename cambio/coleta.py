"""Busca cotações na AwesomeAPI e mantém o histórico diário em CSV."""
import csv
import json
import time
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

API = "https://economia.awesomeapi.com.br/json"
MOEDAS = {"usd": "USD-BRL", "eur": "EUR-BRL", "btc": "BTC-BRL"}
BRT = timezone(timedelta(hours=-3))

Historico = dict[str, dict[str, float]]  # {"2026-10-15": {"usd": 5.07, ...}}


def buscar(url: str, tentativas: int = 3):
    requisicao = urllib.request.Request(url, headers={"User-Agent": "rastreador-cambio"})
    for tentativa in range(1, tentativas + 1):
        try:
            with urllib.request.urlopen(requisicao, timeout=20) as resposta:
                return json.load(resposta)
        except OSError:
            if tentativa == tentativas:
                raise
            time.sleep(5 * tentativa)


def data_brt(timestamp: str) -> str:
    return datetime.fromtimestamp(int(timestamp), BRT).date().isoformat()


def ler(caminho: Path) -> Historico:
    if not caminho.exists():
        return {}
    with caminho.open(newline="", encoding="utf-8") as arquivo:
        return {
            linha["data"]: {m: float(linha[m]) for m in MOEDAS if linha.get(m)}
            for linha in csv.DictReader(arquivo)
        }


def salvar(historico: Historico, caminho: Path) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with caminho.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(["data", *MOEDAS])
        for data in sorted(historico):
            valores = historico[data]
            escritor.writerow([data, *(valores.get(m, "") for m in MOEDAS)])


def completar_passado(historico: Historico, dias: int) -> None:
    """Preenche dias que ainda não estão no histórico (usado na primeira execução)."""
    for moeda, par in MOEDAS.items():
        for item in buscar(f"{API}/daily/{par}/{dias}"):
            # a lista vem do mais recente para o mais antigo: o primeiro de cada dia vale
            historico.setdefault(data_brt(item["timestamp"]), {}).setdefault(moeda, float(item["bid"]))


def registrar_atual(historico: Historico) -> None:
    dados = buscar(f"{API}/last/{','.join(MOEDAS.values())}")
    for moeda, par in MOEDAS.items():
        item = dados[par.replace("-", "")]
        historico.setdefault(data_brt(item["timestamp"]), {})[moeda] = float(item["bid"])


def serie(historico: Historico, moeda: str) -> list[tuple[str, float]]:
    return [(d, historico[d][moeda]) for d in sorted(historico) if moeda in historico[d]]
