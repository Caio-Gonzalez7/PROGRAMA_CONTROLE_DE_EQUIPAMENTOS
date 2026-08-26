import sqlite3


ARQUIVO_BANCO = 'equipamentos.db'


def conectar():
    conexao = sqlite3.connect(ARQUIVO_BANCO)
    conexao.row_factory = sqlite3.Row
    return conexao


def criar_tabela():
    with conectar() as conexao:
        conexao.execute(
            '''
            CREATE TABLE IF NOT EXISTS equipamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                patrimonio TEXT NOT NULL UNIQUE,
                serial TEXT NOT NULL UNIQUE,
                categoria TEXT NOT NULL,
                setor TEXT NOT NULL,
                responsavel TEXT NOT NULL,
                status TEXT NOT NULL,
                data_cadastro TEXT NOT NULL,
                ultima_atualizacao TEXT NOT NULL
            )
            '''
        )


def inserir_equipamento(equipamento):
    with conectar() as conexao:
        cursor = conexao.execute(
            '''
            INSERT INTO equipamentos (
                nome,
                patrimonio,
                serial,
                categoria,
                setor,
                responsavel,
                status,
                data_cadastro,
                ultima_atualizacao
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                equipamento['nome'],
                equipamento['patrimonio'],
                equipamento['serial'],
                equipamento['categoria'],
                equipamento['setor'],
                equipamento['responsavel'],
                equipamento['status'],
                equipamento['data_cadastro'],
                equipamento['ultima_atualizacao']
            )
        )

        return cursor.lastrowid


def listar_equipamentos():
    with conectar() as conexao:
        resultados = conexao.execute(
            '''
            SELECT *
            FROM equipamentos
            ORDER BY id
            '''
        ).fetchall()

    return [
        dict(equipamento)
        for equipamento in resultados
    ]


def atualizar_equipamento(equipamento):
    with conectar() as conexao:
        cursor = conexao.execute(
            '''
            UPDATE equipamentos
            SET
                nome = ?,
                patrimonio = ?,
                serial = ?,
                categoria = ?,
                setor = ?,
                responsavel = ?,
                status = ?,
                data_cadastro = ?,
                ultima_atualizacao = ?
            WHERE id = ?
            ''',
            (
                equipamento['nome'],
                equipamento['patrimonio'],
                equipamento['serial'],
                equipamento['categoria'],
                equipamento['setor'],
                equipamento['responsavel'],
                equipamento['status'],
                equipamento['data_cadastro'],
                equipamento['ultima_atualizacao'],
                equipamento['id']
            )
        )

    return cursor.rowcount > 0


def remover_equipamento(equipamento_id):
    with conectar() as conexao:
        cursor = conexao.execute(
            '''
            DELETE FROM equipamentos
            WHERE id = ?
            ''',
            (equipamento_id,)
        )

    return cursor.rowcount > 0
