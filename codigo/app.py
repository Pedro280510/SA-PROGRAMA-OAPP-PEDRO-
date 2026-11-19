import os
import json
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session

ARQUIVO = "dados_fabrica.json"


def para_int(valor, padrao=0):
    try:
        return int(str(valor).strip())
    except ValueError:
        return padrao


def para_float(valor, padrao=0.0):
    try:
        return float(str(valor).strip().replace(",", "."))
    except ValueError:
        return padrao


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
        return {"Nome": self.nome, "Receita": self.receita, "Prontos": [self.prontos],
                "Preco": [self.preco], "Vendidos": [self.vendidos]}

    @classmethod
    def from_dict(cls, dados):
        receita = {int(k): v for k, v in dados.get("Receita", {}).items()}
        return cls(dados["Nome"], dados["Preco"][0], dados["Prontos"][0],
                   dados["Vendidos"][0], receita)


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
            4: Ingrediente("Avelã (Kg)", 50),
        }
        self.chocolates = {
            1: Chocolate("Barra ao Leite", 45.00, prontos=5, receita={1: 2, 2: 2, 3: 2}),
            2: Chocolate("Barra Amargo 70%", 55.00, prontos=3, receita={1: 4, 3: 1}),
            3: Chocolate("BomBom de Avelã", 70.00, prontos=2, receita={1: 2, 2: 1, 3: 2, 4: 2}),
            4: Chocolate("Barra de Chocolate Branco", 50.00, prontos=0, receita={2: 3, 3: 2}),
            5: Chocolate("Barra Crocante com Avelã", 60.00, prontos=4, receita={1: 3, 2: 1, 3: 1, 4: 1}),
        }
        self.historico_producao = []
        self.caixa_vendas = 0.0
        self.despesas_compras = 0.0
        self.clientes = {}

    # ---------- Ingredientes ----------
    def comprar_ingredientes(self, id_ing, quantidade, custo):
        if id_ing not in self.ingredientes:
            return "erro", "Ingrediente não encontrado."
        if quantidade <= 0:
            return "erro", "Informe uma quantidade maior que zero."
        if custo < 0:
            return "erro", "O valor pago não pode ser negativo."
        self.ingredientes[id_ing].estoque += quantidade
        self.despesas_compras += custo
        return "ok", f"Estoque de {self.ingredientes[id_ing].nome} atualizado (+{quantidade} Kg)."

    def cadastrar_ingrediente(self, nome, estoque):
        if not nome:
            return "erro", "Informe o nome do ingrediente."
        if estoque <= 0:
            return "erro", "O estoque inicial deve ser maior que zero."
        novo_id = max(self.ingredientes, default=0) + 1
        self.ingredientes[novo_id] = Ingrediente(nome, estoque)
        return "ok", f"{nome} cadastrado com {estoque} Kg."

    # ---------- Chocolates ----------
    def produzir_chocolate(self, id_choc, lotes):
        if id_choc not in self.chocolates:
            return "erro", "Chocolate inválido."
        if lotes <= 0:
            return "erro", "Informe quantas caixas produzir."
        choc = self.chocolates[id_choc]
        for id_ing, qtd in choc.receita.items():
            if self.ingredientes[id_ing].estoque < qtd * lotes:
                return "erro", f"Falta {self.ingredientes[id_ing].nome} no estoque."
        for id_ing, qtd in choc.receita.items():
            self.ingredientes[id_ing].estoque -= qtd * lotes
        choc.prontos += lotes
        agora = datetime.now().strftime("%d/%m/%Y %H:%M")
        self.historico_producao.append(f"[{agora}] {lotes}x {choc.nome}")
        return "ok", f"{lotes} caixa(s) de {choc.nome} produzida(s)."

    def cadastrar_chocolate(self, nome, preco, receita):
        if not nome:
            return "erro", "Informe o nome do chocolate."
        if preco <= 0:
            return "erro", "O preço deve ser maior que zero."
        if not receita:
            return "erro", "O chocolate precisa usar pelo menos 1 ingrediente."
        novo_id = max(self.chocolates, default=0) + 1
        self.chocolates[novo_id] = Chocolate(nome, preco, receita=receita)
        return "ok", f"{nome} cadastrado."

    # ---------- Vendas ----------
    def resumo_carrinho(self, carrinho):
        itens, bruto, caixas = [], 0.0, 0
        for id_item, qtd in carrinho.items():
            choc = self.chocolates[id_item]
            itens.append({"id": id_item, "nome": choc.nome, "qtd": qtd, "subtotal": choc.preco * qtd})
            bruto += choc.preco * qtd
            caixas += qtd
        desconto = bruto * 0.10 if caixas >= 5 else 0.0
        return {"itens": itens, "bruto": bruto, "desconto": desconto, "total": bruto - desconto}

    def adicionar_ao_carrinho(self, carrinho, id_choc, qtd):
        if id_choc not in self.chocolates:
            return "erro", "Chocolate inválido."
        if qtd <= 0:
            return "erro", "Informe uma quantidade maior que zero."
        choc = self.chocolates[id_choc]
        ja = carrinho.get(id_choc, 0)
        if choc.prontos < ja + qtd:
            return "erro", f"Estoque insuficiente. Disponível: {choc.prontos - ja} cx."
        carrinho[id_choc] = ja + qtd
        return "ok", f"{qtd}x {choc.nome} no carrinho."

    def finalizar_venda(self, carrinho, cpf, nome):
        msgs = []
        for id_item, qtd in carrinho.items():
            if self.chocolates[id_item].prontos < qtd:
                return [("erro", f"Estoque de {self.chocolates[id_item].nome} mudou. Revise o carrinho.")]

        nome_cliente = "Cliente Balcão"
        if cpf:
            if cpf not in self.clientes:
                nome_cliente = nome or "Cliente"
                self.clientes[cpf] = Cliente(nome_cliente)
            else:
                nome_cliente = self.clientes[cpf].nome
            n = self.clientes[cpf].registrar_compra()
            msgs.append(("ok", f"{nome_cliente}: compra nº {n} no cartão fidelidade."))
            if n % 5 == 0:
                for id_item, qtd in carrinho.items():
                    choc = self.chocolates[id_item]
                    if choc.prontos >= qtd + 1:
                        choc.prontos -= 1
                        msgs.append(("ok", f"5ª compra: +1 caixa grátis de {choc.nome}."))
                        break

        resumo = self.resumo_carrinho(carrinho)
        for id_item, qtd in carrinho.items():
            self.chocolates[id_item].prontos -= qtd
            self.chocolates[id_item].vendidos += qtd
        self.caixa_vendas += resumo["total"]
        if resumo["desconto"]:
            msgs.append(("ok", f"Desconto de atacado aplicado: -R$ {resumo['desconto']:.2f}."))
        msgs.append(("ok", f"Venda concluída para {nome_cliente}: R$ {resumo['total']:.2f}."))
        return msgs

    # ---------- Relatório ----------
    def campeao(self):
        melhor = max(self.chocolates.values(), key=lambda c: c.vendidos, default=None)
        return melhor if melhor and melhor.vendidos > 0 else None

    # ---------- Persistência ----------
    def salvar_dados(self):
        dados = {
            "ingredientes": {k: v.to_dict() for k, v in self.ingredientes.items()},
            "chocolates": {k: v.to_dict() for k, v in self.chocolates.items()},
            "historico_producao": self.historico_producao,
            "caixa_vendas": self.caixa_vendas,
            "despesas_compras": self.despesas_compras,
            "clientes": {k: v.to_dict() for k, v in self.clientes.items()},
        }
        with open(ARQUIVO, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)

    def carregar_dados(self):
        if not os.path.exists(ARQUIVO):
            return
        with open(ARQUIVO, "r", encoding="utf-8") as f:
            dados = json.load(f)
        self.ingredientes = {int(k): Ingrediente.from_dict(v) for k, v in dados["ingredientes"].items()}
        self.chocolates = {int(k): Chocolate.from_dict(v) for k, v in dados["chocolates"].items()}
        self.clientes = {k: Cliente.from_dict(v) for k, v in dados.get("clientes", {}).items()}
        self.historico_producao = dados.get("historico_producao", [])
        self.caixa_vendas = dados.get("caixa_vendas", 0.0)
        self.despesas_compras = dados.get("despesas_compras", 0.0)


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "troque-esta-chave-em-producao")
fabrica = FabricaERP()
fabrica.carregar_dados()


