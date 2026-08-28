from datetime import datetime
from pathlib import Path
import csv
import json
import shutil

import banco


ARQUIVO_DADOS = 'equipamentos.json'

STATUS_VALIDOS = [
    'Em uso',
    'Disponível',
    'Em manutenção',
    'Baixado'
]


def obter_data_hora():
    return datetime.now().strftime('%d/%m/%Y %H:%M')


def carregar_equipamentos_json():
    try:
        with open(ARQUIVO_DADOS, 'r', encoding='utf-8') as arquivo:
            dados = json.load(arquivo)

    except FileNotFoundError:
        return []

    except json.JSONDecodeError:
        print('\nErro ao ler o arquivo de dados!')
        return []

    if not isinstance(dados, list):
        print('\nFormato inválido no arquivo de dados!')
        return []

    equipamentos_convertidos = []

    for equipamento in dados:
        # Converte registros antigos que utilizavam listas.
        if isinstance(equipamento, list) and len(equipamento) >= 3:
            equipamento_convertido = {
                'nome': equipamento[0],
                'patrimonio': equipamento[1],
                'serial': equipamento[2],
                'categoria': 'Não informado',
                'setor': 'Não informado',
                'responsavel': 'Não informado',
                'status': 'Não informado',
                'data_cadastro': 'Não informado',
                'ultima_atualizacao': 'Não informado'
            }

        # Mantém e completa registros que já utilizam dicionários.
        elif isinstance(equipamento, dict):
            equipamento_convertido = {
                'nome': equipamento.get('nome', ''),
                'patrimonio': equipamento.get('patrimonio', ''),
                'serial': equipamento.get('serial', ''),
                'categoria': equipamento.get(
                    'categoria',
                    'Não informado'
                ),
                'setor': equipamento.get('setor', 'Não informado'),
                'responsavel': equipamento.get(
                    'responsavel',
                    'Não informado'
                ),
                'status': equipamento.get('status', 'Não informado'),
                'data_cadastro': equipamento.get(
                    'data_cadastro',
                    'Não informado'
                ),
                'ultima_atualizacao': equipamento.get(
                    'ultima_atualizacao',
                    'Não informado'
                )
            }

        else:
            continue

        equipamentos_convertidos.append(equipamento_convertido)

    return equipamentos_convertidos


def iniciar_banco():
    banco.criar_tabela()
    caminho_json = Path(ARQUIVO_DADOS)

    if (
        banco.usa_sqlite()
        and caminho_json.exists()
        and not banco.migracao_json_concluida()
    ):
        equipamentos_antigos = carregar_equipamentos_json()
        quantidade_importada = 0

        for equipamento in equipamentos_antigos:
            try:
                banco.inserir_equipamento(equipamento)
                quantidade_importada += 1

            except banco.ERROS_INTEGRIDADE:
                print(
                    '\nUm equipamento duplicado não foi importado: '
                    f"{equipamento['patrimonio']}"
                )

        banco.marcar_migracao_json()

        if quantidade_importada > 0:
            print(
                f'\n{quantidade_importada} equipamento(s) '
                'importado(s) do JSON para o SQLite!'
            )

    return banco.listar_equipamentos()


def criar_backup():
    if banco.usa_postgres():
        return

    caminho_dados = Path(banco.ARQUIVO_BANCO)

    if not caminho_dados.exists():
        return

    caminho_backup = caminho_dados.with_name('equipamentos_backup.db')

    try:
        shutil.copy2(caminho_dados, caminho_backup)
    except OSError as erro:
        print(f'\nAviso: não foi possível criar o backup: {erro}')


def mostrar_menu():
    print('\n======= CONTROLE DE EQUIPAMENTOS =======')
    print('[1] Cadastrar equipamento')
    print('[2] Listar equipamentos')
    print('[3] Pesquisar equipamentos')
    print('[4] Editar equipamento')
    print('[5] Remover equipamento')
    print('[6] Mostrar resumo')
    print('[7] Exportar para CSV')
    print('[0] Sair')


def escolher_status(status_atual=None):
    while True:
        print('\n======= STATUS =======')

        for posicao, status in enumerate(STATUS_VALIDOS, start=1):
            print(f'[{posicao}] {status}')

        if status_atual is not None:
            print(f'[0] Manter status atual: {status_atual}')

        escolha = input('\nEscolha o status: ').strip()

        if status_atual is not None and escolha == '0':
            return status_atual

        if escolha.isnumeric():
            posicao = int(escolha) - 1

            if 0 <= posicao < len(STATUS_VALIDOS):
                return STATUS_VALIDOS[posicao]

        print('\nStatus inválido!')


