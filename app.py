import csv
from datetime import datetime
from io import BytesIO, StringIO
import math
import os
from pathlib import Path
import shutil
from urllib.parse import urlsplit

from flask import (
    abort,
    flash,
    Flask,
    redirect,
    render_template,
    request,
    Response,
    send_file,
    url_for
)
from flask_login import (
    current_user,
    LoginManager,
    login_required,
    login_user,
    logout_user
)
from flask_wtf.csrf import CSRFProtect
import qrcode
from werkzeug.security import check_password_hash, generate_password_hash

from autenticacao import PERFIS, perfis_permitidos, Usuario
import banco


STATUS_VALIDOS = [
    'Em uso',
    'Disponível',
    'Em manutenção',
    'Baixado'
]
ITENS_POR_PAGINA = 10


def obter_data_hora():
    return datetime.now().strftime('%d/%m/%Y %H:%M')


def obter_dados_formulario():
    return {
        'nome': request.form.get('nome', '').strip(),
        'patrimonio': request.form.get(
            'patrimonio',
            ''
        ).strip().upper(),
        'serial': request.form.get('serial', '').strip().upper(),
        'categoria': request.form.get('categoria', '').strip(),
        'setor': request.form.get('setor', '').strip(),
        'responsavel': request.form.get('responsavel', '').strip(),
        'status': request.form.get('status', '').strip()
    }


def validar_dados(dados):
    campos_obrigatorios = [
        dados['nome'],
        dados['patrimonio'],
        dados['serial'],
        dados['categoria'],
        dados['status']
    ]

    if not all(campos_obrigatorios):
        return 'Preencha todos os campos obrigatórios.'

    if dados['status'] not in STATUS_VALIDOS:
        return 'Selecione um status válido.'

    return None


def criar_backup():
    if banco.usa_postgres():
        return

    caminho_banco = Path(banco.ARQUIVO_BANCO)

    if not caminho_banco.exists():
        return

    caminho_backup = caminho_banco.with_name('equipamentos_backup.db')
    shutil.copy2(caminho_banco, caminho_backup)


def registrar_acao(equipamento_id, acao, detalhes):
    if current_user.is_authenticated:
        usuario_id = int(current_user.get_id())
        usuario_nome = current_user.nome
    else:
        usuario_id = None
        usuario_nome = 'Sistema de testes'

    banco.registrar_historico(
        equipamento_id,
        usuario_id,
        usuario_nome,
        acao,
        detalhes
    )


def destino_login_seguro(destino):
    if not destino:
        return None

    partes = urlsplit(destino)

    if partes.scheme or partes.netloc:
        return None

    return destino if destino.startswith('/') else None


