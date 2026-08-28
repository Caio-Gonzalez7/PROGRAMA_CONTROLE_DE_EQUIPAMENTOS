# Controle de Equipamentos

Aplicação web para administrar equipamentos de TI com banco PostgreSQL na nuvem, autenticação, níveis de acesso e histórico de alterações. O projeto começou como um exercício de Python no terminal e evoluiu para um sistema Flask completo, testado e preparado para produção.

## Demonstração online

Acesse o sistema publicado: [controle-equipamentos-caio.onrender.com](https://controle-equipamentos-caio.onrender.com)

> O plano gratuito do Render pode levar cerca de 50 segundos para iniciar após um período sem acessos.

## Funcionalidades

- Dashboard com resumo e gráficos por status e categoria
- Cadastro, consulta, pesquisa, filtros, edição e remoção
- PostgreSQL hospedado no Supabase, com opção de SQLite local
- Login com senhas armazenadas por hash
- Perfis Administrador, Operador e Consulta
- Gestão de usuários e ativação de contas
- Histórico com usuário, ação, equipamento, data e hora
- Importação e exportação em CSV
- Paginação da listagem
- Página individual e QR Code para cada equipamento
- Proteção CSRF em formulários
- Verificação de integridade e bloqueio de duplicidades
- Health check para monitoramento em produção
- Testes automáticos no GitHub Actions

## Permissões

| Perfil | Consultar | Cadastrar e editar | Remover | Gerenciar usuários |
|---|:---:|:---:|:---:|:---:|
| Administrador | Sim | Sim | Sim | Sim |
| Operador | Sim | Sim | Não | Não |
| Consulta | Sim | Não | Não | Não |

## Tecnologias

- Python 3.14
- Flask, Flask-Login e Flask-WTF
- PostgreSQL/Supabase e SQLite
- Psycopg 3
- HTML e CSS responsivos
- QR Code e CSV
- unittest e GitHub Actions
- Gunicorn e Render Blueprint

## Instalação

```bash
git clone https://github.com/Caio-Gonzalez7/PROGRAMA_CONTROLE_DE_EQUIPAMENTOS.git
cd PROGRAMA_CONTROLE_DE_EQUIPAMENTOS
python -m pip install -r requirements.txt
```

Copie `.env.example` para `.env` e configure:

```env
DATABASE_URL=postgresql://USUARIO:SENHA@HOST:5432/postgres
FLASK_SECRET_KEY=uma-chave-longa-e-aleatoria
FLASK_ENV=development
```

O arquivo `.env` é ignorado pelo Git e nunca deve ser enviado ao repositório.

## Primeiro administrador

Após configurar o banco, execute:

```bash
python criar_admin.py
```

Informe nome, e-mail e uma senha com no mínimo oito caracteres. Depois inicie a aplicação:

```bash
python app.py
```

Acesse `http://127.0.0.1:5000`.

## Migração do SQLite

Para copiar equipamentos antigos de `equipamentos.db` para o Supabase:

```bash
python migrar_para_supabase.py
```

A migração preserva o SQLite, pula duplicidades e informa o resultado final.

## Testes

```bash
python -m unittest -v test_main.py test_app.py test_autenticacao.py
```

A suíte possui 30 testes cobrindo terminal, interface Flask, banco, login, permissões, usuários, histórico, CSV, paginação e QR Code.

## Publicação

O arquivo `render.yaml` prepara a aplicação para o Render. Na plataforma de hospedagem, configure `DATABASE_URL` como variável secreta. `FLASK_SECRET_KEY` é gerada automaticamente pelo Blueprint.

Comando de produção:

```bash
gunicorn --bind 0.0.0.0:$PORT app:app
```

## Estrutura principal

- `app.py`: rotas e interface web
- `autenticacao.py`: usuário autenticado e permissões
- `banco.py`: camada de acesso ao PostgreSQL e SQLite
- `criar_admin.py`: criação segura do primeiro administrador
- `main.py`: versão de terminal preservada
- `migrar_para_supabase.py`: migração do banco local
- `templates/` e `static/`: interface visual
- `test_*.py`: testes automatizados

## Status

Projeto educacional em desenvolvimento contínuo, criado para demonstrar Python, Flask, SQL, segurança web, testes e versionamento profissional com Git e GitHub.