def exibir_equipamento(equipamento):
    print(f"Nome: {equipamento.get('nome', '')}")
    print(f"Patrimônio: {equipamento.get('patrimonio', '')}")
    print(f"Serial: {equipamento.get('serial', '')}")
    print(
        f"Categoria: "
        f"{equipamento.get('categoria', 'Não informado')}"
    )
    print(f"Setor: {equipamento.get('setor', 'Não informado')}")
    print(
        f"Responsável: "
        f"{equipamento.get('responsavel', 'Não informado')}"
    )
    print(f"Status: {equipamento.get('status', 'Não informado')}")
    print(
        f"Data de cadastro: "
        f"{equipamento.get('data_cadastro', 'Não informado')}"
    )
    print(
        f"Última atualização: "
        f"{equipamento.get('ultima_atualizacao', 'Não informado')}"
    )


def cadastrar_equipamento():
    novo_nome = input('\nEQUIPAMENTO: ').strip()
    novo_patrimonio = input('PATRIMÔNIO: ').strip().upper()
    novo_serial = input('SERIAL: ').strip().upper()
    nova_categoria = input('CATEGORIA: ').strip()
    novo_setor = input('SETOR (opcional): ').strip()
    novo_responsavel = input('RESPONSÁVEL (opcional): ').strip()

    if novo_setor == '':
        novo_setor = 'Não informado'

    if novo_responsavel == '':
        novo_responsavel = 'Não informado'

    if (
        novo_nome == ''
        or novo_patrimonio == ''
        or novo_serial == ''
        or nova_categoria == ''
    ):
        print(
            '\nNome, patrimônio, serial e categoria '
            'são obrigatórios!'
        )
        return

    for equipamento in equipamentos:
        if novo_patrimonio == equipamento['patrimonio']:
            print('\nEsse patrimônio já está cadastrado!')
            return

        if novo_serial == equipamento['serial']:
            print('\nEsse serial já está cadastrado!')
            return

    novo_status = escolher_status()
    data_atual = obter_data_hora()

    novo_equipamento = {
        'nome': novo_nome,
        'patrimonio': novo_patrimonio,
        'serial': novo_serial,
        'categoria': nova_categoria,
        'setor': novo_setor,
        'responsavel': novo_responsavel,
        'status': novo_status,
        'data_cadastro': data_atual,
        'ultima_atualizacao': data_atual
    }

    try:
        novo_id = banco.inserir_equipamento(novo_equipamento)

    except banco.ERROS_INTEGRIDADE:
        print(
            '\nNão foi possível cadastrar. '
            'O patrimônio ou serial já existe!'
        )
        return

    novo_equipamento['id'] = novo_id
    equipamentos.append(novo_equipamento)

    print(
        f'\nEquipamento cadastrado com sucesso! '
        f'ID: {novo_id}'
    )


def listar_equipamentos():
    if len(equipamentos) == 0:
        print('\nNenhum equipamento cadastrado!')
        return

    print('\n======= ORDENAR LISTAGEM POR =======')
    print('[1] Nome')
    print('[2] Patrimônio')
    print('[3] Categoria')
    print('[4] Status')
    print('[0] Ordem de cadastro')

    opcao = input('\nESCOLHA: ').strip()

    campos_ordenacao = {
        '1': 'nome',
        '2': 'patrimonio',
        '3': 'categoria',
        '4': 'status'
    }

    if opcao == '0':
        equipamentos_ordenados = equipamentos.copy()

    elif opcao in campos_ordenacao:
        campo = campos_ordenacao[opcao]
        equipamentos_ordenados = sorted(
            equipamentos,
            key=lambda equipamento: equipamento.get(campo, '').lower()
        )

    else:
        print('\nOpção inválida!')
        return

    print('\n======= EQUIPAMENTOS CADASTRADOS =======')

    for posicao, equipamento in enumerate(
        equipamentos_ordenados,
        start=1
    ):
        print(f'\nEquipamento {posicao}')
        exibir_equipamento(equipamento)


