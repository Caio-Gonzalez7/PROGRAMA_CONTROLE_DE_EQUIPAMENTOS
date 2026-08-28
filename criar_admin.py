from getpass import getpass

from werkzeug.security import generate_password_hash

import banco


def criar_administrador():
    banco.criar_tabela()
    print(f'Banco conectado: {banco.nome_backend()}')

    nome = input('Nome do administrador: ').strip()
    email = input('E-mail do administrador: ').strip().lower()

    if not nome or not email:
        print('Nome e e-mail são obrigatórios.')
        return 1

    if banco.buscar_usuario_por_email(email):
        print('Já existe um usuário com esse e-mail.')
        return 1

    senha = getpass('Senha (mínimo de 8 caracteres): ')
    confirmacao = getpass('Confirme a senha: ')

    if len(senha) < 8:
        print('A senha precisa ter pelo menos 8 caracteres.')
        return 1

    if senha != confirmacao:
        print('As senhas não são iguais.')
        return 1

    banco.inserir_usuario({
        'nome': nome,
        'email': email,
        'senha_hash': generate_password_hash(senha),
        'perfil': 'administrador',
        'ativo': True
    })
    print('Administrador criado com sucesso!')
    return 0


if __name__ == '__main__':
    raise SystemExit(criar_administrador())
