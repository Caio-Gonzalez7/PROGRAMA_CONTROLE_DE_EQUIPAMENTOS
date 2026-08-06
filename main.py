equipamentos = []
patrimonios = []
sereais = []

while True:
    print('======= CONTROLE DE EQUIPAMENTOS =======')

    print('[1] Cadastrar equipamentos')
    print('[2] Listar equipamentos')
    print('[3] Pesquisar equipamentos')
    print('[4] Verificar duplicados')
    print('[5] Remover equipamentos')
    print('[6] Mostrar resumo')
    print('[0] Sair')

    func = int(input('\nESCOLHA: '))

    if func == 1:
        equipamentos.append(str(input('\nEQUIPAMENTO: ')))
        patrimonios.append(input('PATRIMÔNIO: '))
        sereais.append(input('SERIAL: '))

    if func == 2:
        for p in range(len(equipamentos)):
            print(equipamentos[p])

    if func == 3:
        pesq = input('Digite o patrimônio do equipamento que deseja pesquisar: ')
        for pesq in patrimonios:
            if pesq in patrimonios:
                print('Equipamento encontrado!')
            else:
                print('Equipamento não encontrado!')


    if func == 0:
        print('PROGRAMA FINALIZADO!!!')
        break