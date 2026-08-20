import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import main


class TestControleEquipamentos(unittest.TestCase):

    def setUp(self):
        self.pasta_temporaria = tempfile.TemporaryDirectory()
        self.arquivo_original = main.ARQUIVO_DADOS

        main.ARQUIVO_DADOS = str(
            Path(self.pasta_temporaria.name) / 'equipamentos.json'
        )

        main.equipamentos.clear()

    def tearDown(self):
        main.equipamentos.clear()
        main.ARQUIVO_DADOS = self.arquivo_original
        self.pasta_temporaria.cleanup()

    def test_cadastrar_equipamento(self):
        respostas = [
            'Notebook Dell',
            'PAT001',
            'SER001',
            'Notebook',
            'TI',
            'Caio',
            '1'
        ]

        with patch(
            'builtins.input',
            side_effect=respostas
        ), patch('builtins.print'):
            main.cadastrar_equipamento()

        self.assertEqual(len(main.equipamentos), 1)

        equipamento = main.equipamentos[0]

        self.assertEqual(equipamento['nome'], 'Notebook Dell')
        self.assertEqual(equipamento['patrimonio'], 'PAT001')
        self.assertEqual(equipamento['serial'], 'SER001')
        self.assertEqual(equipamento['categoria'], 'Notebook')
        self.assertEqual(equipamento['setor'], 'TI')
        self.assertEqual(equipamento['responsavel'], 'Caio')
        self.assertEqual(equipamento['status'], 'Em uso')

        self.assertTrue(Path(main.ARQUIVO_DADOS).exists())

    def test_bloquear_patrimonio_duplicado(self):
        main.equipamentos.append({
            'nome': 'Notebook',
            'patrimonio': 'PAT001',
            'serial': 'SER001',
            'categoria': 'Notebook',
            'setor': 'TI',
            'responsavel': 'Caio',
            'status': 'Em uso'
        })

        respostas = [
            'Monitor',
            'PAT001',
            'SER002',
            'Monitor',
            'TI',
            'Caio'
        ]

        with patch(
            'builtins.input',
            side_effect=respostas
        ), patch('builtins.print'):
            main.cadastrar_equipamento()

        self.assertEqual(len(main.equipamentos), 1)

    def test_pesquisar_por_setor(self):
        main.equipamentos.append({
            'nome': 'Notebook Dell',
            'patrimonio': 'PAT001',
            'serial': 'SER001',
            'categoria': 'Notebook',
            'setor': 'TI',
            'responsavel': 'Caio',
            'status': 'Em uso'
        })

        with patch(
            'builtins.input',
            side_effect=['5', 'TI']
        ), patch('builtins.print') as print_simulado:
            main.pesquisar_equipamento()

        saida = ' '.join(
            str(chamada.args[0])
            for chamada in print_simulado.call_args_list
            if chamada.args
        )

        self.assertIn('Notebook Dell', saida)


def test_editar_equipamento(self):
    main.equipamentos.append({
        'nome': 'Notebook Dell',
        'patrimonio': 'PAT001',
        'serial': 'SER001',
        'categoria': 'Notebook',
        'setor': 'TI',
        'responsavel': 'Caio',
        'status': 'Em uso'
    })

    respostas = [
        'PAT001',          # Patrimônio pesquisado
        'Notebook Lenovo', # Novo nome
        'PAT002',          # Novo patrimônio
        'SER002',          # Novo serial
        'Computador',      # Nova categoria
        'Financeiro',      # Novo setor
        'João',            # Novo responsável
        '3',               # Novo status: Em manutenção
        'S'                # Confirmar alteração
    ]

    with patch('builtins.input', side_effect=respostas):
        main.editar_equipamento()

    equipamento = main.equipamentos[0]

    self.assertEqual(equipamento['nome'], 'Notebook Lenovo')
    self.assertEqual(equipamento['patrimonio'], 'PAT002')
    self.assertEqual(equipamento['serial'], 'SER002')
    self.assertEqual(equipamento['categoria'], 'Computador')
    self.assertEqual(equipamento['setor'], 'Financeiro')
    self.assertEqual(equipamento['responsavel'], 'João')
    self.assertEqual(equipamento['status'], 'Em manutenção')


if __name__ == '__main__':
    unittest.main()