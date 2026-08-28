import csv
import json
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ['MODO_BANCO'] = 'sqlite'

import banco
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
        self.arquivo_json_original = main.ARQUIVO_DADOS
        self.arquivo_banco_original = banco.ARQUIVO_BANCO
        self.diretorio_original = os.getcwd()

        pasta = Path(self.pasta_temporaria.name)
        main.ARQUIVO_DADOS = str(pasta / 'equipamentos.json')
        banco.ARQUIVO_BANCO = str(pasta / 'equipamentos.db')

        os.chdir(pasta)
        banco.criar_tabela()
        main.equipamentos.clear()

    def tearDown(self):
        main.equipamentos.clear()
        main.ARQUIVO_DADOS = self.arquivo_json_original
        banco.ARQUIVO_BANCO = self.arquivo_banco_original
        os.chdir(self.diretorio_original)
        self.pasta_temporaria.cleanup()

    def salvar_no_banco(self, equipamento):
        equipamento_salvo = equipamento.copy()
        equipamento_salvo['id'] = banco.inserir_equipamento(
            equipamento_salvo
        )
        main.equipamentos.append(equipamento_salvo)
        return equipamento_salvo

    def juntar_impressoes(self, print_simulado):
        return ' '.join(
            str(chamada.args[0])
            for chamada in print_simulado.call_args_list
            if chamada.args
        )

    def test_cadastrar_equipamento_no_sqlite(self):
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
        self.assertTrue(Path(banco.ARQUIVO_BANCO).exists())

        equipamento = banco.listar_equipamentos()[0]

        self.assertIsInstance(equipamento['id'], int)
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

    def test_banco_bloqueia_patrimonio_duplicado(self):
        banco.inserir_equipamento(criar_equipamento())

        duplicado = criar_equipamento(serial='SER002')

        with self.assertRaises(sqlite3.IntegrityError):
            banco.inserir_equipamento(duplicado)

    def test_banco_bloqueia_serial_duplicado(self):
        banco.inserir_equipamento(criar_equipamento())

        duplicado = criar_equipamento(patrimonio='PAT002')

        with self.assertRaises(sqlite3.IntegrityError):
            banco.inserir_equipamento(duplicado)

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

    def test_editar_equipamento_no_sqlite_e_criar_backup(self):
        self.salvar_no_banco(criar_equipamento())

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

        equipamento = banco.listar_equipamentos()[0]

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
            'equipamentos_backup.db'
        )
        self.assertTrue(caminho_backup.exists())

        conexao_backup = sqlite3.connect(caminho_backup)

        try:
            patrimonio_antigo = conexao_backup.execute(
                'SELECT patrimonio FROM equipamentos'
            ).fetchone()[0]

        finally:
            conexao_backup.close()

        self.assertEqual(patrimonio_antigo, 'PAT001')

    def test_bloquear_duplicado_durante_edicao(self):
        self.salvar_no_banco(criar_equipamento())
        self.salvar_no_banco(
            criar_equipamento(
                nome='Monitor',
                patrimonio='PAT002',
                serial='SER002',
                categoria='Monitor'
            )
        )

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

        equipamentos_salvos = banco.listar_equipamentos()
        self.assertEqual(equipamentos_salvos[0]['patrimonio'], 'PAT001')

    def test_remover_equipamento_do_sqlite_e_criar_backup(self):
        self.salvar_no_banco(criar_equipamento())

        with patch(
            'builtins.input',
            side_effect=['PAT001', 'S']
        ), patch('builtins.print'):
            main.remover_equipamento()

        self.assertEqual(main.equipamentos, [])
        self.assertEqual(banco.listar_equipamentos(), [])
        self.assertTrue(
            Path(
                self.pasta_temporaria.name,
                'equipamentos_backup.db'
            ).exists()
        )

    def test_migrar_json_uma_unica_vez_e_preservar_datas(self):
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

        primeira_carga = main.iniciar_banco()
        segunda_carga = main.iniciar_banco()

        self.assertEqual(len(primeira_carga), 2)
        self.assertEqual(len(segunda_carga), 2)
        self.assertTrue(banco.migracao_json_concluida())
        self.assertEqual(
            primeira_carga[0]['data_cadastro'],
            'Não informado'
        )
        self.assertEqual(
            primeira_carga[1]['data_cadastro'],
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
