from flask import Flask, render_template

import banco


def criar_app(configuracao_teste=None):
    app = Flask(__name__)

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

    return app


app = criar_app()


if __name__ == '__main__':
    app.run(debug=True)
