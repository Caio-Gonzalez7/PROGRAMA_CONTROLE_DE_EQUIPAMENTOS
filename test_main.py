import csv
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import main


def criar_equipamento(
    nome='Notebook Dell',
    patrimonio='PAT001',
    serial='SER001',
    categoria='Notebook',
    setor='TI',
    responsavel='Caio',
    status='Em uso'
):
    return {
        'nome': nome,
        'patrimonio': patrimonio,
        'serial': serial,
        'categoria': categoria,
        'setor': setor,
        'responsavel': responsavel,
        'status': status,
        'data_cadastro': '25/08/2026 20:00',
        'ultima_atualizacao': '25/08/2026 20:00'
    }


class TestControleEquipamentos(unittest.TestCase):

    def setUp(self):
        self.pasta_temporaria = tempfile.TemporaryDirectory()
        self.arquivo_original = main.ARQUIVO_DADOS
        self.diretorio_original = os.getcwd()

        main.ARQUIVO_DADOS = str(
            Path(self.pasta_temporaria.name) / 'equipamentos.json'
        )

        os.chdir(self.pasta_temporaria.name)
        main.equipamentos.clear()

    def tearDown(self):
        main.equipamentos.clear()
        main.ARQUIVO_DADOS = self.arquivo_original
        os.chdir(self.diretorio_original)
        self.pasta_temporaria.cleanup()

    def juntar_impressoes(self, print_simulado):
        return ' '.join(
            str(chamada.args[0])
            for chamada in print_simulado.call_args_list
            if chamada.args
        )

    def test_cadastrar_equipamento(self):
        respostas = [
            'Notebook Dell',
            'pat001',
            'ser001',
            'Notebook',
            'TI',
            'Caio',
            '1'
        ]

        with patch(
            'builtins.input',
            side_effect=respostas
        ), patch('builtins.print'), patch.object(
            main,
            'obter_data_hora',
            return_value='25/08/2026 21:00'
        ):
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
        self.assertEqual(
            equipamento['data_cadastro'],
            '25/08/2026 21:00'
        )
        self.assertEqual(
            equipamento['ultima_atualizacao'],
            '25/08/2026 21:00'
        )
        self.assertTrue(Path(main.ARQUIVO_DADOS).exists())

    def test_bloquear_patrimonio_duplicado(self):
        main.equipamentos.append(criar_equipamento())

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

    def test_bloquear_serial_duplicado(self):
        main.equipamentos.append(criar_equipamento())

        respostas = [
            'Monitor',
            'PAT002',
            'SER001',
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

    def test_pesquisar_por_setor_e_status(self):
        main.equipamentos.append(criar_equipamento())

        pesquisas = [
            (['5', 'TI'], 'Notebook Dell'),
            (['7', 'Em uso'], 'Notebook Dell')
        ]

        for respostas, texto_esperado in pesquisas:
            with self.subTest(respostas=respostas), patch(
                'builtins.input',
                side_effect=respostas
            ), patch('builtins.print') as print_simulado:
                main.pesquisar_equipamento()

                saida = self.juntar_impressoes(print_simulado)
                self.assertIn(texto_esperado, saida)

    def test_editar_equipamento_e_criar_backup(self):
        main.equipamentos.append(criar_equipamento())
        main.salvar_equipamentos()

        respostas = [
            'PAT001',
            'Notebook Lenovo',
            'PAT002',
            'SER002',
            'Computador',
            'Financeiro',
            'João',
            '3',
            'S'
        ]

        with patch(
            'builtins.input',
            side_effect=respostas
        ), patch('builtins.print'), patch.object(
            main,
            'obter_data_hora',
            return_value='25/08/2026 22:00'
        ):
            main.editar_equipamento()

        equipamento = main.equipamentos[0]

        self.assertEqual(equipamento['nome'], 'Notebook Lenovo')
        self.assertEqual(equipamento['patrimonio'], 'PAT002')
        self.assertEqual(equipamento['serial'], 'SER002')
        self.assertEqual(equipamento['categoria'], 'Computador')
        self.assertEqual(equipamento['setor'], 'Financeiro')
        self.assertEqual(equipamento['responsavel'], 'João')
        self.assertEqual(equipamento['status'], 'Em manutenção')
        self.assertEqual(
            equipamento['ultima_atualizacao'],
            '25/08/2026 22:00'
        )

        caminho_backup = Path(
            self.pasta_temporaria.name,
            'equipamentos_backup.json'
        )
        self.assertTrue(caminho_backup.exists())

        with caminho_backup.open(encoding='utf-8') as arquivo:
            dados_backup = json.load(arquivo)

        self.assertEqual(dados_backup[0]['patrimonio'], 'PAT001')

    def test_bloquear_duplicado_durante_edicao(self):
        main.equipamentos.extend([
            criar_equipamento(),
            criar_equipamento(
                nome='Monitor',
                patrimonio='PAT002',
                serial='SER002',
                categoria='Monitor'
            )
        ])

        respostas = [
            'PAT001',
            '',
            'PAT002',
            '',
            '',
            '',
            ''
        ]

        with patch(
            'builtins.input',
            side_effect=respostas
        ), patch('builtins.print'):
            main.editar_equipamento()

        self.assertEqual(
            main.equipamentos[0]['patrimonio'],
            'PAT001'
        )

    def test_remover_equipamento_e_criar_backup(self):
        main.equipamentos.append(criar_equipamento())
        main.salvar_equipamentos()

        with patch(
            'builtins.input',
            side_effect=['PAT001', 'S']
        ), patch('builtins.print'):
            main.remover_equipamento()

        self.assertEqual(len(main.equipamentos), 0)
        self.assertTrue(
            Path(
                self.pasta_temporaria.name,
                'equipamentos_backup.json'
            ).exists()
        )

    def test_carregar_registros_antigos_e_preservar_datas(self):
        dados = [
            ['Monitor', 'PAT001', 'SER001'],
            criar_equipamento(
                nome='Notebook',
                patrimonio='PAT002',
                serial='SER002'
            )
        ]

        with open(main.ARQUIVO_DADOS, 'w', encoding='utf-8') as arquivo:
            json.dump(dados, arquivo, ensure_ascii=False)

        carregados = main.carregar_equipamentos()

        self.assertEqual(len(carregados), 2)
        self.assertEqual(
            carregados[0]['data_cadastro'],
            'Não informado'
        )
        self.assertEqual(
            carregados[1]['data_cadastro'],
            '25/08/2026 20:00'
        )

    def test_listar_ordenado_por_nome(self):
        main.equipamentos.extend([
            criar_equipamento(nome='Zebra', patrimonio='PAT002'),
            criar_equipamento(
                nome='Alpha',
                patrimonio='PAT001',
                serial='SER002'
            )
        ])

        with patch(
            'builtins.input',
            return_value='1'
        ), patch('builtins.print') as print_simulado:
            main.listar_equipamentos()

        saida = self.juntar_impressoes(print_simulado)

        self.assertLess(
            saida.index('Nome: Alpha'),
            saida.index('Nome: Zebra')
        )

    def test_mostrar_resumo_por_status_e_categoria(self):
        main.equipamentos.extend([
            criar_equipamento(),
            criar_equipamento(
                nome='Monitor',
                patrimonio='PAT002',
                serial='SER002',
                categoria='Monitor',
                status='Disponível'
            )
        ])

        with patch('builtins.print') as print_simulado:
            main.mostrar_resumo()

        saida = self.juntar_impressoes(print_simulado)

        self.assertIn('Total de equipamentos: 2', saida)
        self.assertIn('- Em uso: 1', saida)
        self.assertIn('- Disponível: 1', saida)
        self.assertIn('- Notebook: 1', saida)
        self.assertIn('- Monitor: 1', saida)

    def test_exportar_csv_com_datas(self):
        main.equipamentos.append(criar_equipamento())

        with patch('builtins.print'):
            main.exportar_csv()

        caminho_csv = Path('equipamentos.csv')
        self.assertTrue(caminho_csv.exists())

        with caminho_csv.open(
            encoding='utf-8-sig',
            newline=''
        ) as arquivo:
            linhas = list(csv.DictReader(arquivo, delimiter=';'))

        self.assertEqual(len(linhas), 1)
        self.assertEqual(
            linhas[0]['data_cadastro'],
            '25/08/2026 20:00'
        )
        self.assertEqual(
            linhas[0]['ultima_atualizacao'],
            '25/08/2026 20:00'
        )


if __name__ == '__main__':
    unittest.main()
