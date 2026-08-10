import unittest

from main import buscar_por_patrimonio, encontrar_duplicados, resumir_por_tipo


class ControleEquipamentosTestCase(unittest.TestCase):
    def setUp(self):
        self.equipamentos = [
            {"tipo": "Notebook", "patrimonio": "PAT-001", "serial": "ABC-123"},
            {"tipo": "Monitor", "patrimonio": "PAT-002", "serial": "XYZ-999"},
            {"tipo": "Notebook", "patrimonio": "pat-001", "serial": "abc-123"},
        ]

    def test_busca_ignora_maiusculas_e_espacos(self):
        resultado = buscar_por_patrimonio(self.equipamentos, "  pat-002 ")
        self.assertEqual(resultado["tipo"], "Monitor")

    def test_busca_inexistente_retorna_none(self):
        self.assertIsNone(buscar_por_patrimonio(self.equipamentos, "PAT-999"))

    def test_encontra_patrimonios_duplicados(self):
        duplicados = encontrar_duplicados(self.equipamentos, "patrimonio")
        self.assertEqual(duplicados, ["pat-001"])

    def test_resumo_por_tipo(self):
        resumo = resumir_por_tipo(self.equipamentos)
        self.assertEqual(resumo, {"Notebook": 2, "Monitor": 1})


if __name__ == "__main__":
    unittest.main()

