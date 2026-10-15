# 💱 Rastreador de Câmbio

[![Atualizar cotações](https://github.com/Higor-Bachiao/rastreador-cambio/actions/workflows/atualizar.yml/badge.svg)](https://github.com/Higor-Bachiao/rastreador-cambio/actions/workflows/atualizar.yml)

Coleta todos os dias a cotação do **Dólar**, do **Euro** e do **Bitcoin** em reais, guarda o histórico em CSV e regenera o gráfico e a tabela abaixo, tudo de forma automática com GitHub Actions.

<!-- COTACOES:INICIO -->
| Moeda | Cotação | 1 dia | 7 dias | 30 dias |
|---|---:|---:|---:|---:|
| Dólar (USD) | R$ 5,0714 | 🟢 ▲ 0,47% | 🟢 ▲ 1,07% | 🔴 ▼ 1,58% |
| Euro (EUR) | R$ 5,6918 | 🟢 ▲ 0,84% | 🟢 ▲ 1,14% | 🔴 ▼ 4,15% |
| Bitcoin (BTC) | R$ 417.512 | 🟢 ▲ 1,15% | 🟢 ▲ 1,41% | 🟢 ▲ 6,79% |

<sub>Última atualização: 15/10/2026 · Fonte: AwesomeAPI</sub>
<!-- COTACOES:FIM -->

<p align="center">
  <img src="assets/grafico.svg" width="100%" alt="Gráfico das cotações dos últimos 90 dias" />
</p>

## Como funciona

```
GitHub Actions (todo dia, 9h de Brasília)
        │
        ▼
python -m cambio ──► AwesomeAPI (cotação atual + dias faltantes)
        │
        ├──► data/historico.csv   histórico diário (um dia por linha)
        ├──► assets/grafico.svg   gráfico gerado em SVG puro, sem bibliotecas
        └──► README.md            tabela com variação de 1, 7 e 30 dias
        │
        ▼
commit automático com o histórico atualizado
```

- **Sem dependências:** só a biblioteca padrão do Python (`urllib`, `csv`, `json`).
- **Histórico completo desde o início:** na primeira execução o script busca os últimos 90 dias; nas seguintes, registra o dia e preenche eventuais buracos da última semana.
- **Resiliente:** repete a requisição em caso de falha de rede, e os testes rodam antes de qualquer commit.
- **Dado aberto:** o [`historico.csv`](data/historico.csv) pode ser usado em qualquer análise.

## Rodando localmente

Requer Python 3.10+.

```bash
python -m cambio             # atualiza CSV, gráfico e README
python -m unittest -v        # roda os testes
```

## Estrutura

```
cambio/
├── coleta.py     # requisições à API e leitura/escrita do CSV
├── grafico.py    # geração do SVG
├── readme.py     # tabela de variações no README
└── __main__.py   # orquestra a atualização
tests/            # testes unitários
.github/workflows/atualizar.yml
```
