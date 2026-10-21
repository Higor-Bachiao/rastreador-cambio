"""Busca cotações e mantém o histórico diário em CSV.

Dólar e Euro vêm da Frankfurter (taxas de referência do Banco Central Europeu,
publicadas em dias úteis); o Bitcoin vem do preço spot da Coinbase.
"""
import csv
import json
import time
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

FRANKFURTER = "https://api.frankfurter.dev/v1"
COINBASE = "https://api.coinbase.com/v2/prices/BTC-BRL/spot"
FIAT = {"usd": "USD", "eur": "EUR"}
MOEDAS = [*FIAT, "btc"]
BRT = timezone(timedelta(hours=-3))

Historico = dict[str, dict[str, float]]  # {"2026-10-15": {"usd": 5.07, ...}}


def buscar(url: str, tentativas: int = 4):
    requisicao = urllib.request.Request(url, headers={"User-Agent": "rastreador-cambio"})
    for tentativa in range(1, tentativas + 1):
        try:
            with urllib.request.urlopen(requisicao, timeout=20) as resposta:
                return json.load(resposta)
        except (urllib.error.URLError, TimeoutError, ValueError):
            # as APIs às vezes devolvem 404/429/5xx momentâneos: vale tentar de novo
            if tentativa == tentativas:
                raise
            time.sleep(10 * tentativa)


def hoje() -> date:
    return datetime.now(BRT).date()


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
    """Preenche os dias que ainda faltam no histórico, sem sobrescrever o que já existe."""
    inicio = hoje() - timedelta(days=dias)
    for moeda, codigo in FIAT.items():
        dados = buscar(f"{FRANKFURTER}/{inicio.isoformat()}..?base={codigo}&symbols=BRL")
        for data, taxas in dados["rates"].items():
            historico.setdefault(data, {}).setdefault(moeda, taxas["BRL"])
    for i in range(dias):
        data = (inicio + timedelta(days=i)).isoformat()
        if "btc" not in historico.get(data, {}):
            preco = buscar(f"{COINBASE}?date={data}")["data"]["amount"]
            historico.setdefault(data, {})["btc"] = round(float(preco), 2)


def registrar_atual(historico: Historico) -> None:
    for moeda, codigo in FIAT.items():
        dados = buscar(f"{FRANKFURTER}/latest?base={codigo}&symbols=BRL")
        historico.setdefault(dados["date"], {})[moeda] = dados["rates"]["BRL"]
    preco = buscar(COINBASE)["data"]["amount"]
    historico.setdefault(hoje().isoformat(), {})["btc"] = round(float(preco), 2)


def serie(historico: Historico, moeda: str) -> list[tuple[str, float]]:
    return [(d, historico[d][moeda]) for d in sorted(historico) if moeda in historico[d]]
