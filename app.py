import csv
from datetime import datetime
from io import StringIO
from pathlib import Path
import shutil

from flask import (
    abort,
    flash,
    Flask,
    redirect,
    render_template,
    request,
    Response,
    url_for
)

import banco


STATUS_VALIDOS = [
    'Em uso',
    'Disponível',
    'Em manutenção',
    'Baixado'
]


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


def criar_app(configuracao_teste=None):
    app = Flask(__name__)
    app.config.from_mapping(SECRET_KEY='desenvolvimento')

    if configuracao_teste is not None:
        app.config.update(configuracao_teste)

    @app.get('/')
    def inicio():
        banco.criar_tabela()
        todos_equipamentos = banco.listar_equipamentos()

        termo = request.args.get('q', '').strip()
        status_selecionado = request.args.get('status', '').strip()
        categoria_selecionada = request.args.get('categoria', '').strip()

        equipamentos = todos_equipamentos

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
            equipamentos = [
                equipamento
                for equipamento in equipamentos
                if any(
                    termo_normalizado
                    in str(equipamento.get(campo, '')).casefold()
                    for campo in campos_pesquisa
                )
            ]

        if status_selecionado:
            equipamentos = [
                equipamento
                for equipamento in equipamentos
                if equipamento['status'] == status_selecionado
            ]

        if categoria_selecionada:
            equipamentos = [
                equipamento
                for equipamento in equipamentos
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

        filtros = {
            'termo': termo,
            'status': status_selecionado,
            'categoria': categoria_selecionada
        }

        return render_template(
            'index.html',
            equipamentos=equipamentos,
            resumo=resumo,
            quantidade_exibida=len(equipamentos),
            categorias=categorias,
            status_validos=STATUS_VALIDOS,
            filtros=filtros,
            filtros_ativos=any(filtros.values())
        )

    @app.route('/equipamentos/novo', methods=['GET', 'POST'])
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
                    banco.inserir_equipamento(novo_equipamento)

                except banco.ERROS_INTEGRIDADE:
                    flash(
                        'O patrimônio ou serial já está cadastrado.',
                        'erro'
                    )

                else:
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

            flash('Equipamento removido com sucesso!', 'sucesso')
            return redirect(url_for('inicio'))

        return render_template(
            'confirmar_remocao.html',
            equipamento=equipamento
        )

    @app.get('/equipamentos/exportar')
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

    @app.errorhandler(404)
    def pagina_nao_encontrada(_erro):
        return render_template('404.html'), 404

    return app


app = criar_app()


if __name__ == '__main__':
    app.run(debug=True)
