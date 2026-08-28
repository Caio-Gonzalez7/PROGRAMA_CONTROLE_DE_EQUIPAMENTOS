from functools import wraps

from flask import abort, current_app
from flask_login import current_user, login_required, UserMixin


PERFIS = {
    'administrador': 'Administrador',
    'operador': 'Operador',
    'consulta': 'Consulta'
}


class Usuario(UserMixin):

    def __init__(self, dados):
        self.id = dados['id']
        self.nome = dados['nome']
        self.email = dados['email']
        self.senha_hash = dados['senha_hash']
        self.perfil = dados['perfil']
        self.ativo = bool(dados['ativo'])

    @property
    def is_active(self):
        return self.ativo

    def get_id(self):
        return str(self.id)


def perfis_permitidos(*perfis):
    def decorar(funcao):
        @wraps(funcao)
        @login_required
        def protegida(*args, **kwargs):
            if current_app.config.get('LOGIN_DISABLED'):
                return funcao(*args, **kwargs)

            if current_user.perfil not in perfis:
                abort(403)

            return funcao(*args, **kwargs)

        return protegida

    return decorar
