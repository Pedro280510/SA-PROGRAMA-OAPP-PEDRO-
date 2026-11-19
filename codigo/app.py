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
# MENSAGENS DE ERRO AMIGÁVEIS
# =========================================

def texto_erro(erro):

    if isinstance(erro, KeyError):
        return "Dados inválidos ou incompletos!"

    mensagem = str(erro)

    if "invalid literal" in mensagem or "could not convert" in mensagem:
        return "Valor numérico inválido!"

    return mensagem
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
        flash(texto_erro(erro), "erro")

    return redirect(url_for("inicio"))


# =========================================
# INICIAR SERVIDOR
# =========================================

if __name__ == "__main__":

    app.run(debug=True)