@app.template_filter("brl")
def brl(valor):
    texto = f"{valor:,.2f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


def avisar(resultado, salvar=True):
    categoria, mensagem = resultado
    flash(mensagem, categoria)
    if categoria == "ok" and salvar:
        fabrica.salvar_dados()
    return categoria == "ok"


def carrinho_atual():
    return {int(k): v for k, v in session.get("carrinho", {}).items()}


@app.route("/")
def painel():
    return render_template("painel.html", f=fabrica, lucro=fabrica.caixa_vendas - fabrica.despesas_compras,
                           campeao=fabrica.campeao(), pagina="painel")


@app.route("/ingredientes")
def ingredientes():
    return render_template("ingredientes.html", f=fabrica, pagina="ingredientes")


@app.post("/ingredientes/repor")
def repor_ingrediente():
    avisar(fabrica.comprar_ingredientes(para_int(request.form.get("id")),
                                        para_int(request.form.get("quantidade")),
                                        para_float(request.form.get("custo"))))
    return redirect(url_for("ingredientes"))


@app.post("/ingredientes/novo")
def novo_ingrediente():
    avisar(fabrica.cadastrar_ingrediente(request.form.get("nome", "").strip(),
                                         para_int(request.form.get("estoque"))))
    return redirect(url_for("ingredientes"))


