import os
import tempfile
import unittest
from pathlib import Path

os.environ['MODO_BANCO'] = 'sqlite'

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

    def test_formulario_de_cadastro_abre(self):
        resposta = self.cliente.get('/equipamentos/novo')

        self.assertEqual(resposta.status_code, 200)
        self.assertIn(
            'Cadastrar equipamento',
            resposta.get_data(as_text=True)
        )

    def test_cadastrar_equipamento_pela_interface(self):
        resposta = self.cliente.post(
            '/equipamentos/novo',
            data={
                'nome': 'Monitor LG',
                'patrimonio': 'pat002',
                'serial': 'ser002',
                'categoria': 'Monitor',
                'setor': 'Financeiro',
                'responsavel': 'João',
                'status': 'Disponível'
            },
            follow_redirects=True
        )

        conteudo = resposta.get_data(as_text=True)
        equipamentos = banco.listar_equipamentos()

        self.assertEqual(resposta.status_code, 200)
        self.assertIn('Equipamento cadastrado com sucesso!', conteudo)
        self.assertIn('Monitor LG', conteudo)
        self.assertEqual(len(equipamentos), 1)
        self.assertEqual(equipamentos[0]['patrimonio'], 'PAT002')

    def test_cadastro_bloqueia_patrimonio_duplicado(self):
        banco.criar_tabela()
        banco.inserir_equipamento(criar_equipamento())

        resposta = self.cliente.post(
            '/equipamentos/novo',
            data={
                'nome': 'Outro notebook',
                'patrimonio': 'PAT001',
                'serial': 'SER999',
                'categoria': 'Notebook',
                'status': 'Em uso'
            }
        )

        self.assertIn(
            'O patrimônio ou serial já está cadastrado.',
            resposta.get_data(as_text=True)
        )
        self.assertEqual(len(banco.listar_equipamentos()), 1)

    def test_pesquisar_e_filtrar_equipamentos(self):
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

        resposta = self.cliente.get(
            '/',
            query_string={
                'q': 'monitor',
                'status': 'Disponível'
            }
        )
        conteudo = resposta.get_data(as_text=True)

        self.assertIn('Monitor LG', conteudo)
        self.assertNotIn('Notebook Dell', conteudo)
        self.assertIn('1 registro(s) encontrado(s)', conteudo)

    def test_editar_equipamento_pela_interface_e_criar_backup(self):
        banco.criar_tabela()
        equipamento_id = banco.inserir_equipamento(criar_equipamento())

        resposta = self.cliente.post(
            f'/equipamentos/{equipamento_id}/editar',
            data={
                'nome': 'Notebook Lenovo',
                'patrimonio': 'PAT010',
                'serial': 'SER010',
                'categoria': 'Notebook',
                'setor': 'Financeiro',
                'responsavel': 'João',
                'status': 'Em manutenção'
            },
            follow_redirects=True
        )

        equipamento = banco.buscar_equipamento_por_id(equipamento_id)
        caminho_backup = Path(
            self.pasta_temporaria.name,
            'equipamentos_backup.db'
        )

        self.assertIn(
            'Equipamento atualizado com sucesso!',
            resposta.get_data(as_text=True)
        )
        self.assertEqual(equipamento['nome'], 'Notebook Lenovo')
        self.assertEqual(equipamento['patrimonio'], 'PAT010')
        self.assertEqual(equipamento['status'], 'Em manutenção')
        self.assertEqual(
            equipamento['data_cadastro'],
            '26/08/2026 20:00'
        )
        self.assertTrue(caminho_backup.exists())

    def test_edicao_bloqueia_patrimonio_duplicado(self):
        banco.criar_tabela()
        primeiro_id = banco.inserir_equipamento(criar_equipamento())
        banco.inserir_equipamento(
            criar_equipamento(
                nome='Monitor',
                patrimonio='PAT002',
                serial='SER002'
            )
        )

        resposta = self.cliente.post(
            f'/equipamentos/{primeiro_id}/editar',
            data={
                'nome': 'Notebook Dell',
                'patrimonio': 'PAT002',
                'serial': 'SER001',
                'categoria': 'Notebook',
                'status': 'Em uso'
            }
        )

        self.assertIn(
            'O patrimônio ou serial já está cadastrado.',
            resposta.get_data(as_text=True)
        )
        equipamento = banco.buscar_equipamento_por_id(primeiro_id)
        self.assertEqual(equipamento['patrimonio'], 'PAT001')

    def test_remover_equipamento_pela_interface_e_criar_backup(self):
        banco.criar_tabela()
        equipamento_id = banco.inserir_equipamento(criar_equipamento())

        confirmacao = self.cliente.get(
            f'/equipamentos/{equipamento_id}/remover'
        )
        resposta = self.cliente.post(
            f'/equipamentos/{equipamento_id}/remover',
            follow_redirects=True
        )

        self.assertIn(
            'Remover equipamento?',
            confirmacao.get_data(as_text=True)
        )
        self.assertIn(
            'Equipamento removido com sucesso!',
            resposta.get_data(as_text=True)
        )
        self.assertEqual(banco.listar_equipamentos(), [])
        self.assertTrue(
            Path(
                self.pasta_temporaria.name,
                'equipamentos_backup.db'
            ).exists()
        )

    def test_exportar_equipamentos_para_csv(self):
        banco.criar_tabela()
        banco.inserir_equipamento(criar_equipamento())

        resposta = self.cliente.get('/equipamentos/exportar')
        conteudo = resposta.get_data(as_text=True)

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.mimetype, 'text/csv')
        self.assertIn(
            'attachment; filename=equipamentos.csv',
            resposta.headers['Content-Disposition']
        )
        self.assertIn('Notebook Dell', conteudo)
        self.assertIn('PAT001', conteudo)
        self.assertIn('data_cadastro', conteudo)

    def test_equipamento_inexistente_retorna_404(self):
        resposta = self.cliente.get('/equipamentos/999/editar')

        self.assertEqual(resposta.status_code, 404)
        self.assertIn(
            'Página não encontrada',
            resposta.get_data(as_text=True)
        )


if __name__ == '__main__':
    unittest.main()
