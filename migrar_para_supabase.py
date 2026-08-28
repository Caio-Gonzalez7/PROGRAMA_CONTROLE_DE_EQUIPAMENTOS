from pathlib import Path
import sqlite3

import banco


ARQUIVO_SQLITE = Path('equipamentos.db')
STATUS_VALIDOS = {
    'Em uso',
    'Disponível',
    'Em manutenção',
    'Baixado'
}


def carregar_equipamentos_sqlite():
    conexao = sqlite3.connect(ARQUIVO_SQLITE)
    conexao.row_factory = sqlite3.Row

    try:
        registros = conexao.execute(
            'SELECT * FROM equipamentos ORDER BY id'
        ).fetchall()

    finally:
        conexao.close()

    return [dict(registro) for registro in registros]


def migrar():
    if not banco.usa_postgres():
        print(
            'A conexão do Supabase não foi encontrada. '
            'Confira o DATABASE_URL no arquivo .env.'
        )
        return 1

    if not ARQUIVO_SQLITE.exists():
        print('O arquivo equipamentos.db não foi encontrado.')
        return 1

    try:
        equipamentos_locais = carregar_equipamentos_sqlite()

    except sqlite3.Error as erro:
        print(f'Não foi possível ler o SQLite: {erro}')
        return 1

    banco.criar_tabela()
    equipamentos_online = banco.listar_equipamentos()
    patrimonios = {
        equipamento['patrimonio']
        for equipamento in equipamentos_online
    }
    seriais = {
        equipamento['serial']
        for equipamento in equipamentos_online
    }

    importados = 0
    duplicados = 0
    invalidos = 0

    for equipamento in equipamentos_locais:
        if equipamento.get('status') not in STATUS_VALIDOS:
            invalidos += 1
            print(
                'Ignorado por possuir status inválido: '
                f"{equipamento.get('patrimonio', 'sem patrimônio')}"
            )
            continue

        if (
            equipamento.get('patrimonio') in patrimonios
            or equipamento.get('serial') in seriais
        ):
            duplicados += 1
            continue

        try:
            banco.inserir_equipamento(equipamento)

        except banco.ERROS_INTEGRIDADE:
            duplicados += 1

        else:
            importados += 1
            patrimonios.add(equipamento['patrimonio'])
            seriais.add(equipamento['serial'])

    print('\nMigração concluída!')
    print(f'Importados: {importados}')
    print(f'Já existentes: {duplicados}')
    print(f'Ignorados por dados inválidos: {invalidos}')
    print(f'Total no Supabase: {len(banco.listar_equipamentos())}')
    return 0


if __name__ == '__main__':
    raise SystemExit(migrar())
