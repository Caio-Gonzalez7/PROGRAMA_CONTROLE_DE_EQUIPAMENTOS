import json
import csv

ARQUIVO_DADOS = 'equipamentos.json'

STATUS_VALIDOS = [
    'Em uso',
    'Disponível',
    'Em manutenção',
    'Baixado'
]

def carregar_equipamentos():
    try:
        with open(ARQUIVO_DADOS, 'r', encoding='utf-8') as arquivo:
            dados = json.load(arquivo)

    except FileNotFoundError:
        return []

    except json.JSONDecodeError:
        print('Erro ao ler o arquivo de dados!')
        return []

    equipamentos_convertidos = []

    for equipamento in dados:
        #Converte registros antigos que utilazavam listas
        if isinstance(equipamento, list) and len(equipamento) >= 3:
            equipamentos_convertidos.append({
                'nome': equipamento[0],
                'patrimonio': equipamento[1],
                'serial': equipamento[2],
                'categoria': 'Não informado',
                'setor': 'Não informado',
                'responsavel': 'Não informado',
                'status': 'Não informado'
            })

        #Mantém registros que já utilizavam dicionários
        elif isinstance(equipamento, dict):
            equipamentos_convertidos.append({
                'nome': equipamento.get('nome', ''),
                'patrimonio': equipamento.get('patrimonio', ''),
                'serial': equipamento.get('serial', ''),
                'categoria': equipamento.get('categoria', 'Não informado'),
                'setor': equipamento.get('setor', 'Não informado'),
                'responsavel': equipamento.get(
                    'responsavel',
                    'Não informado'
                ),
                'status': equipamento.get('status', 'Não informado')
            })

    return equipamentos_convertidos

def salvar_equipamentos():
    with open(ARQUIVO_DADOS, 'w', encoding='utf-8') as arquivo:
        json.dump(
            equipamentos,
            arquivo,
            ensure_ascii=False,
            indent=4
        )
#MENU
def mostrar_menu():
    print('\n======= CONTROLE DE EQUIPAMENTOS =======')
    print('[1] Cadastrar equipamentos')
    print('[2] Listar equipamentos')
    print('[3] Pesquisar equipamentos')
    print('[4] Editar equipamentos')
    print('[5] Remover equipamentos')
    print('[6] Mostrar resumo')
    print('[7] Exportar para CSV')
    print('[0] Sair')

#CADASTRAR
def cadastrar_equipamento():
    # 1. Receber os dados
    novo_nome = input('\nEQUIPAMENTO: ').strip()
    novo_patrimonio = input('PATRIMÔNIO: ').strip().upper()
    novo_serial = input('SERIAL: ').strip().upper()
    nova_categoria = input('CATEGORIA: ').strip()
    novo_setor = input('SETOR (opcional): ').strip()
    novo_responsavel = input('RESPONSÁVEL (opcional): ').strip()

    # 2. Preencher os campos opcionais
    if novo_setor == '':
        novo_setor = 'Não informado'

    if novo_responsavel == '':
        novo_responsavel = 'Não informado'

    # 3. Validar os campos obrigatórios
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

    # 4. Verificar duplicidades
    for equipamento in equipamentos:
        if novo_patrimonio == equipamento['patrimonio']:
            print('\nEsse patrimônio já está cadastrado!')
            return

        if novo_serial == equipamento['serial']:
            print('\nEsse serial já está cadastrado!')
            return

    # 5. Escolher o status somente após validar os dados
    novo_status = escolher_status()

    # 6. Criar o dicionário
    novo_equipamento = {
        'nome': novo_nome,
        'patrimonio': novo_patrimonio,
        'serial': novo_serial,
        'categoria': nova_categoria,
        'setor': novo_setor,
        'responsavel': novo_responsavel,
        'status': novo_status
    }

    # 7. Salvar
    equipamentos.append(novo_equipamento)
    salvar_equipamentos()

    print('\nEquipamento cadastrado!')

