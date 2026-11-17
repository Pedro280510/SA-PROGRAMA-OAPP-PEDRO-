import os
import time
import json
from datetime import datetime

os.system("cls")


def ler_numero(mensagem):
    while True:
        try:
            numero = int(input(mensagem))
            return numero
        except ValueError:
            print("Invalido! DIGITE APENAS NUMEROS")


def ler_decimal(mensagem):
    while True:
        try:
            valor = input(mensagem).strip().replace(",", ".")
            return float(valor)
        except ValueError:
            print("Inválido! Digite um valor numérico (ex: 45,50 ou 45.50)")


class Ingrediente:
    def __init__(self, nome, estoque):
        self.nome = nome
        self.estoque = estoque

    def to_dict(self):
        return {"Item": self.nome, "Estoque": [self.estoque]}

    @classmethod
    def from_dict(cls, dados):
        return cls(dados["Item"], dados["Estoque"][0])


class Chocolate:
    def __init__(self, nome, preco, prontos=0, vendidos=0, receita=None):
        self.nome = nome
        self.preco = preco
        self.prontos = prontos
        self.vendidos = vendidos
        self.receita = receita if receita is not None else {}

    def to_dict(self):
        return {
            "Nome": self.nome,
            "Receita": self.receita,
            "Prontos": [self.prontos],
            "Preco": [self.preco],
            "Vendidos": [self.vendidos]
        }

    @classmethod
    def from_dict(cls, dados):
        receita = {int(ik): iv for ik, iv in dados.get("Receita", {}).items()}
        return cls(
            nome=dados["Nome"],
            preco=dados["Preco"][0],
            prontos=dados["Prontos"][0],
            vendidos=dados["Vendidos"][0],
            receita=receita
        )


class Cliente:
    def __init__(self, nome, compras=0):
        self.nome = nome
        self.compras = compras

    def registrar_compra(self):
        self.compras += 1
        return self.compras

    def to_dict(self):
        return {"Nome": self.nome, "Compras": self.compras}

    @classmethod
    def from_dict(cls, dados):
        return cls(dados["Nome"], dados["Compras"])


