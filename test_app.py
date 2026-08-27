import os
import tempfile
import unittest
from pathlib import Path

import banco
from app import criar_app


def criar_equipamento(
    nome='Notebook Dell',
    patrimonio='PAT001',
    serial='SER001',
    status='Em uso'
):
    return {
        'nome': nome,
        'patrimonio': patrimonio,
        'serial': serial,
        'categoria': 'Notebook',
        'setor': 'TI',
        'responsavel': 'Caio',
        'status': status,
        'data_cadastro': '26/08/2026 20:00',
        'ultima_atualizacao': '26/08/2026 20:00'
    }


class TestInterfaceFlask(unittest.TestCase):

    def setUp(self):
        self.pasta_temporaria = tempfile.TemporaryDirectory()
        self.arquivo_banco_original = banco.ARQUIVO_BANCO
        self.diretorio_original = os.getcwd()

        pasta = Path(self.pasta_temporaria.name)
        banco.ARQUIVO_BANCO = str(pasta / 'equipamentos.db')
        os.chdir(pasta)

        self.app = criar_app({'TESTING': True})
        self.cliente = self.app.test_client()

    def tearDown(self):
        banco.ARQUIVO_BANCO = self.arquivo_banco_original
        os.chdir(self.diretorio_original)
        self.pasta_temporaria.cleanup()

    def test_pagina_inicial_sem_equipamentos(self):
        resposta = self.cliente.get('/')

        self.assertEqual(resposta.status_code, 200)
        self.assertIn(
            'Nenhum equipamento cadastrado',
            resposta.get_data(as_text=True)
        )

    def test_pagina_inicial_lista_equipamento(self):
        banco.criar_tabela()
        banco.inserir_equipamento(criar_equipamento())

        resposta = self.cliente.get('/')
        conteudo = resposta.get_data(as_text=True)

        self.assertEqual(resposta.status_code, 200)
        self.assertIn('Notebook Dell', conteudo)
        self.assertIn('PAT001', conteudo)
        self.assertIn('SER001', conteudo)
        self.assertIn('Em uso', conteudo)

    def test_pagina_inicial_calcula_resumo(self):
        banco.criar_tabela()
        banco.inserir_equipamento(criar_equipamento())
        banco.inserir_equipamento(
            criar_equipamento(
                nome='Monitor LG',
                patrimonio='PAT002',
                serial='SER002',
                status='Disponível'
            )
        )

        conteudo = self.cliente.get('/').get_data(as_text=True)

        self.assertIn('Total de equipamentos', conteudo)
        self.assertIn('Disponíveis', conteudo)
        self.assertIn('2 registro(s) encontrado(s)', conteudo)


if __name__ == '__main__':
    unittest.main()
