"""Uso: python -m cambio

Registra a cotação atual, completa dias faltantes e regenera o gráfico e o README.
"""
import sys
from pathlib import Path

from . import coleta, grafico, readme

RAIZ = Path(__file__).resolve().parent.parent
CSV = RAIZ / "data" / "historico.csv"
SVG = RAIZ / "assets" / "grafico.svg"
README = RAIZ / "README.md"


def main() -> None:
    historico = coleta.ler(CSV)
    antes = {d: dict(v) for d, v in historico.items()}
    # na primeira execução busca 90 dias; depois só completa eventuais buracos da última semana
    etapas = {
        "dias faltantes": lambda: coleta.completar_passado(historico, 7 if historico else 90),
        "cotação atual": lambda: coleta.registrar_atual(historico),
    }
    falhas = []
    for nome, etapa in etapas.items():
        try:
            etapa()
        except Exception as erro:  # uma fonte fora do ar não deve descartar o que as outras trouxeram
            falhas.append(nome)
            print(f"::warning::Falha ao buscar {nome}: {erro}")
    if historico == antes:
        sys.exit(f"Nenhuma cotação nova coletada (falhas: {', '.join(falhas) or 'nenhuma'}).")
    coleta.salvar(historico, CSV)

    SVG.parent.mkdir(exist_ok=True)
    SVG.write_text(grafico.gerar_svg(historico), encoding="utf-8")
    README.write_text(readme.atualizar(README.read_text(encoding="utf-8"), historico), encoding="utf-8")
    print(f"{len(historico)} dias no histórico; mais recente: {max(historico)}")


if __name__ == "__main__":
    main()
