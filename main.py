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
                'status': 'Não informado'
            })

        #Mantém registros que já utilizavam dicionários
        elif isinstance(equipamento, dict):
            equipamentos_convertidos.append({
                'nome': equipamento.get('nome', ''),
                'patrimonio': equipamento.get('patrimonio', ''),
                'serial': equipamento.get('serial', ''),
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
    novo_nome = input('\nEQUIPAMENTO: ').strip()
    novo_patrimonio = input('PATRIMÔNIO: ').strip().upper()
    novo_serial = input('SERIAL: ').strip().upper()
    novo_status = escolher_status()

    patrimonio_duplicado = False
    serial_duplicado = False

    for equipamento in equipamentos:
        if novo_patrimonio == equipamento['patrimonio']:
            patrimonio_duplicado = True

        if novo_serial == equipamento['serial']:
            serial_duplicado = True

    if novo_nome == '' or novo_patrimonio == '' or novo_serial == '':
        print('\nTodos os campos devem ser preenchidos!')

    elif patrimonio_duplicado:
        print('\nEsse patrimônio já está cadastrado!')

    elif serial_duplicado:
        print('\nEsse serial já está cadastrado!')

    else:
        novo_equipamento = {
            'nome': novo_nome,
            'patrimonio': novo_patrimonio,
            'serial': novo_serial,
            'status': novo_status
        }

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
            print(f"Status: {equipamento['status']}")

def pesquisar_equipamento():
    if len(equipamentos) == 0:
        print('\nNenhum equipamento caadastrado!')
        return

    patrimonio_pesquisado = input(
        '\nDigite o patrimônio que deseja pesquisar: '
    ).strip().upper()
    
    for equipamento in equipamentos:
        if patrimonio_pesquisado == equipamento['patrimonio']:
            print('\nEquipamento encontrado!')
            print(f'Nome: {equipamento['nome']}')
            print(f'Patrimônio: {equipamento['patrimonio']}')
            print(f'Serial: {equipamento['serial']}')
            print(f"Status: {equipamento['status']}")
            return

    print('\nEquipamento não encontrado!')

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
            print(f"Nome: {equipamento['nome']}")
            print(f"Patrimônio: {equipamento['patrimonio']}")
            print(f"Serial: {equipamento['serial']}")
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

            if novo_nome == '':
                novo_nome = equipamento['nome']

            if novo_patrimonio == '':
                novo_patrimonio = equipamento['patrimonio']

            if novo_serial == '':
                novo_serial = equipamento['serial']

            novo_status = escolher_status(equipamento['status'])

            patrimonio_duplicado = False
            serial_duplicado = False

            for outro_equipamento in equipamentos:
                if outro_equipamento != equipamento:
                    if novo_patrimonio == outro_equipamento['patrimonio']:
                        patrimonio_duplicado = True

                    if novo_serial == outro_equipamento['serial']:
                        serial_duplicado = True

            if patrimonio_duplicado:
                print('\nEsse patrimônio já está cadastrado!')
                return

            if serial_duplicado:
                print('\nEsse serial já está cadastrado!')
                return

            print('\n======= NOVOS DADOS =======')
            print(f'Nome: {novo_nome}')
            print(f'Patrimônio: {novo_patrimonio}')
            print(f'Serial: {novo_serial}')
            print(f'Status: {novo_status}')

            confirmacao = input(
                '\nConfirmar alteração? [S/N]: '
            ).strip().upper()

            if confirmacao == 'S':
                equipamento['nome'] = novo_nome
                equipamento['patrimonio'] = novo_patrimonio
                equipamento['serial'] = novo_serial
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
        campos = ['nome', 'patrimonio', 'serial', 'status']

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