def pesquisar_equipamento():
    if len(equipamentos) == 0:
        print('\nNenhum equipamento cadastrado!')
        return

    print('\n======= PESQUISAR POR =======')
    print('[1] Patrimônio')
    print('[2] Serial')
    print('[3] Nome')
    print('[4] Categoria')
    print('[5] Setor')
    print('[6] Responsável')
    print('[7] Status')
    print('[0] Voltar')

    opcao = input('\nESCOLHA: ').strip()

    campos_pesquisa = {
        '1': ('patrimonio', 'Digite o patrimônio: ', True),
        '2': ('serial', 'Digite o serial: ', True),
        '3': ('nome', 'Digite o nome: ', False),
        '4': ('categoria', 'Digite a categoria: ', False),
        '5': ('setor', 'Digite o setor: ', False),
        '6': ('responsavel', 'Digite o responsável: ', False),
        '7': ('status', 'Digite o status: ', False)
    }

    if opcao == '0':
        return

    if opcao not in campos_pesquisa:
        print('\nOpção inválida!')
        return

    campo, mensagem, pesquisa_exata = campos_pesquisa[opcao]
    termo = input(f'\n{mensagem}').strip()

    if termo == '':
        print('\nA pesquisa não pode ficar vazia!')
        return

    encontrados = []

    for equipamento in equipamentos:
        valor = str(equipamento.get(campo, ''))

        if pesquisa_exata:
            corresponde = termo.upper() == valor.upper()
        else:
            corresponde = termo.lower() in valor.lower()

        if corresponde:
            encontrados.append(equipamento)

    if len(encontrados) == 0:
        print('\nNenhum equipamento encontrado!')
        return

    print(
        f'\n======= {len(encontrados)} '
        f'EQUIPAMENTO(S) ENCONTRADO(S) ======='
    )

    for posicao, equipamento in enumerate(encontrados, start=1):
        print(f'\nResultado {posicao}')
        exibir_equipamento(equipamento)


def editar_equipamento():
    if len(equipamentos) == 0:
        print('\nNenhum equipamento cadastrado!')
        return

    patrimonio_pesquisado = input(
        '\nDigite o patrimônio do equipamento: '
    ).strip().upper()

    for equipamento in equipamentos:
        if patrimonio_pesquisado != equipamento['patrimonio']:
            continue

        print('\nEquipamento encontrado!')
        exibir_equipamento(equipamento)
        print('\nDeixe o campo vazio para manter o valor atual.')

        novo_nome = input(
            f"Novo nome [{equipamento['nome']}]: "
        ).strip()
        novo_patrimonio = input(
            f"Novo patrimônio [{equipamento['patrimonio']}]: "
        ).strip().upper()
        novo_serial = input(
            f"Novo serial [{equipamento['serial']}]: "
        ).strip().upper()
        nova_categoria = input(
            f"Nova categoria [{equipamento['categoria']}]: "
        ).strip()
        novo_setor = input(
            f"Novo setor [{equipamento['setor']}]: "
        ).strip()
        novo_responsavel = input(
            f"Novo responsável [{equipamento['responsavel']}]: "
        ).strip()

        novo_nome = novo_nome or equipamento['nome']
        novo_patrimonio = novo_patrimonio or equipamento['patrimonio']
        novo_serial = novo_serial or equipamento['serial']
        nova_categoria = nova_categoria or equipamento['categoria']
        novo_setor = novo_setor or equipamento['setor']
        novo_responsavel = (
            novo_responsavel or equipamento['responsavel']
        )

        for outro_equipamento in equipamentos:
            if outro_equipamento is equipamento:
                continue

            if novo_patrimonio == outro_equipamento['patrimonio']:
                print('\nEsse patrimônio já está cadastrado!')
                return

            if novo_serial == outro_equipamento['serial']:
                print('\nEsse serial já está cadastrado!')
                return

        novo_status = escolher_status(equipamento['status'])

        print('\n======= NOVOS DADOS =======')
        print(f'Nome: {novo_nome}')
        print(f'Patrimônio: {novo_patrimonio}')
        print(f'Serial: {novo_serial}')
        print(f'Categoria: {nova_categoria}')
        print(f'Setor: {novo_setor}')
        print(f'Responsável: {novo_responsavel}')
        print(f'Status: {novo_status}')

        confirmacao = input(
            '\nConfirmar alteração? [S/N]: '
        ).strip().upper()

        if confirmacao == 'S':
            criar_backup()

            equipamento_atualizado = equipamento.copy()
            equipamento_atualizado.update({
                'nome': novo_nome,
                'patrimonio': novo_patrimonio,
                'serial': novo_serial,
                'categoria': nova_categoria,
                'setor': novo_setor,
                'responsavel': novo_responsavel,
                'status': novo_status,
                'ultima_atualizacao': obter_data_hora()
            })

            try:
                atualizou = banco.atualizar_equipamento(
                    equipamento_atualizado
                )

            except banco.ERROS_INTEGRIDADE:
                print(
                    '\nNão foi possível atualizar. '
                    'O patrimônio ou serial já existe!'
                )
                return

            if atualizou:
                equipamento.update(equipamento_atualizado)
                print('\nEquipamento atualizado com sucesso!')

            else:
                print('\nEquipamento não encontrado no banco!')

        elif confirmacao == 'N':
            print('\nAlteração cancelada!')

        else:
            print('\nOpção inválida. Alteração cancelada!')

        return

    print('\nEquipamento não encontrado!')


