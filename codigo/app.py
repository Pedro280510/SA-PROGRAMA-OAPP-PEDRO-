from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "fabrica_chocolate_erp_v1"

ARQUIVO = "dados_fabrica.json"


# =========================================
# CLASSE INGREDIENTE
# =========================================

class Ingrediente:
    def __init__(self, nome, estoque):
        self.nome = nome
        self.estoque = estoque

    def to_dict(self):
        return {
            "Item": self.nome,
            "Estoque": [self.estoque]
        }

    @classmethod
    def from_dict(cls, dados):
        return cls(dados["Item"], dados["Estoque"][0])


# =========================================
# CLASSE CHOCOLATE
# =========================================

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
        receita = {
            int(k): v for k, v in dados.get("Receita", {}).items()
        }

        return cls(
            dados["Nome"],
            dados["Preco"][0],
            dados["Prontos"][0],
            dados["Vendidos"][0],
            receita
        )


# =========================================
# CLASSE CLIENTE
# =========================================

class Cliente:
    def __init__(self, nome, compras=0):
        self.nome = nome
        self.compras = compras

    def registrar_compra(self):
        self.compras += 1
        return self.compras

    def to_dict(self):
        return {
            "Nome": self.nome,
            "Compras": self.compras
        }

    @classmethod
    def from_dict(cls, dados):
        return cls(dados["Nome"], dados["Compras"])


# =========================================
# CLASSE PRINCIPAL ERP
# =========================================

