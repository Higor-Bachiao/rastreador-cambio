"""Uso: python -m cambio

Registra a cotação atual, completa dias faltantes e regenera o gráfico e o README.
"""
from pathlib import Path

from . import coleta, grafico, readme

RAIZ = Path(__file__).resolve().parent.parent
CSV = RAIZ / "data" / "historico.csv"
SVG = RAIZ / "assets" / "grafico.svg"
README = RAIZ / "README.md"


def main() -> None:
    historico = coleta.ler(CSV)
    # na primeira execução busca 90 dias; depois só completa eventuais buracos da última semana
    coleta.completar_passado(historico, 7 if historico else 90)
    coleta.registrar_atual(historico)
    coleta.salvar(historico, CSV)

    SVG.parent.mkdir(exist_ok=True)
    SVG.write_text(grafico.gerar_svg(historico), encoding="utf-8")
    README.write_text(readme.atualizar(README.read_text(encoding="utf-8"), historico), encoding="utf-8")
    print(f"{len(historico)} dias no histórico; mais recente: {max(historico)}")


if __name__ == "__main__":
    main()