@app.route("/chocolates")
def chocolates():
    return render_template("chocolates.html", f=fabrica, pagina="chocolates")


@app.post("/chocolates/produzir")
def produzir():
    avisar(fabrica.produzir_chocolate(para_int(request.form.get("id")), para_int(request.form.get("lotes"))))
    return redirect(url_for("chocolates"))


@app.post("/chocolates/novo")
def novo_chocolate():
    receita = {}
    for id_ing in fabrica.ingredientes:
        qtd = para_int(request.form.get(f"ing_{id_ing}"))
        if qtd > 0:
            receita[id_ing] = qtd
    avisar(fabrica.cadastrar_chocolate(request.form.get("nome", "").strip(),
                                       para_float(request.form.get("preco")), receita))
    return redirect(url_for("chocolates"))


@app.route("/vender")
def vender():
    carrinho = carrinho_atual()
    return render_template("vender.html", f=fabrica, resumo=fabrica.resumo_carrinho(carrinho), pagina="vender")


@app.post("/vender/adicionar")
def adicionar():
    carrinho = carrinho_atual()
    avisar(fabrica.adicionar_ao_carrinho(carrinho, para_int(request.form.get("id")),
                                         para_int(request.form.get("quantidade"), 1)), salvar=False)
    session["carrinho"] = carrinho
    return redirect(url_for("vender"))


@app.post("/vender/remover/<int:id_choc>")
def remover(id_choc):
    carrinho = carrinho_atual()
    carrinho.pop(id_choc, None)
    session["carrinho"] = carrinho
    return redirect(url_for("vender"))


@app.post("/vender/finalizar")
def finalizar():
    carrinho = carrinho_atual()
    if not carrinho:
        flash("O carrinho está vazio.", "erro")
        return redirect(url_for("vender"))
    msgs = fabrica.finalizar_venda(carrinho, request.form.get("cpf", "").strip(),
                                   request.form.get("nome", "").strip())
    for categoria, texto in msgs:
        flash(texto, categoria)
    if msgs[-1][0] == "ok":
        fabrica.salvar_dados()
        session["carrinho"] = {}
    return redirect(url_for("vender"))


if __name__ == "__main__":
    app.run(debug=True)