class FabricaERP:

    def __init__(self):

        self.ingredientes = {
            1: Ingrediente("Massa de Cacau (Kg)", 50),
            2: Ingrediente("Leite em Pó (Kg)", 50),
            3: Ingrediente("Açúcar (Kg)", 50),
            4: Ingrediente("Avelã (Kg)", 50)
        }

        self.chocolates = {
            1: Chocolate(
                "Barra ao Leite", 45.00, 5,
                receita={1: 2, 2: 2, 3: 2}
            ),
            2: Chocolate(
                "Barra Amargo 70%", 55.00, 3,
                receita={1: 4, 3: 1}
            ),
            3: Chocolate(
                "BomBom de Avelã", 70.00, 2,
                receita={1: 2, 2: 1, 3: 2, 4: 2}
            ),
            4: Chocolate(
                "Barra de Chocolate Branco", 50.00, 0,
                receita={2: 3, 3: 2}
            ),
            5: Chocolate(
                "Barra Crocante com Avelã", 60.00, 4,
                receita={1: 3, 2: 1, 3: 1, 4: 1}
            )
        }

        self.historico_producao = []
        self.caixa_vendas = 0.0
        self.despesas_compras = 0.0
        self.clientes = {}

    # =====================================
    # SALVAR DADOS
    # =====================================

    def salvar_dados(self):

        dados = {
            "ingredientes": {
                k: v.to_dict()
                for k, v in self.ingredientes.items()
            },

            "chocolates": {
                k: v.to_dict()
                for k, v in self.chocolates.items()
            },

            "historico_producao": self.historico_producao,
            "caixa_vendas": self.caixa_vendas,
            "despesas_compras": self.despesas_compras,

            "clientes": {
                k: v.to_dict()
                for k, v in self.clientes.items()
            }
        }

        with open(ARQUIVO, "w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, ensure_ascii=False, indent=4)

    # =====================================
    # CARREGAR DADOS
    # =====================================

    def carregar_dados(self):

        if not os.path.exists(ARQUIVO):
            return

        with open(ARQUIVO, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)

        self.ingredientes = {
            int(k): Ingrediente.from_dict(v)
            for k, v in dados["ingredientes"].items()
        }

        self.chocolates = {
            int(k): Chocolate.from_dict(v)
            for k, v in dados["chocolates"].items()
        }

        self.clientes = {
            k: Cliente.from_dict(v)
            for k, v in dados.get("clientes", {}).items()
        }

        self.historico_producao = dados.get(
            "historico_producao", []
        )

        self.caixa_vendas = dados.get("caixa_vendas", 0.0)

        self.despesas_compras = dados.get(
            "despesas_compras", 0.0
        )

    # =====================================
    # REPOR INGREDIENTES
    # =====================================

    def comprar_ingredientes(self, escolha, quantidade, custo):

        if escolha not in self.ingredientes:
            raise ValueError("Ingrediente não encontrado!")

        if quantidade <= 0:
            raise ValueError("Quantidade inválida!")

        if custo < 0:
            raise ValueError("Valor inválido!")

        self.ingredientes[escolha].estoque += quantidade
        self.despesas_compras += custo

        self.salvar_dados()

    # =====================================
    # PRODUZIR CHOCOLATES
    # =====================================

    def produzir_chocolate(self, escolha, lotes):

        if escolha not in self.chocolates:
            raise ValueError("Chocolate inválido!")

        if lotes <= 0:
            raise ValueError("Quantidade inválida!")

        chocolate = self.chocolates[escolha]

        for id_ing, qtd_por_caixa in chocolate.receita.items():

            necessario = qtd_por_caixa * lotes

            if self.ingredientes[id_ing].estoque < necessario:
                raise ValueError(
                    f"Falta {self.ingredientes[id_ing].nome} no estoque!"
                )

        for id_ing, qtd_por_caixa in chocolate.receita.items():

            self.ingredientes[id_ing].estoque -= (
                qtd_por_caixa * lotes
            )

        chocolate.prontos += lotes

        agora = datetime.now().strftime("%d/%m/%Y %H:%M")

        self.historico_producao.append(
            f"[{agora}] {lotes}x {chocolate.nome}"
        )

        self.salvar_dados()

    # =====================================
    # CADASTRAR INGREDIENTE
    # =====================================

    def cadastrar_ingrediente(self, nome, estoque):

        if not nome.strip():
            raise ValueError("Nome inválido!")

        if estoque <= 0:
            raise ValueError("Quantidade inválida!")

        if any(
            ing.nome.strip().lower() == nome.strip().lower()
            for ing in self.ingredientes.values()
        ):
            raise ValueError("Ingrediente já cadastrado!")

        novo_id = max(self.ingredientes.keys(), default=0) + 1

        self.ingredientes[novo_id] = Ingrediente(
            nome, estoque
        )

        self.salvar_dados()

    # =====================================
    # CADASTRAR CHOCOLATE
    # =====================================

    def cadastrar_chocolate(self, nome, preco, receita):

        if not nome.strip():
            raise ValueError("Nome inválido!")

        if preco <= 0:
            raise ValueError("Preço inválido!")

        if not receita:
            raise ValueError("O chocolate precisa de ingredientes!")

        if any(
            choc.nome.strip().lower() == nome.strip().lower()
            for choc in self.chocolates.values()
        ):
            raise ValueError("Chocolate já cadastrado!")

        for id_ing in receita:
            if id_ing not in self.ingredientes:
                raise ValueError("Ingrediente da receita não encontrado!")

        novo_id = max(self.chocolates.keys(), default=0) + 1

        self.chocolates[novo_id] = Chocolate(
            nome,
            preco,
            receita=receita
        )

        self.salvar_dados()

    # =====================================
    # VENDER CHOCOLATES
    # =====================================

    def vender_chocolates(self, carrinho, cpf="", nome_cliente="Cliente Balcão"):

        if not carrinho:
            raise ValueError("Carrinho vazio!")

        # Mantém só os dígitos, para "123.456.789-00" e "12345678900"
        # serem o mesmo cliente no programa de fidelidade
        cpf = "".join(c for c in (cpf or "") if c.isdigit())

        nome_informado = (nome_cliente or "").strip()
        nome_cliente = nome_informado or "Cliente Balcão"

        total = 0.0
        total_caixas = sum(carrinho.values())

        # Verifica o estoque antes de realizar a venda

        for id_item, quantidade in carrinho.items():

            if id_item not in self.chocolates:
                raise ValueError("Chocolate inválido!")

            chocolate = self.chocolates[id_item]

            if quantidade <= 0:
                raise ValueError("Quantidade inválida!")

            if chocolate.prontos < quantidade:
                raise ValueError(
                    f"Estoque insuficiente para {chocolate.nome}!"
                )

        # Identifica o cliente

        ganhou_brinde = False

        if cpf:

            if cpf not in self.clientes:

                self.clientes[cpf] = Cliente(nome_informado or "Cliente")

            cliente = self.clientes[cpf]
            nome_cliente = cliente.nome

            total_compras = cliente.registrar_compra()

            # Fidelidade: a cada 5 compras

            if total_compras % 5 == 0:

                for id_item in carrinho:

                    chocolate = self.chocolates[id_item]

                    if chocolate.prontos > carrinho[id_item]:

                        chocolate.prontos -= 1
                        ganhou_brinde = True
                        break

        # Registra a venda

        for id_item, quantidade in carrinho.items():

            chocolate = self.chocolates[id_item]

            chocolate.prontos -= quantidade
            chocolate.vendidos += quantidade

            total += chocolate.preco * quantidade

        # Desconto de atacado

        desconto = 0.0

        if total_caixas >= 5:

            desconto = round(total * 0.10, 2)
            total -= desconto

        total = round(total, 2)


        self.caixa_vendas += total

        self.salvar_dados()

        return {
            "cliente": nome_cliente,
            "total": total,
            "desconto": desconto,
            "caixas": total_caixas,
            "brinde": ganhou_brinde
        }

    # =====================================
    # RELATÓRIO
    # =====================================

    def ver_relatorio(self):

        lucro = self.caixa_vendas - self.despesas_compras

        campeao = max(
            self.chocolates.values(),
            key=lambda choc: choc.vendidos,
            default=None
        )

        return {
            "receita": self.caixa_vendas,
            "despesas": self.despesas_compras,
            "lucro": lucro,
            "historico": self.historico_producao,
            "campeao": campeao
        }


# =========================================
# INICIALIZAÇÃO DO SISTEMA
# =========================================

fabrica = FabricaERP()
fabrica.carregar_dados()


# =========================================
# MENSAGENS DE ERRO AMIGÁVEIS
# =========================================

def texto_erro(erro):

    if isinstance(erro, KeyError):
        return "Dados inválidos ou incompletos!"

    mensagem = str(erro)

    if "invalid literal" in mensagem or "could not convert" in mensagem:
        return "Valor numérico inválido!"

    return mensagem



# =========================================
# ROTA PRINCIPAL
# =========================================

@app.route("/")
def inicio():

    relatorio = fabrica.ver_relatorio()

    return render_template(
        "index.html",

        ingredientes=fabrica.ingredientes,
        chocolates=fabrica.chocolates,

        relatorio=relatorio,

        clientes=fabrica.clientes,

        carrinho=session.get("carrinho", {})
    )


# =========================================
# ROTA PARA REPOR INGREDIENTES
# =========================================

@app.route("/repor", methods=["POST"])
def repor():

    try:

        escolha = int(request.form["ingrediente"])
        quantidade = int(request.form["quantidade"])
        custo = float(
            request.form["custo"].replace(",", ".")
        )

        fabrica.comprar_ingredientes(
            escolha, quantidade, custo
        )

        flash("Estoque atualizado com sucesso!", "sucesso")

    except (ValueError, KeyError) as erro:
        flash(texto_erro(erro), "erro")

    return redirect(url_for("inicio"))


# =========================================
# ROTA PARA PRODUZIR CHOCOLATES
# =========================================

@app.route("/produzir", methods=["POST"])
def produzir():

    try:

        escolha = int(request.form["chocolate"])
        lotes = int(request.form["lotes"])

        fabrica.produzir_chocolate(escolha, lotes)

        flash("Produção concluída com sucesso!", "sucesso")

    except (ValueError, KeyError) as erro:
        flash(texto_erro(erro), "erro")

    return redirect(url_for("inicio"))


# =========================================
# ROTA PARA ADICIONAR AO CARRINHO
# =========================================

@app.route("/adicionar", methods=["POST"])
def adicionar():

    try:

        escolha = int(request.form["produto"])
        quantidade = int(request.form["quantidade"])

        if escolha not in fabrica.chocolates:
            raise ValueError("Chocolate inválido!")

        if quantidade <= 0:
            raise ValueError("Quantidade inválida!")

        carrinho = session.get("carrinho", {})

        nova_quantidade = carrinho.get(str(escolha), 0) + quantidade

        if nova_quantidade > fabrica.chocolates[escolha].prontos:
            raise ValueError("Estoque insuficiente!")

        carrinho[str(escolha)] = nova_quantidade

        session["carrinho"] = carrinho

        flash("Produto adicionado ao carrinho!", "sucesso")

    except (ValueError, KeyError) as erro:
        flash(texto_erro(erro), "erro")


    return redirect(url_for("inicio"))


# =========================================
# ROTA PARA REMOVER PRODUTO DO CARRINHO
# =========================================

@app.route("/remover/<int:id_item>", methods=["POST"])
def remover(id_item):

    carrinho = session.get("carrinho", {})

    carrinho.pop(str(id_item), None)

    session["carrinho"] = carrinho

    return redirect(url_for("inicio"))


# =========================================
# ROTA PARA FINALIZAR VENDA
# =========================================

@app.route("/finalizar_venda", methods=["POST"])
def finalizar_venda():

    try:

        carrinho = {
            int(k): int(v)
            for k, v in session.get("carrinho", {}).items()
        }

        cpf = request.form.get("cpf", "").strip()
        nome = request.form.get("nome", "").strip()

        resultado = fabrica.vender_chocolates(
            carrinho, cpf, nome
        )

        session["carrinho"] = {}

        flash(
            f"Venda concluída! Total: R$ {resultado['total']:.2f}",
            "sucesso"
        )

        if resultado["desconto"] > 0:
            flash(
                f"Desconto aplicado: R$ {resultado['desconto']:.2f}",
                "sucesso"
            )

        if resultado["brinde"]:
            flash("Parabéns! O cliente ganhou uma caixa grátis!", "sucesso")

    except (ValueError, KeyError) as erro:
        flash(texto_erro(erro), "erro")

    return redirect(url_for("inicio"))


# =========================================
# ROTA PARA CADASTRAR INGREDIENTE
# =========================================

@app.route("/cadastrar_ingrediente", methods=["POST"])
def cadastrar_ingrediente():

    try:

        nome = request.form["nome"].strip()
        estoque = int(request.form["estoque"])

        fabrica.cadastrar_ingrediente(nome, estoque)

        flash("Ingrediente cadastrado com sucesso!", "sucesso")

    except (ValueError, KeyError) as erro:
        flash(texto_erro(erro), "erro")


    return redirect(url_for("inicio"))


# =========================================
# ROTA PARA CADASTRAR CHOCOLATE
# =========================================

@app.route("/cadastrar_chocolate", methods=["POST"])
def cadastrar_chocolate():

    try:

        nome = request.form["nome"].strip()

        preco = float(
            request.form["preco"].replace(",", ".")
        )

        receita = {}

        for id_ing in fabrica.ingredientes:

            quantidade = int(
                request.form.get(f"ingrediente_{id_ing}", 0)
            )

            if quantidade < 0:
                raise ValueError("Quantidade inválida!")

            if quantidade > 0:
                receita[id_ing] = quantidade

        fabrica.cadastrar_chocolate(
            nome, preco, receita
        )

        flash("Chocolate cadastrado com sucesso!", "sucesso")

    except (ValueError, KeyError) as erro:
        flash(texto_erro(erro), "erro")

    return redirect(url_for("inicio"))


# =========================================
# INICIAR SERVIDOR
# =========================================

if __name__ == "__main__":

    app.run(debug=True)