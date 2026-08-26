# Controle de Equipamentos

Sistema de linha de comando desenvolvido em Python para cadastrar, consultar e acompanhar equipamentos. O projeto começou com estruturas em memória e evoluiu para persistência em SQLite, migração de dados antigos, backups e testes automatizados.

## Funcionalidades

- Cadastro de equipamentos com nome, patrimônio, número de série, categoria, setor e responsável
- Controle de status: Em uso, Disponível, Em manutenção e Baixado
- Edição e remoção com confirmação
- Validação de campos obrigatórios
- Bloqueio de patrimônios e números de série duplicados
- Pesquisa por patrimônio, serial, nome, categoria, setor, responsável ou status
- Ordenação por nome, patrimônio, categoria ou status
- Registro das datas de cadastro e última atualização
- Resumo por status e categoria
- Exportação dos dados para CSV
- Backup automático do banco antes de editar ou remover registros

## Persistência de dados

Os dados são armazenados localmente em um banco SQLite (`equipamentos.db`).

Caso exista um arquivo `equipamentos.json` de uma versão anterior, o programa realiza a migração automática para o SQLite uma única vez, preservando os dados disponíveis e evitando registros duplicados.

## Tecnologias e conceitos praticados

- Python
- SQLite e SQL
- CRUD
- Persistência e migração de dados
- Manipulação de JSON e CSV
- Funções e modularização
- Dicionários, listas, condições e estruturas de repetição
- Tratamento de exceções
- Validação de entrada e integridade de dados
- Manipulação de arquivos e criação de backups
- Testes automatizados com `unittest` e `unittest.mock`
- Git e GitHub com desenvolvimento por branches

## Estrutura do projeto

- `main.py`: interface de linha de comando e regras da aplicação
- `banco.py`: criação do banco e operações CRUD no SQLite
- `test_main.py`: suíte de testes automatizados
- `.gitignore`: impede o versionamento de bancos, backups e arquivos locais gerados pelo programa

## Como executar

Tenha o Python 3 instalado, clone o repositório e execute:

```bash
git clone https://github.com/Caio-Gonzalez7/PROGRAMA_CONTROLE_DE_EQUIPAMENTOS.git
cd PROGRAMA_CONTROLE_DE_EQUIPAMENTOS
python main.py
```

O banco de dados e as tabelas são criados automaticamente na primeira execução.

## Como executar os testes

```bash
python -m unittest -v
```

A suíte atual possui 11 testes que verificam cadastro, bloqueio de duplicados, pesquisa, edição, remoção, backup, migração do JSON, ordenação, resumo e exportação CSV.

## Próximas melhorias

- Criar uma interface gráfica
- Separar ainda mais as regras de negócio da interface de linha de comando
- Adicionar filtros por período de cadastro e atualização
- Gerar relatórios mais completos

## Status

Projeto educacional em desenvolvimento contínuo, criado para aplicar na prática conceitos de Python, banco de dados, testes e versionamento.