def remover_equipamento():
    if len(equipamentos) == 0:
        print('\nNenhum equipamento cadastrado!')
        return

    patrimonio_remover = input(
        '\nDigite o patrimônio do equipamento: '
    ).strip().upper()

    for equipamento in equipamentos:
        if patrimonio_remover != equipamento['patrimonio']:
            continue

        print('\nEquipamento encontrado!')
        exibir_equipamento(equipamento)

        confirmacao = input(
            '\nDeseja realmente remover? [S/N]: '
        ).strip().upper()

        if confirmacao == 'S':
            criar_backup()

            removeu = banco.remover_equipamento(
                equipamento['id']
            )

            if removeu:
                equipamentos.remove(equipamento)
                print('\nEquipamento removido com sucesso!')

            else:
                print('\nEquipamento não encontrado no banco!')

        elif confirmacao == 'N':
            print('\nRemoção cancelada!')

        else:
            print('\nOpção inválida. Remoção cancelada!')

        return

    print('\nEquipamento não encontrado!')


def mostrar_resumo():
    if len(equipamentos) == 0:
        print('\nNenhum equipamento cadastrado!')
        return

    quantidades_status = {}
    quantidades_categoria = {}

    for status in STATUS_VALIDOS:
        quantidades_status[status] = 0

    for equipamento in equipamentos:
        status = equipamento.get('status', 'Não informado')
        categoria = equipamento.get('categoria', 'Não informado')

        quantidades_status[status] = quantidades_status.get(status, 0) + 1
        quantidades_categoria[categoria] = (
            quantidades_categoria.get(categoria, 0) + 1
        )

    print('\n======= RESUMO =======')
    print(f'Total de equipamentos: {len(equipamentos)}')

    print('\nPor status:')
    for status, quantidade in quantidades_status.items():
        print(f'- {status}: {quantidade}')

    print('\nPor categoria:')
    for categoria in sorted(quantidades_categoria, key=str.lower):
        print(f'- {categoria}: {quantidades_categoria[categoria]}')


def exportar_csv():
    if len(equipamentos) == 0:
        print('\nNenhum equipamento cadastrado para exportar!')
        return

    nome_arquivo = 'equipamentos.csv'
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

    try:
        with open(
            nome_arquivo,
            'w',
            newline='',
            encoding='utf-8-sig'
        ) as arquivo:
            escritor = csv.DictWriter(
                arquivo,
                fieldnames=campos,
                delimiter=';',
                extrasaction='ignore'
            )

            escritor.writeheader()

            for equipamento in equipamentos:
                linha = {
                    campo: equipamento.get(campo, 'Não informado')
                    for campo in campos
                }
                escritor.writerow(linha)

    except OSError as erro:
        print(f'\nNão foi possível exportar o CSV: {erro}')
        return

    print(f'\nEquipamentos exportados para {nome_arquivo}!')


equipamentos = []


def executar_programa():
    global equipamentos
    equipamentos = iniciar_banco()

    while True:
        mostrar_menu()
        escolha = input('\nESCOLHA: ').strip()

        if not escolha.isnumeric():
            print('\nDigite apenas números!')
            continue

        func = int(escolha)

        if func == 1:
            cadastrar_equipamento()
        elif func == 2:
            listar_equipamentos()
        elif func == 3:
            pesquisar_equipamento()
        elif func == 4:
            editar_equipamento()
        elif func == 5:
            remover_equipamento()
        elif func == 6:
            mostrar_resumo()
        elif func == 7:
            exportar_csv()
        elif func == 0:
            print('\nPrograma finalizado!')
            break
        else:
            print('\nOpção inválida!')


if __name__ == '__main__':
    executar_programa()