def listar_equipamentos():
    if len(equipamentos) == 0:
        print('\nNenhum equipamento cadastrado!')

    else:
        print('\n======= EQUIPAMENTOS CADASTRADOS =======')

        for posicao in range(len(equipamentos)):
            equipamento = equipamentos[posicao]

            print(f'\nEquipamento {posicao + 1}')
            print(f"Nome: {equipamento['nome']}")
            print(f"Patrimônio: {equipamento['patrimonio']}")
            print(f"Serial: {equipamento['serial']}")
            print(f"Categoria: {equipamento['categoria']}")
            print(f"Setor: {equipamento['setor']}")
            print(f"Responsável: {equipamento['responsavel']}")
            print(f"Status: {equipamento['status']}")


def exibir_equipamento(equipamento):
    print(f"Nome: {equipamento['nome']}")
    print(f"Patrimônio: {equipamento['patrimonio']}")
    print(f"Serial: {equipamento['serial']}")
    print(f"Categoria: {equipamento['categoria']}")
    print(f"Setor: {equipamento['setor']}")
    print(f"Responsável: {equipamento['responsavel']}")
    print(f"Status: {equipamento['status']}")


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
    print('[0] Voltar')

    opcao = input('\nESCOLHA: ').strip()

    pesquisa_exata = False

    if opcao == '1':
        campo = 'patrimonio'
        termo = input('\nDigite o patrimônio: ').strip().upper()
        pesquisa_exata = True

    elif opcao == '2':
        campo = 'serial'
        termo = input('\nDigite o serial: ').strip().upper()
        pesquisa_exata = True

    elif opcao == '3':
        campo = 'nome'
        termo = input('\nDigite o nome: ').strip().lower()

    elif opcao == '4':
        campo = 'categoria'
        termo = input('\nDigite a categoria: ').strip().lower()

    elif opcao == '5':
        campo = 'setor'
        termo = input('\nDigite o setor: ').strip().lower()

    elif opcao == '6':
        campo = 'responsavel'
        termo = input('\nDigite o responsável: ').strip().lower()

    elif opcao == '0':
        return

    else:
        print('\nOpção inválida!')
        return

    if termo == '':
        print('\nA pesquisa não pode ficar vazia!')
        return

    encontrados = []

    for equipamento in equipamentos:
        valor = equipamento.get(campo, '')

        if pesquisa_exata:
            if termo == valor.upper():
                encontrados.append(equipamento)

        else:
            if termo in valor.lower():
                encontrados.append(equipamento)

    if len(encontrados) == 0:
        print('\nNenhum equipamento encontrado!')
        return

    print(
        f'\n======= {len(encontrados)} '
        f'EQUIPAMENTO(S) ENCONTRADO(S) ======='
    )

    for posicao in range(len(encontrados)):
        print(f'\nResultado {posicao + 1}')
        exibir_equipamento(encontrados[posicao])

#EDITAR
def editar_equipamento():
    if len(equipamentos) == 0:
        print('\nNenhum equipamento cadastrado!')
        return

    patrimonio_pesquisado = input(
        '\nDigite o patrimônio do equipamento: '
    ).strip().upper()

    for equipamento in equipamentos:
        if patrimonio_pesquisado == equipamento['patrimonio']:
            print('\nEquipamento encontrado!')
            print(f"Nome: {equipamento['nome']}")
            print(f"Patrimônio: {equipamento['patrimonio']}")
            print(f"Serial: {equipamento['serial']}")
            print(f"Categoria: {equipamento['categoria']}")
            print(f"Setor: {equipamento['setor']}")
            print(f"Responsável: {equipamento['responsavel']}")
            print(f"Status: {equipamento['status']}")

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

            if novo_nome == '':
                novo_nome = equipamento['nome']

            if novo_patrimonio == '':
                novo_patrimonio = equipamento['patrimonio']

            if novo_serial == '':
                novo_serial = equipamento['serial']

            if nova_categoria == '':
                nova_categoria = equipamento['categoria']

            if novo_setor == '':
                novo_setor = equipamento['setor']

            if novo_responsavel == '':
                novo_responsavel = equipamento['responsavel']

            # Verificar duplicidades em outros equipamentos
            for outro_equipamento in equipamentos:
                if outro_equipamento != equipamento:
                    if (
                        novo_patrimonio
                        == outro_equipamento['patrimonio']
                    ):
                        print(
                            '\nEsse patrimônio já está cadastrado!'
                        )
                        return

                    if novo_serial == outro_equipamento['serial']:
                        print('\nEsse serial já está cadastrado!')
                        return

            novo_status = escolher_status(
                equipamento['status']
            )

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
                equipamento['nome'] = novo_nome
                equipamento['patrimonio'] = novo_patrimonio
                equipamento['serial'] = novo_serial
                equipamento['categoria'] = nova_categoria
                equipamento['setor'] = novo_setor
                equipamento['responsavel'] = novo_responsavel
                equipamento['status'] = novo_status

                salvar_equipamentos()
                print('\nEquipamento atualizado com sucesso!')

            elif confirmacao == 'N':
                print('\nAlteração cancelada!')

            else:
                print('\nOpção inválida. Alteração cancelada!')

            return

    print('\nEquipamento não encontrado!')

