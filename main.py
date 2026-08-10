from collections import Counter


OPCOES_VALIDAS = {0, 1, 2, 3, 4, 5, 6}


def normalizar(valor):
    """Remove espaços e diferenças entre letras maiúsculas e minúsculas."""
    return valor.strip().casefold()


def buscar_por_patrimonio(equipamentos, patrimonio):
    """Retorna o equipamento com o patrimônio informado ou None."""
    patrimonio_normalizado = normalizar(patrimonio)
    for equipamento in equipamentos:
        if normalizar(equipamento["patrimonio"]) == patrimonio_normalizado:
            return equipamento
    return None


def encontrar_duplicados(equipamentos, campo):
    """Retorna os valores repetidos de um campo."""
    contagem = Counter(
        normalizar(equipamento[campo])
        for equipamento in equipamentos
        if equipamento[campo].strip()
    )
    return sorted(valor for valor, quantidade in contagem.items() if quantidade > 1)


def resumir_por_tipo(equipamentos):
    """Conta quantos equipamentos existem de cada tipo."""
    return dict(Counter(equipamento["tipo"] for equipamento in equipamentos))


def ler_opcao():
    while True:
        try:
            opcao = int(input("\nEscolha uma opção: "))
        except ValueError:
            print("Digite apenas o número da opção.")
            continue

        if opcao in OPCOES_VALIDAS:
            return opcao
        print("Opção inválida. Escolha um número entre 0 e 6.")


def cadastrar_equipamento(equipamentos):
    print("\n--- Cadastro de equipamento ---")
    tipo = input("Tipo do equipamento: ").strip()
    patrimonio = input("Patrimônio: ").strip()
    serial = input("Serial: ").strip()

    if not tipo or not patrimonio or not serial:
        print("Todos os campos são obrigatórios.")
        return

    if buscar_por_patrimonio(equipamentos, patrimonio):
        print("Já existe um equipamento com esse patrimônio.")
        return

    if any(normalizar(item["serial"]) == normalizar(serial) for item in equipamentos):
        print("Já existe um equipamento com esse serial.")
        return

    equipamentos.append(
        {"tipo": tipo.title(), "patrimonio": patrimonio, "serial": serial}
    )
    print("Equipamento cadastrado com sucesso!")


def listar_equipamentos(equipamentos):
    if not equipamentos:
        print("\nNenhum equipamento cadastrado.")
        return

    print("\n--- Equipamentos cadastrados ---")
    for indice, equipamento in enumerate(equipamentos, start=1):
        print(
            f'{indice}. {equipamento["tipo"]} | '
            f'Patrimônio: {equipamento["patrimonio"]} | '
            f'Serial: {equipamento["serial"]}'
        )


def pesquisar_equipamento(equipamentos):
    patrimonio = input("\nPatrimônio que deseja pesquisar: ")
    equipamento = buscar_por_patrimonio(equipamentos, patrimonio)

    if equipamento is None:
        print("Equipamento não encontrado.")
        return

    print(
        f'Encontrado: {equipamento["tipo"]} | '
        f'Patrimônio: {equipamento["patrimonio"]} | '
        f'Serial: {equipamento["serial"]}'
    )


def verificar_duplicados(equipamentos):
    patrimonios = encontrar_duplicados(equipamentos, "patrimonio")
    seriais = encontrar_duplicados(equipamentos, "serial")

    if not patrimonios and not seriais:
        print("\nNenhum patrimônio ou serial duplicado.")
        return

    if patrimonios:
        print(f'Patrimônios duplicados: {", ".join(patrimonios)}')
    if seriais:
        print(f'Seriais duplicados: {", ".join(seriais)}')


def remover_equipamento(equipamentos):
    patrimonio = input("\nPatrimônio do equipamento que deseja remover: ")
    equipamento = buscar_por_patrimonio(equipamentos, patrimonio)

    if equipamento is None:
        print("Equipamento não encontrado.")
        return

    confirmacao = input(
        f'Remover {equipamento["tipo"]} de patrimônio '
        f'{equipamento["patrimonio"]}? [S/N] '
    ).strip().casefold()

    if confirmacao == "s":
        equipamentos.remove(equipamento)
        print("Equipamento removido com sucesso!")
    else:
        print("Remoção cancelada.")


def mostrar_resumo(equipamentos):
    print(f"\nTotal de equipamentos: {len(equipamentos)}")
    for tipo, quantidade in sorted(resumir_por_tipo(equipamentos).items()):
        print(f"- {tipo}: {quantidade}")


def exibir_menu():
    print("\n======= CONTROLE DE EQUIPAMENTOS =======")
    print("[1] Cadastrar equipamento")
    print("[2] Listar equipamentos")
    print("[3] Pesquisar equipamento")
    print("[4] Verificar duplicados")
    print("[5] Remover equipamento")
    print("[6] Mostrar resumo")
    print("[0] Sair")


def main():
    equipamentos = []

    while True:
        exibir_menu()
        opcao = ler_opcao()

        if opcao == 1:
            cadastrar_equipamento(equipamentos)
        elif opcao == 2:
            listar_equipamentos(equipamentos)
        elif opcao == 3:
            pesquisar_equipamento(equipamentos)
        elif opcao == 4:
            verificar_duplicados(equipamentos)
        elif opcao == 5:
            remover_equipamento(equipamentos)
        elif opcao == 6:
            mostrar_resumo(equipamentos)
        else:
            print("Programa finalizado!")
            break


if __name__ == "__main__":
    main()

