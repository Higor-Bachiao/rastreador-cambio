import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from cambio import coleta, grafico, readme

HISTORICO = {
    "2026-09-14": {"usd": 5.00, "eur": 5.50, "btc": 400000.0},
    "2026-10-08": {"usd": 5.05, "eur": 5.60, "btc": 410000.0},
    "2026-10-14": {"usd": 5.10, "eur": 5.65, "btc": 405000.0},
    "2026-10-15": {"btc": 420000.0},  # fim de semana/feriado: só BTC
}


class ColetaTest(unittest.TestCase):
    def test_salvar_e_ler_preserva_valores_e_lacunas(self):
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "historico.csv"
            coleta.salvar(HISTORICO, caminho)
            self.assertEqual(coleta.ler(caminho), HISTORICO)

    def test_data_brt_usa_fuso_de_brasilia(self):
        # 2026-10-15 02:00 UTC ainda é dia 14 em Brasília
        self.assertEqual(coleta.data_brt("1792029600"), "2026-10-14")

    def test_serie_ignora_dias_sem_a_moeda(self):
        self.assertEqual(len(coleta.serie(HISTORICO, "usd")), 3)
        self.assertEqual(len(coleta.serie(HISTORICO, "btc")), 4)


class GraficoTest(unittest.TestCase):
    def test_svg_valido_com_um_painel_por_moeda(self):
        raiz = ET.fromstring(grafico.gerar_svg(HISTORICO))
        paineis = raiz.findall("{http://www.w3.org/2000/svg}g")
        self.assertEqual(len(paineis), 3)

    def test_formatar_brl(self):
        self.assertEqual(grafico.formatar_brl(417805, 0), "R$ 417.805")
        self.assertEqual(grafico.formatar_brl(5.0714, 4), "R$ 5,0714")


class ReadmeTest(unittest.TestCase):
    def test_substitui_apenas_o_bloco_entre_marcadores(self):
        texto = f"antes\n{readme.INICIO}\nvelho\n{readme.FIM}\ndepois"
        novo = readme.atualizar(texto, HISTORICO)
        self.assertTrue(novo.startswith("antes\n") and novo.endswith("\ndepois"))
        self.assertNotIn("velho", novo)
        self.assertIn("R$ 420.000", novo)
        self.assertIn("15/10/2026", novo)

    def test_variacao_sem_dado_antigo_mostra_traco(self):
        self.assertEqual(readme.variacao([("2026-10-15", 1.0)], 30), "—")


if __name__ == "__main__":
    unittest.main()