class FabricaERP:
    def __init__(self):
        self.ingredientes = {
            1: Ingrediente("Massa de Cacau (Kg)", 50),
            2: Ingrediente("Leite em Pó (Kg)", 50),
            3: Ingrediente("Açucar (Kg)", 50),
            4: Ingrediente("Avelã (Kg)", 50)
        }

        self.chocolates = {
            1: Chocolate("Barra ao Leite", 45.00, prontos=5, receita={1: 2, 2: 2, 3: 2}),
            2: Chocolate("Barra Amargo 70%", 55.00, prontos=3, receita={1: 4, 3: 1}),
            3: Chocolate("BomBom de Avelã", 70.00, prontos=2, receita={1: 2, 2: 1, 3: 2, 4: 2}),
            4: Chocolate("Barra de Chocolate Branco", 50.00, prontos=0, receita={2: 3, 3: 2}),
            5: Chocolate("Barra Crocante com Avelã", 60.00, prontos=4, receita={1: 3, 2: 1, 3: 1, 4: 1})
        }

        self.historico_producao = []
        self.caixa_vendas = 0.0
        self.despesas_compras = 0.0
        self.clientes = {}

    def mostrar_ingredientes(self):
        print("======== ESTOQUE DE INGREDIENTE =======")
        for id_ingrediente, ing in self.ingredientes.items():
            alerta = "  <-- [!] ESTOQUE BAIXO - REPOR!" if ing.estoque <= 10 else ""
            print(f"{id_ingrediente}.{ing.nome} - Estoque {ing.estoque} Kg{alerta}")
            time.sleep(0.1)

    def mostrar_chocolates(self):
        print("======== ESTOQUE DE CHOCOLATE =======")
        for id_chocolate, choc in self.chocolates.items():
            print(f"{id_chocolate}. {choc.nome} - Prontos: {choc.prontos} cx | Preço: R$ {choc.preco:.2f}")

    def comprar_ingredientes(self):
        self.mostrar_ingredientes()
        escolha = ler_numero("Qual Ingrediente Chegou? ")
        if escolha == 0:
            return
        if escolha not in self.ingredientes:
            print("Ingrediente não encontrado!")
            return

        quantidade = ler_numero("Quantos Quilos Chegaram? ")
        if quantidade <= 0:
            print("Quantidade inválida!")
            return

        custo = ler_decimal("Qual foi o valor total pago (R$)? ")
        if custo < 0:
            print("Valor inválido!")
            return

        self.ingredientes[escolha].estoque += quantidade
        self.despesas_compras += custo
        print("Estoque Atualizado com Sucesso!")

    def produzir_chocolate(self):
        self.mostrar_chocolates()
        escolha = ler_numero("\nQual Chocolate deseja Produzir? ")
        if escolha == 0:
            return
        if escolha not in self.chocolates:
            print("Chocolate inválido!")
            return
        lotes = ler_numero("Quantas caixas vai produzir? ")
        if lotes <= 0:
            print("Quantidade inválida!")
            return

        choc = self.chocolates[escolha]

        for id_ing, qtd_por_caixa in choc.receita.items():
            if self.ingredientes[id_ing].estoque < qtd_por_caixa * lotes:
                print(f"Falta {self.ingredientes[id_ing].nome} no estoque!")
                return

        for id_ing, qtd_por_caixa in choc.receita.items():
            self.ingredientes[id_ing].estoque -= qtd_por_caixa * lotes

        choc.prontos += lotes
        agora = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.historico_producao.append(f"[{agora}] {lotes}x {choc.nome}")
        print("Produção concluída com sucesso!")

    def vender_chocolates(self):
        carrinho = {}

        while True:
            self.mostrar_chocolates()
            if carrinho:
                print("\n--- Carrinho Atual ---")
                for id_item, qtd_item in carrinho.items():
                    print(f"- {qtd_item}x {self.chocolates[id_item].nome}")

            entrada = input("\nEscolha o chocolate (ou 0 / ENTER para finalizar): ").strip()

            if entrada == "" or entrada == "0":
                break

            if not entrada.isdigit():
                print("Inválido! Digite o número do chocolate ou 0 para finalizar.")
                continue

            escolha = int(entrada)
            if escolha not in self.chocolates:
                print("Chocolate inválido!")
                continue

            quantidade = ler_numero("Quantas caixas deseja? ")
            if quantidade <= 0:
                print("Quantidade inválida!")
                continue

            choc = self.chocolates[escolha]
            ja_no_carrinho = carrinho.get(escolha, 0)
            if choc.prontos < (ja_no_carrinho + quantidade):
                print(f"Estoque insuficiente! Disponível: {choc.prontos - ja_no_carrinho} cx.")
                continue

            carrinho[escolha] = ja_no_carrinho + quantidade
            print(f"{quantidade}x {choc.nome} adicionado ao carrinho!")

        if not carrinho:
            return

        cpf = input("\nCPF ou Telefone do cliente (ou ENTER para pular): ").strip()  # .strip ele reconhece que não tem nada deixa em vazio e vai para o proximo
        nome_cliente = "Cliente Balcão"
        ganhou_brinde = False

        if cpf != "":
            if cpf not in self.clientes:  # Guarda os clientes cadastrados no programa de fidelidade (pelo CPF ou telefone)
                nome_cliente = input("Digite seu nome: ").strip() or "Cliente"
                self.clientes[cpf] = Cliente(nome_cliente)
            else:
                nome_cliente = self.clientes[cpf].nome

            total_compras = self.clientes[cpf].registrar_compra()
            print(f"Cliente: {nome_cliente} | Compra nº {total_compras} no Cartão Fidelidade")

            if total_compras % 5 == 0:
                for id_item in carrinho:
                    if self.chocolates[id_item].prontos >= (carrinho[id_item] + 1):
                        self.chocolates[id_item].prontos -= 1
                        ganhou_brinde = True
                        print(f"PARABÉNS! 5ª compra atingida: +1 caixa GRÁTIS de {self.chocolates[id_item].nome}!")
                        break

        total = 0.0
        total_caixas = 0
        for id_item, qtd_item in carrinho.items():
            choc = self.chocolates[id_item]
            choc.prontos -= qtd_item
            choc.vendidos += qtd_item
            total += choc.preco * qtd_item
            total_caixas += qtd_item

        if total_caixas >= 5:
            desconto = total * 0.10
            total -= desconto
            print(f"Desconto de atacado ({total_caixas} caixas - 10%): -R$ {desconto:.2f}")

        self.caixa_vendas += total
        print(f"Venda concluída para {nome_cliente}! Total: R$ {total:.2f}")
        if ganhou_brinde:
            print("(Brinde fidelidade já descontado do estoque!)")

    def ver_relatorio(self):
        lucro = self.caixa_vendas - self.despesas_compras
        print("\n======== RELATÓRIO DA FÁBRICA ========")
        print(f"Receita Bruta (Vendas):   R$ {self.caixa_vendas:.2f}")
        print(f"Despesas (Compras):       R$ {self.despesas_compras:.2f}")
        print(f"Lucro Líquido:            R$ {lucro:.2f}")
        print("\n--- Histórico de Produção ---")
        if len(self.historico_producao) == 0:
            print("Nenhuma produção registrada ainda.")
        else:
            for registro in self.historico_producao:
                print(registro)
        # Percorre os chocolates para descobrir qual teve mais caixas vendidas
        campeao_nome = "Nenhuma Venda Ainda!"
        maior_venda = 0
        for choc in self.chocolates.values():
            if choc.vendidos > maior_venda:
                maior_venda = choc.vendidos
                campeao_nome = choc.nome
        print(f"Campeão de Vendas: {campeao_nome} ({maior_venda} caixas)")

    def cadastrar_ingrediente(self):
        print("\n======== CADASTRAR NOVO INGREDIENTE ========")
        nome = input("Nome do Ingrediente: ").strip()
        if nome == "":
            print("Nome Invalido!")
            return
        estoque_inicial = ler_numero("Quantidade Inicial em Estoque: ")
        if estoque_inicial <= 0:
            print("Quantidade inválida!")
            return
        novo_id = len(self.ingredientes) + 1
        self.ingredientes[novo_id] = Ingrediente(nome, estoque_inicial)  # Cria o novo ingrediente usando a classe Ingrediente (em maiúsculo para diferenciar da lista)
        print(f"Sucesso! {nome} cadastrado com ID {novo_id} ({estoque_inicial} Kg).")

    def cadastrar_chocolate(self):
        print("\n======== CADASTRAR NOVO CHOCOLATE ========")
        nome = input("Nome novo do Chocolate: ").strip()
        if nome == "":
            print("Nome Invalido!")
            return
        preco = ler_decimal("Preço da Caixa R$: ")
        if preco <= 0:
            print("Valor Invalido!")
            return
        receita = {}
        print("\nInforme quanto cada caixa gasta de cada ingrediente (digite 0 se não usar):")
        for id_ingrediente, ing in self.ingredientes.items():
            quantidade = ler_numero(f"- {ing.nome}: ")
            if quantidade > 0:
                receita[id_ingrediente] = quantidade

        if len(receita) == 0:
            print("Erro: o chocolate precisa usar pelo menos 1 ingrediente!")
            return

        novo_id = len(self.chocolates) + 1
        self.chocolates[novo_id] = Chocolate(nome, preco, receita=receita)  # Cria o novo Chocolate vinculando a receita montada
        print(f"\nSucesso! '{nome}' cadastrado com ID {novo_id}!")

    def salvar_dados(self):
        # Converte os objetos das classes para dicionários e grava no arquivo JSON
        dados = {
            "ingredientes": {k: v.to_dict() for k, v in self.ingredientes.items()},
            "chocolates": {k: v.to_dict() for k, v in self.chocolates.items()},
            "historico_producao": self.historico_producao,
            "caixa_vendas": self.caixa_vendas,
            "despesas_compras": self.despesas_compras,
            "clientes": {k: v.to_dict() for k, v in self.clientes.items()}
        }
        with open("dados_fabrica.json", "w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, ensure_ascii=False, indent=4)

    def carregar_dados(self):
        if not os.path.exists("dados_fabrica.json"):
            return

        with open("dados_fabrica.json", "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)

        self.ingredientes = {int(k): Ingrediente.from_dict(v) for k, v in dados["ingredientes"].items()}
        self.chocolates = {int(k): Chocolate.from_dict(v) for k, v in dados["chocolates"].items()}
        self.clientes = {k: Cliente.from_dict(v) for k, v in dados.get("clientes", {}).items()}
        self.historico_producao = dados.get("historico_producao", [])
        self.caixa_vendas = dados.get("caixa_vendas", 0.0)
        self.despesas_compras = dados.get("despesas_compras", 0.0)


fabrica = FabricaERP()
fabrica.carregar_dados()

while True:
    print ("=========================================================")
    print ("              FABRICA DE CHOCOLATE  - ERP  V1.0          ")
    print ("=========================================================")
    print("1 - Ver Estoque de Ingredientes")
    print("2 - Repor Ingredientes")
    print("3 - Ver Estoque de Chocolates")
    print("4 - Produzir Chocolates")
    print("5 - Vender Chocolates")
    print("6 - Ver Relatório e Caixa")
    print("7 - Cadastrar Ingrediente")
    print("8 - Cadastrar Chocolate")
    print("0 - Sair")
    print ("=========================================================")

    opcao = ler_numero("Escolha um Número: ")

    match opcao:
        case 1:
            fabrica.mostrar_ingredientes()
        case 2:
            fabrica.comprar_ingredientes()
        case 3:
            fabrica.mostrar_chocolates()
        case 4:
            fabrica.produzir_chocolate()
        case 5:
            fabrica.vender_chocolates()
        case 6:
            fabrica.ver_relatorio()
        case 7:
            fabrica.cadastrar_ingrediente()
        case 8:
            fabrica.cadastrar_chocolate()
        case 0:
            fabrica.salvar_dados()
            print("Dados salvos! Obrigado! Até a Próxima!")
            break
        case _:
            print("Opção Invalida! Tente Novamente!")

    input("\nPressione ENTER para continuar...")
    os.system("cls")