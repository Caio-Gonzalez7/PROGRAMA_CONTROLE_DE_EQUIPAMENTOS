from io import BytesIO
import os
import tempfile
import unittest
from pathlib import Path

os.environ['MODO_BANCO'] = 'sqlite'

from werkzeug.security import generate_password_hash

import banco
from app import criar_app


class TestAutenticacaoERecursosProfissionais(unittest.TestCase):

    def setUp(self):
        self.pasta_temporaria = tempfile.TemporaryDirectory()
        self.arquivo_banco_original = banco.ARQUIVO_BANCO
        banco.ARQUIVO_BANCO = str(
            Path(self.pasta_temporaria.name) / 'equipamentos.db'
        )
        banco.criar_tabela()

        self.app = criar_app({
            'TESTING': True,
            'LOGIN_DISABLED': False,
            'WTF_CSRF_ENABLED': False,
            'SECRET_KEY': 'chave-de-testes'
        })
        self.cliente = self.app.test_client()

        self.criar_usuario(
            'Administrador',
            'admin@teste.com',
            'administrador'
        )
        self.criar_usuario('Operador', 'operador@teste.com', 'operador')
        self.criar_usuario('Consulta', 'consulta@teste.com', 'consulta')

    def tearDown(self):
        banco.ARQUIVO_BANCO = self.arquivo_banco_original
        self.pasta_temporaria.cleanup()

    def criar_usuario(self, nome, email, perfil):
        return banco.inserir_usuario({
            'nome': nome,
            'email': email,
            'senha_hash': generate_password_hash('Senha123'),
            'perfil': perfil,
            'ativo': True
        })

    def entrar(self, email='admin@teste.com', senha='Senha123'):
        return self.cliente.post(
            '/entrar',
            data={'email': email, 'senha': senha},
            follow_redirects=True
        )

    def equipamento_formulario(self, patrimonio='PAT001', serial='SER001'):
        return {
            'nome': 'Notebook Dell',
            'patrimonio': patrimonio,
            'serial': serial,
            'categoria': 'Notebook',
            'setor': 'TI',
            'responsavel': 'Caio',
            'status': 'Em uso'
        }

    def test_area_protegida_redireciona_para_login(self):
        resposta = self.cliente.get('/')

        self.assertEqual(resposta.status_code, 302)
        self.assertIn('/entrar', resposta.headers['Location'])

    def test_login_valido_e_senha_invalida(self):
        sucesso = self.entrar()
        self.assertIn('Bem-vindo, Administrador!', sucesso.get_data(as_text=True))

        self.cliente.post('/sair')
        erro = self.entrar(senha='senha-errada')
        self.assertIn('E-mail ou senha inválidos.', erro.get_data(as_text=True))

    def test_perfil_consulta_nao_altera_equipamentos(self):
        self.entrar('consulta@teste.com')

        cadastro = self.cliente.get('/equipamentos/novo')
        remocao = self.cliente.get('/equipamentos/1/remover')

        self.assertEqual(cadastro.status_code, 403)
        self.assertEqual(remocao.status_code, 403)

    def test_operador_cadastra_mas_nao_remove(self):
        self.entrar('operador@teste.com')
        cadastro = self.cliente.post(
            '/equipamentos/novo',
            data=self.equipamento_formulario(),
            follow_redirects=True
        )
        equipamento_id = banco.listar_equipamentos()[0]['id']
        remocao = self.cliente.get(
            f'/equipamentos/{equipamento_id}/remover'
        )

        self.assertIn(
            'Equipamento cadastrado com sucesso!',
            cadastro.get_data(as_text=True)
        )
        self.assertEqual(remocao.status_code, 403)

    def test_administrador_cria_usuario(self):
        self.entrar()
        resposta = self.cliente.post(
            '/usuarios',
            data={
                'nome': 'Novo usuário',
                'email': 'novo@teste.com',
                'senha': 'Senha456',
                'perfil': 'consulta'
            },
            follow_redirects=True
        )

        self.assertIn('Usuário criado com sucesso!', resposta.get_data(as_text=True))
        self.assertIsNotNone(banco.buscar_usuario_por_email('novo@teste.com'))

    def test_cadastro_registra_historico_e_gera_qrcode(self):
        self.entrar()
        self.cliente.post(
            '/equipamentos/novo',
            data=self.equipamento_formulario(),
            follow_redirects=True
        )
        equipamento_id = banco.listar_equipamentos()[0]['id']
        historico = banco.listar_historico()
        resposta_qr = self.cliente.get(
            f'/equipamentos/{equipamento_id}/qrcode'
        )

        self.assertEqual(historico[0]['acao'], 'Cadastro')
        self.assertEqual(historico[0]['usuario_nome'], 'Administrador')
        self.assertEqual(resposta_qr.status_code, 200)
        self.assertEqual(resposta_qr.mimetype, 'image/png')

    def test_importar_csv_e_paginar(self):
        self.entrar()
        linhas = [
            'nome;patrimonio;serial;categoria;setor;responsavel;status'
        ]

        for numero in range(1, 12):
            linhas.append(
                f'Equipamento {numero};PAT{numero:03};SER{numero:03};'
                'Notebook;TI;Caio;Em uso'
            )

        resposta = self.cliente.post(
            '/equipamentos/importar',
            data={
                'arquivo': (
                    BytesIO('\n'.join(linhas).encode('utf-8')),
                    'equipamentos.csv'
                )
            },
            content_type='multipart/form-data',
            follow_redirects=True
        )
        pagina_dois = self.cliente.get('/?pagina=2')

        self.assertIn('11 importado(s)', resposta.get_data(as_text=True))
        self.assertIn('Página 1 de 2', resposta.get_data(as_text=True))
        self.assertIn('Equipamento 11', pagina_dois.get_data(as_text=True))


if __name__ == '__main__':
    unittest.main()
