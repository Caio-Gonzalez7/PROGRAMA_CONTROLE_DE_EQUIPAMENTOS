from datetime import datetime
import sqlite3

from flask import flash, Flask, redirect, render_template, request, url_for

import banco


STATUS_VALIDOS = [
    'Em uso',
    'Disponível',
    'Em manutenção',
    'Baixado'
]


def obter_data_hora():
    return datetime.now().strftime('%d/%m/%Y %H:%M')


def criar_app(configuracao_teste=None):
    app = Flask(__name__)
    app.config.from_mapping(SECRET_KEY='desenvolvimento')

    if configuracao_teste is not None:
        app.config.update(configuracao_teste)

    @app.get('/')
    def inicio():
        banco.criar_tabela()
        equipamentos = banco.listar_equipamentos()

        resumo = {
            'total': len(equipamentos),
            'em_uso': sum(
                equipamento['status'] == 'Em uso'
                for equipamento in equipamentos
            ),
            'disponiveis': sum(
                equipamento['status'] == 'Disponível'
                for equipamento in equipamentos
            ),
            'manutencao': sum(
                equipamento['status'] == 'Em manutenção'
                for equipamento in equipamentos
            )
        }

        return render_template(
            'index.html',
            equipamentos=equipamentos,
            resumo=resumo
        )

    @app.route('/equipamentos/novo', methods=['GET', 'POST'])
    def cadastrar_equipamento():
        dados = {
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

        if request.method == 'POST':
            campos_obrigatorios = [
                dados['nome'],
                dados['patrimonio'],
                dados['serial'],
                dados['categoria'],
                dados['status']
            ]

            if not all(campos_obrigatorios):
                flash(
                    'Preencha todos os campos obrigatórios.',
                    'erro'
                )

            elif dados['status'] not in STATUS_VALIDOS:
                flash('Selecione um status válido.', 'erro')

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

                except sqlite3.IntegrityError:
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
            status_validos=STATUS_VALIDOS
        )

    return app


app = criar_app()


if __name__ == '__main__':
    app.run(debug=True)
