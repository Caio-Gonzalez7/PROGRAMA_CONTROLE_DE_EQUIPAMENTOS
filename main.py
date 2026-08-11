equipamentos = []

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

            print('\nEquipamento cadastrado!')

    # LISTAR
    elif func == 2:
        if len(equipamentos) == 0:
            print('\nNenhum equipamento cadastrado!')

        else:
            print('\n======= EQUIPAMENTOS CADASTRADOS =======')

            for posicao in range(len(equipamentos)):
                print(f'\nEquipamento {posicao + 1}')
                print(f'Nome: {equipamentos[posicao][0]}')
                print(f'Patrimônio: {equipamentos[posicao][1]}')
                print(f'Serial: {equipamentos[posicao][2]}')

    # PESQUISAR
    elif func == 3:
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

    # REMOVER
    elif func == 4:
        print('\nRemoção ainda não atualizada')

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