def criar_app(configuracao_teste=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.getenv(
            'FLASK_SECRET_KEY',
            'desenvolvimento-local-troque-em-producao'
        ),
        LOGIN_DISABLED=False,
        MAX_CONTENT_LENGTH=2 * 1024 * 1024,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        SESSION_COOKIE_SECURE=(
            os.getenv('FLASK_ENV', '').lower() == 'production'
        ),
        WTF_CSRF_ENABLED=True
    )

    configuracao_teste = configuracao_teste or {}
    app.config.update(configuracao_teste)

    if app.config['TESTING']:
        if 'LOGIN_DISABLED' not in configuracao_teste:
            app.config['LOGIN_DISABLED'] = True
        if 'WTF_CSRF_ENABLED' not in configuracao_teste:
            app.config['WTF_CSRF_ENABLED'] = False

    csrf = CSRFProtect()
    csrf.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'entrar'
    login_manager.login_message = 'Entre com sua conta para continuar.'
    login_manager.login_message_category = 'erro'
    login_manager.init_app(app)

    @login_manager.user_loader
    def carregar_usuario(usuario_id):
        try:
            dados = banco.buscar_usuario_por_id(int(usuario_id))
        except (TypeError, ValueError):
            return None

        return Usuario(dados) if dados and dados['ativo'] else None

    @app.context_processor
    def contexto_global():
        return {
            'nome_backend': banco.nome_backend(),
            'perfis': PERFIS
        }

    @app.route('/entrar', methods=['GET', 'POST'])
    def entrar():
        if current_user.is_authenticated:
            return redirect(url_for('inicio'))

        email = request.form.get('email', '').strip().lower()
        lembrar = request.form.get('lembrar') == '1'

        if request.method == 'POST':
            banco.criar_tabela()
            usuario = banco.buscar_usuario_por_email(email)
            senha = request.form.get('senha', '')

            if (
                usuario is None
                or not usuario['ativo']
                or not check_password_hash(usuario['senha_hash'], senha)
            ):
                flash('E-mail ou senha inválidos.', 'erro')
            else:
                login_user(Usuario(usuario), remember=lembrar)
                flash(f"Bem-vindo, {usuario['nome']}!", 'sucesso')
                destino = destino_login_seguro(request.args.get('next'))
                return redirect(destino or url_for('inicio'))

        return render_template('login.html', email=email)

    @app.post('/sair')
    @login_required
    def sair():
        logout_user()
        flash('Sessão encerrada com segurança.', 'sucesso')
        return redirect(url_for('entrar'))

    @app.get('/health')
    def health():
        try:
            banco.criar_tabela()
            banco.listar_equipamentos()
        except Exception:
            return {'status': 'erro'}, 503

        return {'status': 'ok', 'banco': banco.nome_backend()}

    @app.get('/')
    @login_required
    def inicio():
        banco.criar_tabela()
        todos_equipamentos = banco.listar_equipamentos()

        termo = request.args.get('q', '').strip()
        status_selecionado = request.args.get('status', '').strip()
        categoria_selecionada = request.args.get('categoria', '').strip()

        equipamentos_filtrados = todos_equipamentos

        if termo:
            termo_normalizado = termo.casefold()
            campos_pesquisa = [
                'nome',
                'patrimonio',
                'serial',
                'categoria',
                'setor',
                'responsavel'
            ]
            equipamentos_filtrados = [
                equipamento
                for equipamento in equipamentos_filtrados
                if any(
                    termo_normalizado
                    in str(equipamento.get(campo, '')).casefold()
                    for campo in campos_pesquisa
                )
            ]

        if status_selecionado:
            equipamentos_filtrados = [
                equipamento
                for equipamento in equipamentos_filtrados
                if equipamento['status'] == status_selecionado
            ]

        if categoria_selecionada:
            equipamentos_filtrados = [
                equipamento
                for equipamento in equipamentos_filtrados
                if equipamento['categoria'] == categoria_selecionada
            ]

        resumo = {
            'total': len(todos_equipamentos),
            'em_uso': sum(
                equipamento['status'] == 'Em uso'
                for equipamento in todos_equipamentos
            ),
            'disponiveis': sum(
                equipamento['status'] == 'Disponível'
                for equipamento in todos_equipamentos
            ),
            'manutencao': sum(
                equipamento['status'] == 'Em manutenção'
                for equipamento in todos_equipamentos
            ),
            'baixados': sum(
                equipamento['status'] == 'Baixado'
                for equipamento in todos_equipamentos
            )
        }

        categorias = sorted(
            {
                equipamento['categoria']
                for equipamento in todos_equipamentos
            },
            key=str.casefold
        )
        quantidades_categoria = {
            categoria: sum(
                equipamento['categoria'] == categoria
                for equipamento in todos_equipamentos
            )
            for categoria in categorias
        }

        try:
            pagina = max(1, int(request.args.get('pagina', 1)))
        except ValueError:
            pagina = 1

        quantidade_exibida = len(equipamentos_filtrados)
        total_paginas = max(
            1,
            math.ceil(quantidade_exibida / ITENS_POR_PAGINA)
        )
        pagina = min(pagina, total_paginas)
        inicio_pagina = (pagina - 1) * ITENS_POR_PAGINA
        equipamentos = equipamentos_filtrados[
            inicio_pagina:inicio_pagina + ITENS_POR_PAGINA
        ]

        filtros = {
            'termo': termo,
            'status': status_selecionado,
            'categoria': categoria_selecionada
        }

        return render_template(
            'index.html',
            equipamentos=equipamentos,
            resumo=resumo,
            quantidade_exibida=quantidade_exibida,
            categorias=categorias,
            quantidades_categoria=quantidades_categoria,
            status_validos=STATUS_VALIDOS,
            filtros=filtros,
            filtros_ativos=any(filtros.values()),
            pagina=pagina,
            total_paginas=total_paginas
        )

    @app.get('/equipamentos/<int:equipamento_id>')
    @login_required
    def detalhar_equipamento(equipamento_id):
        banco.criar_tabela()
        equipamento = banco.buscar_equipamento_por_id(equipamento_id)

        if equipamento is None:
            abort(404)

        return render_template(
            'detalhe_equipamento.html',
            equipamento=equipamento
        )

    @app.route('/equipamentos/novo', methods=['GET', 'POST'])
    @perfis_permitidos('administrador', 'operador')
    def cadastrar_equipamento():
        dados = obter_dados_formulario()

        if request.method == 'POST':
            erro = validar_dados(dados)

            if erro:
                flash(erro, 'erro')

            else:
                data_atual = obter_data_hora()
                novo_equipamento = {
                    **dados,
                    'setor': dados['setor'] or 'Não informado',
                    'responsavel': (
                        dados['responsavel'] or 'Não informado'
                    ),
                    'data_cadastro': data_atual,
                    'ultima_atualizacao': data_atual
                }

                try:
                    banco.criar_tabela()
                    novo_id = banco.inserir_equipamento(novo_equipamento)

                except banco.ERROS_INTEGRIDADE:
                    flash(
                        'O patrimônio ou serial já está cadastrado.',
                        'erro'
                    )

                else:
                    registrar_acao(
                        novo_id,
                        'Cadastro',
                        {'equipamento': novo_equipamento}
                    )
                    flash('Equipamento cadastrado com sucesso!', 'sucesso')
                    return redirect(url_for('inicio'))

        return render_template(
            'form_equipamento.html',
            dados=dados,
            status_validos=STATUS_VALIDOS,
            titulo_pagina='Cadastrar equipamento',
            sobretitulo='NOVO REGISTRO',
            descricao_pagina=(
                'Preencha os dados abaixo para adicionar um item ao controle.'
            ),
            texto_botao='Salvar equipamento'
        )

    @app.route(
        '/equipamentos/<int:equipamento_id>/editar',
        methods=['GET', 'POST']
    )
    @perfis_permitidos('administrador', 'operador')
    def editar_equipamento(equipamento_id):
        banco.criar_tabela()
        equipamento = banco.buscar_equipamento_por_id(equipamento_id)

        if equipamento is None:
            abort(404)

        dados = (
            obter_dados_formulario()
            if request.method == 'POST'
            else equipamento.copy()
        )

        if request.method == 'POST':
            erro = validar_dados(dados)

            if erro:
                flash(erro, 'erro')

            else:
                equipamento_atualizado = {
                    **equipamento,
                    **dados,
                    'setor': dados['setor'] or 'Não informado',
                    'responsavel': (
                        dados['responsavel'] or 'Não informado'
                    ),
                    'ultima_atualizacao': obter_data_hora()
                }

                criar_backup()

                try:
                    atualizou = banco.atualizar_equipamento(
                        equipamento_atualizado
                    )

                except banco.ERROS_INTEGRIDADE:
                    flash(
                        'O patrimônio ou serial já está cadastrado.',
                        'erro'
                    )

                else:
                    if atualizou:
                        registrar_acao(
                            equipamento_id,
                            'Edição',
                            {
                                'antes': equipamento,
                                'depois': equipamento_atualizado
                            }
                        )
                        flash(
                            'Equipamento atualizado com sucesso!',
                            'sucesso'
                        )
                        return redirect(url_for('inicio'))

                    abort(404)

        return render_template(
            'form_equipamento.html',
            dados=dados,
            status_validos=STATUS_VALIDOS,
            titulo_pagina='Editar equipamento',
            sobretitulo='ATUALIZAR REGISTRO',
            descricao_pagina=(
                'Altere os campos necessários e salve a nova versão.'
            ),
            texto_botao='Salvar alterações'
        )

    @app.route(
        '/equipamentos/<int:equipamento_id>/remover',
        methods=['GET', 'POST']
    )
    @perfis_permitidos('administrador')
    def remover_equipamento(equipamento_id):
        banco.criar_tabela()
        equipamento = banco.buscar_equipamento_por_id(equipamento_id)

        if equipamento is None:
            abort(404)

        if request.method == 'POST':
            criar_backup()
            removeu = banco.remover_equipamento(equipamento_id)

            if not removeu:
                abort(404)

            registrar_acao(
                equipamento_id,
                'Remoção',
                {'equipamento': equipamento}
            )
            flash('Equipamento removido com sucesso!', 'sucesso')
            return redirect(url_for('inicio'))

        return render_template(
            'confirmar_remocao.html',
            equipamento=equipamento
        )

    @app.route('/equipamentos/importar', methods=['GET', 'POST'])
    @perfis_permitidos('administrador', 'operador')
    def importar_equipamentos():
        if request.method == 'POST':
            arquivo_enviado = request.files.get('arquivo')

            if arquivo_enviado is None or not arquivo_enviado.filename:
                flash('Selecione um arquivo CSV.', 'erro')
                return render_template('importar.html')

            try:
                conteudo = arquivo_enviado.read().decode('utf-8-sig')
                amostra = conteudo[:2048]
                dialeto = csv.Sniffer().sniff(amostra, delimiters=';,')
                leitor = csv.DictReader(StringIO(conteudo), dialect=dialeto)
            except (UnicodeDecodeError, csv.Error):
                flash('Não foi possível ler o arquivo CSV.', 'erro')
                return render_template('importar.html')

            importados = 0
            ignorados = 0
            banco.criar_tabela()

            for linha in leitor:
                dados = {
                    'nome': (linha.get('nome') or '').strip(),
                    'patrimonio': (
                        linha.get('patrimonio') or ''
                    ).strip().upper(),
                    'serial': (linha.get('serial') or '').strip().upper(),
                    'categoria': (linha.get('categoria') or '').strip(),
                    'setor': (
                        linha.get('setor') or 'Não informado'
                    ).strip(),
                    'responsavel': (
                        linha.get('responsavel') or 'Não informado'
                    ).strip(),
                    'status': (linha.get('status') or '').strip()
                }

                if validar_dados(dados):
                    ignorados += 1
                    continue

                data_atual = obter_data_hora()
                equipamento = {
                    **dados,
                    'data_cadastro': (
                        linha.get('data_cadastro') or data_atual
                    ).strip(),
                    'ultima_atualizacao': (
                        linha.get('ultima_atualizacao') or data_atual
                    ).strip()
                }

                try:
                    equipamento_id = banco.inserir_equipamento(equipamento)
                except banco.ERROS_INTEGRIDADE:
                    ignorados += 1
                else:
                    importados += 1
                    registrar_acao(
                        equipamento_id,
                        'Importação CSV',
                        {'equipamento': equipamento}
                    )

            flash(
                f'Importação concluída: {importados} importado(s) e '
                f'{ignorados} ignorado(s).',
                'sucesso'
            )
            return redirect(url_for('inicio'))

        return render_template('importar.html')

    @app.get('/equipamentos/exportar')
    @login_required
    def exportar_equipamentos():
        banco.criar_tabela()
        equipamentos = banco.listar_equipamentos()

        campos = [
            'nome',
            'patrimonio',
            'serial',
            'categoria',
            'setor',
            'responsavel',
            'status',
            'data_cadastro',
            'ultima_atualizacao'
        ]

        arquivo = StringIO(newline='')
        escritor = csv.DictWriter(
            arquivo,
            fieldnames=campos,
            delimiter=';',
            extrasaction='ignore'
        )
        escritor.writeheader()
        escritor.writerows(equipamentos)

        return Response(
            '\ufeff' + arquivo.getvalue(),
            mimetype='text/csv',
            headers={
                'Content-Disposition': (
                    'attachment; filename=equipamentos.csv'
                )
            }
        )

    @app.get('/equipamentos/<int:equipamento_id>/qrcode')
    @login_required
    def qrcode_equipamento(equipamento_id):
        equipamento = banco.buscar_equipamento_por_id(equipamento_id)

        if equipamento is None:
            abort(404)

        endereco = url_for(
            'detalhar_equipamento',
            equipamento_id=equipamento_id,
            _external=True
        )
        imagem = qrcode.make(endereco)
        arquivo = BytesIO()
        imagem.save(arquivo, format='PNG')
        arquivo.seek(0)

        return send_file(
            arquivo,
            mimetype='image/png',
            download_name=f"qr-{equipamento['patrimonio']}.png"
        )

    @app.get('/historico')
    @login_required
    def historico():
        banco.criar_tabela()
        return render_template(
            'historico.html',
            registros=banco.listar_historico()
        )

    @app.route('/usuarios', methods=['GET', 'POST'])
    @perfis_permitidos('administrador')
    def usuarios():
        banco.criar_tabela()

        if request.method == 'POST':
            nome = request.form.get('nome', '').strip()
            email = request.form.get('email', '').strip().lower()
            senha = request.form.get('senha', '')
            perfil = request.form.get('perfil', '')

            if not nome or not email or len(senha) < 8:
                flash(
                    'Informe nome, e-mail e uma senha com pelo menos 8 caracteres.',
                    'erro'
                )
            elif perfil not in PERFIS:
                flash('Selecione um perfil válido.', 'erro')
            else:
                try:
                    banco.inserir_usuario({
                        'nome': nome,
                        'email': email,
                        'senha_hash': generate_password_hash(senha),
                        'perfil': perfil,
                        'ativo': True
                    })
                except banco.ERROS_INTEGRIDADE:
                    flash('Este e-mail já está cadastrado.', 'erro')
                else:
                    flash('Usuário criado com sucesso!', 'sucesso')
                    return redirect(url_for('usuarios'))

        return render_template(
            'usuarios.html',
            usuarios=banco.listar_usuarios()
        )

    @app.route('/usuarios/<int:usuario_id>/editar', methods=['GET', 'POST'])
    @perfis_permitidos('administrador')
    def editar_usuario(usuario_id):
        banco.criar_tabela()
        usuario = banco.buscar_usuario_por_id(usuario_id)

        if usuario is None:
            abort(404)

        if request.method == 'POST':
            nome = request.form.get('nome', '').strip()
            email = request.form.get('email', '').strip().lower()
            perfil = request.form.get('perfil', '')
            ativo = request.form.get('ativo') == '1'
            nova_senha = request.form.get('senha', '')

            if not nome or not email or perfil not in PERFIS:
                flash('Preencha os dados corretamente.', 'erro')
            elif current_user.is_authenticated and usuario_id == current_user.id and not ativo:
                flash('Você não pode desativar a própria conta.', 'erro')
            elif nova_senha and len(nova_senha) < 8:
                flash('A nova senha precisa ter pelo menos 8 caracteres.', 'erro')
            else:
                usuario_atualizado = {
                    **usuario,
                    'nome': nome,
                    'email': email,
                    'perfil': perfil,
                    'ativo': ativo
                }

                try:
                    banco.atualizar_usuario(usuario_atualizado)
                    if nova_senha:
                        banco.atualizar_senha_usuario(
                            usuario_id,
                            generate_password_hash(nova_senha)
                        )
                except banco.ERROS_INTEGRIDADE:
                    flash('Este e-mail já está cadastrado.', 'erro')
                else:
                    flash('Usuário atualizado com sucesso!', 'sucesso')
                    return redirect(url_for('usuarios'))

        return render_template('editar_usuario.html', usuario=usuario)

    @app.errorhandler(403)
    def acesso_negado(_erro):
        return render_template('403.html'), 403

    @app.errorhandler(404)
    def pagina_nao_encontrada(_erro):
        return render_template('404.html'), 404

    return app


app = criar_app()


if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG') == '1')