#REMOVER
def remover_equipamento():
    if len(equipamentos) == 0:
        print('\nNenhum equipamento cadastrado!')
        return

    patrimonio_remover = input(
        '\nDigite o patrimônio do equipamento: '
    ).strip().upper()

    for equipamento in equipamentos:
        if patrimonio_remover == equipamento['patrimonio']:
            print('\nEquipamento encontrado!')
            print(f"Nome: {equipamento['nome']}")
            print(f"Patrimônio: {equipamento['patrimonio']}")
            print(f"Serial: {equipamento['serial']}")
            print(f"Categoria: {equipamento['categoria']}")
            print(f"Setor: {equipamento['setor']}")
            print(f"Responsável: {equipamento['responsavel']}")
            print(f"Status: {equipamento['status']}")

            confirmacao = input(
                '\nDeseja realmente remover? [S/N]: '
            ).strip().upper()

            if confirmacao == 'S':
                equipamentos.remove(equipamento)
                salvar_equipamentos()

                print('\nEquipamento removido com sucesso!')

            elif confirmacao == 'N':
                print('\nRemoção cancelada!')

            else:
                print('\nOpção inválida. Remoção cancelada!')

            return

    print('\nEquipamento não encontrado!')


def mostrar_resumo():
    quantidades = {}

    for status in STATUS_VALIDOS:
        quantidades[status] = 0

    quantidades['Não informado'] = 0

    for equipamento in equipamentos:
        status = equipamento.get('status', 'Não informado')

        if status not in quantidades:
            quantidades[status] = 0

        quantidades[status] += 1

    print('\n======= RESUMO =======')
    print(f'Total de equipamentos: {len(equipamentos)}')

    for status in quantidades:
        print(f'{status}: {quantidades[status]}')


def exportar_csv():
    if len(equipamentos) == 0:
        print('\nNenhum equipamento cadastrado para exportar!')
        return

    nome_arquivo = 'equipamentos.csv'

    with open(
        nome_arquivo,
        'w',
        newline='',
        encoding='utf-8-sig'
    ) as arquivo:
        campos = [
            'nome',
            'patrimonio',
            'serial',
            'categoria',
            'setor',
            'responsavel',
            'status'
                ]

        escritor = csv.DictWriter(
            arquivo,
            fieldnames=campos,
            delimiter=';'
        )

        escritor.writeheader()
        escritor.writerows(equipamentos)

    print(f'\nEquipamentos exportados para {nome_arquivo}!')


def escolher_status(status_atual=None):
    while True:
        print('\n======= STATUS =======')

        for posicao in range(len(STATUS_VALIDOS)):
            print(f'[{posicao + 1}] {STATUS_VALIDOS[posicao]}')

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


equipamentos = carregar_equipamentos()

while True:
    mostrar_menu()

    escolha = input('\nESCOLHA: ')

    # Impede que o programa quebre caso seja digitada uma letra
    if not escolha.isnumeric():
        print('\nDigite apenas números!')
        continue

    func = int(escolha)

    # CADASTRAR
    if func == 1:
        cadastrar_equipamento()

    # LISTAR
    elif func == 2:
        listar_equipamentos()

    # PESQUISAR
    elif func == 3:
        pesquisar_equipamento()

    #EDITAR
    elif func == 4:
        editar_equipamento()

    # REMOVER
    elif func == 5:
        remover_equipamento()

    # RESUMO
    elif func == 6:
        mostrar_resumo()

    #EXPORTAR
    elif func == 7:
        exportar_csv()

    # SAIR
    elif func == 0:
        print('\nPrograma finalizado!')
        break

    # OPÇÃO INEXISTENTE
    else:
        print('\nOpção inválida!')