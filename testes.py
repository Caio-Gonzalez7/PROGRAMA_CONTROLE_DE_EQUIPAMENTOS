import json

ARQUIVO_DADOS = 'equipamentos.json'


def carregar_equipamentos():
    try:
        with open(ARQUIVO_DADOS, 'r', encoding='utf-8') as arquivo:
            return json.load(arquivo)

    except FileNotFoundError:
        return []

    except json.JSONDecodeError:
        print('Erro ao ler o arquivo de dados!')
        return []


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
    print('[0] Sair')

#CADASTRAR
def cadastrar_equipamento():
    novo_equipamento = input('\nEQUIPAMENTO: ').strip()
    novo_patrimonio = input('PATRIMÔNIO: ').strip().upper()
    novo_serial = input('SERIAL: ').strip().upper()

    patrimonio_duplicado = False
    serial_duplicado = False

    for equipamento in equipamentos:
        if novo_patrimonio == equipamento[1]:
            patrimonio_duplicado = True

        if novo_serial == equipamento[2]:
            serial_duplicado = True

    if novo_equipamento == '' or novo_patrimonio == '' or novo_serial == '':
        print('\nTodos os campos devem ser preenchidos!')

    elif patrimonio_duplicado:
        print('\nEsse patrimônio já está cadastrado!')

    elif serial_duplicado:
        print('\nEsse serial já está cadastrado!')

    else:
        equipamentos.append([
            novo_equipamento,
            novo_patrimonio,
            novo_serial
        ])

        salvar_equipamentos()
        print('\nEquipamento cadastrado!')

def listar_equipamentos():
    if len(equipamentos) == 0:
        print('\nNenhum equipamento cadastrado!')

    else:
        print('\n======= EQUIPAMENTOS CADASTRADOS =======')

        for posicao in range(len(equipamentos)):
            print(f'\nEquipamento {posicao + 1}')
            print(f'Nome: {equipamentos[posicao][0]}')
            print(f'Patrimônio: {equipamentos[posicao][1]}')
            print(f'Serial: {equipamentos[posicao][2]}')

def pesquisar_equipamento():
    if len(equipamentos) == 0:
        print('\nNenhum equipamento caadastrado!')
        return

    patrimonio_pesquisado = input(
                '\nDigite o patrimônio que deseja pesquisar: '
            ).strip().upper()
    
    encontrado = False
    
    for equipamento in equipamentos:
            if patrimonio_pesquisado == equipamento[1]:
                    print('\nEquipamento encontrado!')
                    print(f'Nome: {equipamento[0]}')
                    print(f'Patrimônio: {equipamento[1]}')
                    print(f'Serial: {equipamento[2]}')
    
                    encontrado = True
                    break
            if not encontrado:
                print('\nEquipamento não encontrado!')

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
        if len(equipamentos) == 0:
            print('\nNenhum equipamento cadastrado')

        else:
            patrimonio_pesquisado = input(
                '\nDigite o patrimônio do equipamento: '
            ).strip().upper()

            encontrado = False

            for equipamento in equipamentos:
                if patrimonio_pesquisado == equipamento[1]:
                    encontrado = True

                    print('\nEquipamento encontrado!')
                    print(f'Nome: {equipamento[0]}')
                    print(f'Patrimônio: {equipamento[1]}')
                    print(f'Serial: {equipamento[2]}')

                    print('\nDeixe o campo vazio para manter o valor atual.')

                    novo_nome = input(
                        f'Novo nome [{equipamento[0]}]: '
                    ).strip()

                    novo_patrimonio = input(
                        f'Novo patrimônio [{equipamento[1]}]: '
                    ).strip().upper()
    
                    novo_serial = input(
                        f'Novo serial [{equipamento[2]}]: '
                    ).strip().upper()
    
                    if novo_nome == '':
                        novo_nome = equipamento[0]
    
                    if novo_patrimonio == '':
                        novo_patrimonio = equipamento[1]
    
                    if novo_serial == '':
                        novo_serial = equipamento[2]
    
                    patrimonio_duplicado = False
                    serial_duplicado = False
    
                    for outro_equipamento in equipamentos:
                        if outro_equipamento != equipamento:
                            if novo_patrimonio == outro_equipamento[1]:
                                patrimonio_duplicado = True
    
                            if novo_serial == outro_equipamento[2]:
                                serial_duplicado = True
    
                    if patrimonio_duplicado:
                        print('\nEsse patrimônio já está cadastrado!')
    
                    elif serial_duplicado:
                        print('\nEsse serial já está cadastrado!')
    
                    else:
                        print('\n======= NOVOS DADOS =======')
                        print(f'Nome: {novo_nome}')
                        print(f'Patrimônio: {novo_patrimonio}')
                        print(f'Serial: {novo_serial}')
    
                        confirmacao = input(
                            '\nConfirmar alteração? [S/N]: '
                        ).strip().upper()
    
                        if confirmacao == 'S':
                            equipamento[0] = novo_nome
                            equipamento[1] = novo_patrimonio
                            equipamento[2] = novo_serial
    
                            salvar_equipamentos()
    
                            print('\nEquipamento atualizado com sucesso!')
    
                        else:
                            print('\nAlteração cancelada!')
    
                    break
                
            if not encontrado:
                print('\nEquipamento não encontrado!')

    # REMOVER
    elif func == 5:
        if len(equipamentos) == 0:
            print('\nNenhum equipamento cadastrado')

        else:
            patrimonio_remover = input(
                '\nDigite o patrimônio do equipamento: '
            ).strip().upper()

            encontrado = False

            for equipamento in equipamentos:
                if patrimonio_remover == equipamento[1]:
                    encontrado = True

                    print('\nEquipamento encontrado!')
                    print(f'Nome: {equipamento[0]} ')
                    print(f'Patrimônio: {equipamento[1]}')
                    print(f'Serial: {equipamento[2]}')

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

                    break

            if not encontrado:
                print('\nEquipamento não encontrado!')
            
    # RESUMO
    elif func == 6:
        print('\n======= RESUMO =======')
        print(f'Total de equipamentos cadastrados: {len(equipamentos)}')

    # SAIR
    elif func == 0:
        print('\nPrograma finalizado!')
        break

    # OPÇÃO INEXISTENTE
    else:
        print('\nOpção inválida!')