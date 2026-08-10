equipamentos = []
patrimonios = []
seriais = []

while True:
    print('\n======= CONTROLE DE EQUIPAMENTOS =======')
    print('[1] Cadastrar equipamento')
    print('[2] Listar equipamentos')
    print('[3] Pesquisar equipamento')
    print('[4] Remover equipamento')
    print('[5] Mostrar resumo')
    print('[0] Sair')

    escolha = input('\nESCOLHA: ')

    # Impede que o programa quebre caso seja digitada uma letra
    if not escolha.isnumeric():
        print('\nDigite apenas números!')
        continue

    func = int(escolha)

    # CADASTRAR
    if func == 1:
        novo_equipamento = input('\nEQUIPAMENTO: ').strip()
        novo_patrimonio = input('PATRIMÔNIO: ').strip().upper()
        novo_serial = input('SERIAL: ').strip().upper()

        if novo_patrimonio in patrimonios:
            print('\nEsse patrimônio já está cadastrado!')

        elif novo_serial in seriais:
            print('\nEsse serial já está cadastrado!')

        elif novo_equipamento == '' or novo_patrimonio == '' or novo_serial == '':
            print('\nTodos os campos devem ser preenchidos!')

        else:
            equipamentos.append(novo_equipamento)
            patrimonios.append(novo_patrimonio)
            seriais.append(novo_serial)

            print('\nEquipamento cadastrado!')

    # LISTAR
    elif func == 2:
        if len(equipamentos) == 0:
            print('\nNenhum equipamento cadastrado!')

        else:
            print('\n======= EQUIPAMENTOS CADASTRADOS =======')

            for posicao in range(len(equipamentos)):
                print(f'\nEquipamento {posicao + 1}')
                print(f'Nome: {equipamentos[posicao]}')
                print(f'Patrimônio: {patrimonios[posicao]}')
                print(f'Serial: {seriais[posicao]}')

    # PESQUISAR
    elif func == 3:
        patrimonio_pesquisado = input(
            '\nDigite o patrimônio que deseja pesquisar: '
        ).strip().upper()

        if patrimonio_pesquisado in patrimonios:
            posicao = patrimonios.index(patrimonio_pesquisado)

            print('\nEquipamento encontrado!')
            print(f'Nome: {equipamentos[posicao]}')
            print(f'Patrimônio: {patrimonios[posicao]}')
            print(f'Serial: {seriais[posicao]}')

        else:
            print('\nEquipamento não encontrado!')

    # REMOVER
    elif func == 4:
        patrimonio_remover = input(
            '\nDigite o patrimônio que deseja remover: '
        ).strip().upper()

        if patrimonio_remover in patrimonios:
            posicao = patrimonios.index(patrimonio_remover)

            print('\nEquipamento encontrado!')
            print(f'Nome: {equipamentos[posicao]}')
            print(f'Patrimônio: {patrimonios[posicao]}')
            print(f'Serial: {seriais[posicao]}')

            confirmacao = input(
                '\nDeseja realmente remover? [S/N]: '
            ).strip().upper()

            if confirmacao == 'S':
                equipamentos.pop(posicao)
                patrimonios.pop(posicao)
                seriais.pop(posicao)

                print('\nEquipamento removido!')

            else:
                print('\nRemoção cancelada!')

        else:
            print('\nEquipamento não encontrado!')

    # RESUMO
    elif func == 5:
        print('\n======= RESUMO =======')
        print(f'Total de equipamentos cadastrados: {len(equipamentos)}')

    # SAIR
    elif func == 0:
        print('\nPrograma finalizado!')
        break

    # OPÇÃO INEXISTENTE
    else:
        print('\nOpção inválida!')