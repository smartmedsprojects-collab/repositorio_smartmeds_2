from flask import Flask, render_template, request, redirect, url_for, flash
from models.produto import Produto
from models.movimentacao import Movimentacao
#from models.pedido_movimentacao import Pedidos
from models.localizaçao import Localizacao
from models.item_saida import ItemSaida
from models.item_entrada import ItemEntrada
from models.fornecedor import Fornecedor
from models.cliente import Cliente

app = Flask(__name__)
app.secret_key = "chave_secreta"

@app.route("/")
def index():
    return render_template("base.html")

def get_cliente_form():
    return {
        "nome": request.form.get("nome", "").strip(),
        "email": request.form.get("email", "").strip(),
        "senha": request.form.get("senha", "").strip(),
        "cnpj": request.form.get("cnpj", "").strip(),
    }

def get_fornecedor_form():
    return {
    "nome": request.form.get("nome", "").strip(),
    "email": request.form.get("email", "").strip(),
    "senha": request.form.get("senha", "").strip(),
    "cnpj": request.form.get("cnpj", "").strip(),
    }

def get_produto_form():
    return {
        "nome": request.form.get("nome", "").strip(),
        "marca": request.form.get("marca", "").strip(),
        "data_de_validade": request.form.get("data_de_validade", "").strip(),
        "especificacao": request.form.get("especificacao", "").strip(),
        "unidade_medida": request.form.get("unidade_medida", "").strip(),
    }




    
#(Cliente)===========================================================================================
# FORMULÁRIO NOVO CLIENTE
@app.route("/cliente/novo", methods=["GET"])
def novo_cliente():
    return render_template("Cliente.html",cliente=None)

#LISTAR CLIENTES
@app.route("/clientes", methods=["GET"])
def listar_clientes():
    try:
        clientes = Cliente.find_all(order_by="id DESC")
        return render_template("cliente_lista.html",clientes=clientes)
    except Exception as e:
        flash("Erro ao carregar clientes.","erro")
        return render_template("cliente_lista.html",clientes=[])

# SALVAR CLIENTE
@app.route("/cliente/salvar", methods=["POST"])
def salvar_cliente():
    dados = get_cliente_form()
    dados["email"] = dados["email"].lower().strip()
    cliente = Cliente(**dados)
    erros = cliente.validate()
    if erros:
        for erro in erros:
            flash(erro, "erro")
        return render_template("Cliente.html",cliente=cliente)
    try:
        novo_id = cliente.insert()
        flash("Cliente cadastrado com sucesso.","sucesso")
        return redirect(url_for("listar_clientes",id=novo_id))
    except Exception as e:
        flash("Erro ao cadastrar cliente.","erro")
        return render_template("cliente_lista.html",cliente=cliente)

# BUSCAR CLIENTE
@app.route("/cliente/<int:id>/editar", methods=["GET"])
def buscar_cliente(id):
    try:
        cliente = Cliente.find_by_id(id)
        if not cliente:
            flash("Cliente não encontrado.","erro")
            return redirect(url_for("cliente_lista"))
        return render_template("Cliente.html",cliente=cliente)
    except Exception as e:
        flash("Erro ao carregar cliente.","erro")
        return redirect(url_for("cliente_lista"))

# ATUALIZAR CLIENTE
@app.route("/cliente/<int:id>/atualizar", methods=["POST"])
def atualizar_cliente(id):
    dados = get_cliente_form()
    dados["email"] = dados["email"].lower().strip()
    cliente = Cliente(**dados)
    erros = cliente.validate()
    if erros:
        for erro in erros:
            flash(erro, "erro")
        dados["id"] = id
        return render_template("Cliente.html",cliente=dados)
    try:
        cliente_existente = Cliente.find_by_id(id)
        if not cliente_existente:
            flash(
                "Cliente não encontrado.","erro")
            return redirect(url_for("listar_clientes"))
        linhas_afetadas = cliente.update(id)
        if linhas_afetadas == 0:
            flash("Nenhuma alteração realizada.","erro")
            return redirect(url_for("buscar_cliente",id=id))
        flash("Cliente atualizado com sucesso.","sucesso")
        return redirect(url_for("buscar_cliente",id=id))
    except Exception as e:
        flash("Erro ao atualizar cliente.","erro")
        return render_template("Cliente.html",cliente=dados)

# EXCLUIR CLIENTE
@app.route("/cliente/<int:id>/excluir")
def excluir_cliente(id):
    try:
        cliente = Cliente.find_by_id(id)
        if not cliente:
            flash("Cliente não encontrado.","erro")
            return redirect(url_for("listar_clientes"))
        Cliente.safe_delete(id)
        flash("Cliente excluído com sucesso.","sucesso")
    except ValueError as e:
        flash(str(e), "erro")
    except Exception as e:
        flash("Erro ao excluir cliente.","erro")
    return redirect(url_for("listar_clientes"))








    

#(Produto)============================================================================================
# FORMULÁRIO NOVO PRODUTO
@app.route("/produto/novo", methods=["GET"])
def novo_produto():
    return render_template("produtos.html", produto=None)

# LISTAR PRODUTOS
@app.route("/produtos", methods=["GET"])
def listar_produtos():
    try:
        produtos = Produto.find_all(order_by="id DESC")
        return render_template("listar_produtos.html", produtos=produtos)
    except Exception as e:
        flash("Erro ao carregar produtos.", "erro")
        return render_template("listar_produtos.html", produtos=[])

# SALVAR PRODUTO
@app.route("/produto/salvar", methods=["POST"])
def salvar_produto():
    dados = get_produto_form()
    produto = Produto(**dados)
    erros = produto.validate()
    if erros:
        for erro in erros:
            flash(erro, "erro")
        return render_template("produtos.html", produto=produto)
    try:
        novo_id = produto.insert()
        flash("Produto cadastrado com sucesso.", "sucesso")
        return redirect(url_for("listar_produtos"))
    except Exception as e:
        flash(f"Erro ao cadastrar produto: {e}", "erro")
        return render_template("produtos.html", produto=produto)

# BUSCAR PRODUTO
@app.route("/produto/<int:id>/editar", methods=["GET"])
def buscar_produto(id):
    try:
        produto = Produto.find_by_id(id)
        if not produto:
            flash("Produto não encontrado.","erro")
            return redirect(url_for("listar_produtos"))
        return render_template("produtos.html",produto=produto)
    except Exception as e:
        flash("Erro ao carregar produto.","erro")
        return redirect(url_for("listar_produtos"))

# ATUALIZAR PRODUTO
@app.route("/produto/<int:id>/atualizar", methods=["POST"])
def atualizar_produto(id):
    dados = get_produto_form()
    produto = Produto(**dados)
    erros = produto.validate()
    if erros:
        for erro in erros:
            flash(erro, "erro")
        dados["id"] = id
        return render_template("produtos.html",produto=dados)
    try:
        produto_existente = Produto.find_by_id(id)
        if not produto_existente:
            flash("Produto não encontrado.","erro")
            return redirect(url_for("listar_produtos"))
        linhas_afetadas = produto.update(id)
        if linhas_afetadas == 0:
            flash("Nenhuma alteração realizada.","erro")
            return redirect(url_for("buscar_produto",id=id))
        flash("Produto atualizado com sucesso.","sucesso")
        return redirect(url_for("buscar_produto",id=id))
    except Exception as e:
        flash("Erro ao atualizar produto.","erro")
        return render_template("produtos.html",produto=dados)

# EXCLUIR PRODUTO
@app.route("/produto/<int:id>/excluir")
def excluir_produto(id):
    try:
        produto = Produto.find_by_id(id)
        if not produto:
            flash("Produto não encontrado.", "erro")
            return redirect(url_for("listar_produtos"))
        Produto.safe_delete(id)
        flash("Produto excluído com sucesso.", "sucesso")
    except Exception:
        flash("Erro ao excluir produto.", "erro")
    return redirect(url_for("listar_produtos"))

#(Fornecedor)===============================================================================
 # FORMULÁRIO NOVO FORNECEDOR
@app.route("/fornecedor/novo", methods=["GET"])
def novo_fornecedor():
    return render_template("fornecedor.html",fornecedor=None)

    # LISTAR FORNECEDORES
@app.route("/fornecedor", methods=["GET"])
def listar_fornecedor():
    try:
        fornecedores = Fornecedor.find_all(order_by="id DESC")
        return render_template("fornecedor_lista.html",fornecedores=fornecedores)
    except Exception:
            flash("Erro ao carregar fornecedores.","erro")
            return render_template("fornecedor_lista.html",fornecedores=[])


    # SALVAR FORNECEDOR
@app.route("/fornecedor/salvar", methods=["POST"])
def salvar_fornecedor():
    dados = get_fornecedor_form()
    dados["email"] = dados["email"].lower().strip()
    fornecedor = Fornecedor(**dados)
    erros = fornecedor.validate()
    if erros:
        for erro in erros:
            flash(erro, "erro")
        return render_template("fornecedor.html", fornecedor=fornecedor)
    try:
        novo_id = fornecedor.insert()
        flash("Fornecedor cadastrado com sucesso.", "sucesso")
        return redirect(url_for("buscar_fornecedor", id=novo_id))
    except Exception:
        flash("Erro ao cadastrar fornecedor.", "erro")
        return render_template("fornecedor.html", fornecedor=fornecedor)

    # BUSCAR FORNECEDOR
    @app.route(
        "/fornecedor/<int:id>/editar",
        methods=["GET"]
    )
    def buscar_fornecedor(id):
        try:
            fornecedor = Fornecedor.find_by_id(id)

            if not fornecedor:
                flash(
                    "Fornecedor não encontrado.",
                    "erro"
                )

                return redirect(
                    url_for(
                        "listar_fornecedor"
                    )
                )

            return render_template(
                "fornecedor.html",
                fornecedor=fornecedor
            )

        except Exception:
            flash(
                "Erro ao carregar fornecedor.",
                "erro"
            )

            return redirect(
                url_for(
                    "listar_fornecedor"
                )
            )


    # ATUALIZAR FORNECEDOR
    @app.route(
        "/fornecedor/<int:id>/atualizar",
        methods=["POST"]
    )
    def atualizar_fornecedor(id):
        dados = get_fornecedor_form()

        dados["email"] = (
            dados["email"]
            .lower()
            .strip()
        )

        fornecedor = Fornecedor(**dados)

        erros = fornecedor.validate()

        if erros:
            for erro in erros:
                flash(erro, "erro")

            dados["id"] = id

            return render_template(
                "fornecedor.html",
                fornecedor=dados
            )

        try:
            fornecedor_existente = (
                Fornecedor.find_by_id(id)
            )

            if not fornecedor_existente:
                flash(
                    "Fornecedor não encontrado.",
                    "erro"
                )

                return redirect(
                    url_for(
                        "listar_fornecedor"
                    )
                )

            linhas_afetadas = fornecedor.update(id)

            if linhas_afetadas == 0:
                flash(
                    "Nenhuma alteração realizada.","erro")
                return redirect(url_for("buscar_fornecedor",id=id))
            flash("Fornecedor atualizado com sucesso.","sucesso")
            return redirect(url_for("buscar_fornecedor",id=id))
        except Exception:
            flash("Erro ao atualizar fornecedor.","erro")
            return render_template("fornecedor.html",fornecedor=dados)


# EXCLUIR FORNECEDOR
@app.route("/fornecedor/<int:id>/excluir")
def excluir_fornecedor(id):
    try:
        fornecedor = (Fornecedor.find_by_id(id))
        if not fornecedor:
            flash("Fornecedor não encontrado.","erro")
        return redirect(url_for("listar_fornecedor"))
        Fornecedor.safe_delete(id)
        flash("Fornecedor excluído com sucesso.","sucesso")
    except ValueError as e:
        flash(str(e),"erro")
    except Exception:
        flash("Erro ao excluir fornecedor.","erro")
    return redirect(url_for("listar_fornecedor"))









#(Pedido entrada)============================================================================================
# FORMULÁRIO NOVO PEDIDO ENTRADA
@app.route("/pedido_entrada/novo", methods=["GET"])
def novo_pedido_entrada():
    return render_template("pedido_entrada.html", pedido_entrada=None)

# LISTAR PEDIDOS ENTRADA
@app.route("/pedidos_entrada", methods=["GET"])
def listar_pedidos_entrada():
    try:
        pedidos_entrada = PedidoEntrada.find_all(order_by="id DESC")
        return render_template("pedido_entrada_lista.html", pedidos_entrada=pedidos_entrada)
    except Exception as e:
        flash("Erro ao carregar pedidos entrada.", "erro")
        return render_template("pedido_entrada_lista.html", pedidos_entrada=[])
# SALVAR PEDIDO ENTRADA
@app.route("/pedido_entrada/salvar", methods=["POST"])
def salvar_pedido_entrada():
    dados = get_pedido_entrada_form()
    pedido_entrada = PedidoEntrada(**dados)
    erros = pedido_entrada.validate()
    if erros:
        for erro in erros:
            flash(erro, "erro")
        return render_template("pedido_entrada.html", pedido_entrada=pedido_entrada)
    try:
        novo_id = pedido_entrada.insert()
        flash("Pedido entrada cadastrado com sucesso.", "sucesso")
        return redirect(url_for("buscar_pedido_entrada", id=novo_id))
    except Exception as e:
        flash("Erro ao cadastrar pedido entrada.", "erro")
        return render_template("pedido_entrada.html", pedido_entrada=pedido_entrada)

# BUSCAR PEDIDO ENTRADA
@app.route("/pedido_entrada/<int:id>/editar", methods=["GET"])
def buscar_pedido_entrada(id):
    try:
        pedido_entrada = PedidoEntrada.find_by_id(id)
        if not pedido_entrada:
            flash("Pedido entrada não encontrado.", "erro")
            return redirect(url_for("listar_pedidos_entrada"))
        return render_template("pedido_entrada.html", pedido_entrada=pedido_entrada)
    except Exception as e:
        flash("Erro ao carregar pedido entrada.", "erro")
        return redirect(url_for("listar_pedidos_entrada"))

# ATUALIZAR PEDIDO ENTRADA
@app.route("/pedido_entrada/<int:id>/atualizar", methods=["POST"])
def atualizar_pedido_entrada(id):
    dados = get_pedido_entrada_form()
    pedido_entrada = PedidoEntrada(**dados)
    erros = pedido_entrada.validate()
    if erros:
        for erro in erros:
            flash(erro, "erro")
        dados["id"] = id
        return render_template("pedido_entrada.html", pedido_entrada=dados)
    try:
        pedido_entrada_existente = PedidoEntrada.find_by_id(id)
        if not pedido_entrada_existente:
            flash("Pedido entrada não encontrado.", "erro")
            return redirect(url_for("listar_pedidos_entrada"))
        linhas_afetadas = pedido_entrada.update(id)
        if linhas_afetadas == 0:
            flash("Nenhuma alteração realizada.", "erro")
            return redirect(url_for("buscar_pedido_entrada", id=id))
        flash("Pedido entrada atualizado com sucesso.", "sucesso")
        return redirect(url_for("buscar_pedido_entrada", id=id))
    except Exception as e:
        flash("Erro ao atualizar pedido entrada.", "erro")
        return render_template("pedido_entrada.html", pedido_entrada=dados)

# EXCLUIR PEDIDO ENTRADA
@app.route("/pedido_entrada/<int:id>/excluir")
def excluir_pedido_entrada(id):
    try:
        pedido_entrada = PedidoEntrada.find_by_id(id)
        if not pedido_entrada:
            flash("Pedido entrada não encontrado.", "erro")
            return redirect(url_for("listar_pedidos_entrada"))
        PedidoEntrada.safe_delete(id)
        flash("Pedido entrada excluído com sucesso.", "sucesso")
    except ValueError as e:
        flash(str(e), "erro")
    except Exception as e:
        flash("Erro ao excluir pedido entrada.", "erro")
    return redirect(url_for("listar_pedidos_entrada"))





#(Localização)============================================================================================
# FORMULÁRIO NOVA LOCALIZAÇÃO
@app.route("/localizacao/novo", methods=["GET"])
def nova_localizacao():
    return render_template("localizacao.html", localizacao=None)

# LISTAR LOCALIZAÇÕES
@app.route("/localizacoes", methods=["GET"])
def listar_localizacoes():
    try:
        localizacoes = Localizacao.find_all(order_by="id DESC")
        return render_template("localizacao_lista.html", localizacoes=localizacoes)
    except Exception as e:
        flash("Erro ao carregar localizações.", "erro")
        return render_template("localizacao_lista.html", localizacoes=[])

# SALVAR LOCALIZAÇÃO
@app.route("/localizacao/salvar", methods=["POST"])
def salvar_localizacao():
    dados = get_localizacao_form()
    localizacao = Localizacao(**dados)
    erros = localizacao.validate()
    if erros:
        for erro in erros:
            flash(erro, "erro")
        return render_template("localizacao.html", localizacao=localizacao)
    try:
        novo_id = localizacao.insert()
        flash("Localização cadastrada com sucesso.", "sucesso")
        return redirect(url_for("buscar_localizacao", id=novo_id))
    except Exception as e:
        flash("Erro ao cadastrar localização.", "erro")
        return render_template("localizacao.html", localizacao=localizacao)

# BUSCAR LOCALIZAÇÃO
@app.route("/localizacao/<int:id>/editar", methods=["GET"])
def buscar_localizacao(id):
    try:
        localizacao = Localizacao.find_by_id(id)
        if not localizacao:
            flash("Localização não encontrada.", "erro")
            return redirect(url_for("listar_localizacoes"))
        return render_template("localizacao.html", localizacao=localizacao)
    except Exception as e:
        flash("Erro ao carregar localização.", "erro")
        return redirect(url_for("listar_localizacoes"))

# ATUALIZAR LOCALIZAÇÃO
@app.route("/localizacao/<int:id>/atualizar", methods=["POST"])
def atualizar_localizacao(id):
    dados = get_localizacao_form()
    localizacao = Localizacao(**dados)
    erros = localizacao.validate()
    if erros:
        for erro in erros:
            flash(erro, "erro")
        dados["id"] = id
        return render_template("localizacao.html", localizacao=dados)
    try:
        localizacao_existente = Localizacao.find_by_id(id)
        if not localizacao_existente:
            flash("Localização não encontrada.", "erro")
            return redirect(url_for("listar_localizacoes"))
        linhas_afetadas = localizacao.update(id)
        if linhas_afetadas == 0:
            flash("Nenhuma alteração realizada.", "erro")
            return redirect(url_for("buscar_localizacao", id=id))
        flash("Localização atualizada com sucesso.", "sucesso")
        return redirect(url_for("buscar_localizacao", id=id))
    except Exception as e:
        flash("Erro ao atualizar localização.", "erro")
        return render_template("localizacao.html", localizacao=dados)

# EXCLUIR LOCALIZAÇÃO
@app.route("/localizacao/<int:id>/excluir")
def excluir_localizacao(id):
    try:
        localizacao = Localizacao.find_by_id(id)
        if not localizacao:
            flash("Localização não encontrada.", "erro")
            return redirect(url_for("listar_localizacoes"))
        Localizacao.safe_delete(id)
        flash("Localização excluída com sucesso.", "sucesso")
    except ValueError as e:
        flash(str(e), "erro")
    except Exception as e:
        flash("Erro ao excluir localização.", "erro")
    return redirect(url_for("listar_localizacoes"))









#(Estoque)============================================================================================
# FORMULÁRIO NOVO ESTOQUE
@app.route("/estoque/novo", methods=["GET"])
def novo_estoque():
    return render_template("estoque.html", estoque=None)

# LISTAR ESTOQUES
@app.route("/estoques", methods=["GET"])
def listar_estoques():
    try:
        estoques = Estoque.find_all(order_by="id DESC")
        return render_template("estoque_lista.html", estoques=estoques)
    except Exception as e:
        flash("Erro ao carregar estoques.", "erro")
        return render_template("estoque_lista.html", estoques=[])

# SALVAR ESTOQUE
@app.route("/estoque/salvar", methods=["POST"])
def salvar_estoque():
    dados = get_estoque_form()
    estoque = Estoque(**dados)
    erros = estoque.validate()
    if erros:
        for erro in erros:
            flash(erro, "erro")
        return render_template("estoque.html", estoque=estoque)
    try:
        novo_id = estoque.insert()
        flash("Estoque cadastrado com sucesso.", "sucesso")
        return redirect(url_for("buscar_estoque", id=novo_id))
    except Exception as e:
        flash("Erro ao cadastrar estoque.", "erro")
        return render_template("estoque.html", estoque=estoque)

# BUSCAR ESTOQUE
@app.route("/estoque/<int:id>/editar", methods=["GET"])
def buscar_estoque(id):
    try:
        estoque = Estoque.find_by_id(id)
        if not estoque:
            flash("Estoque não encontrado.", "erro")
            return redirect(url_for("listar_estoques"))
        return render_template("estoque.html", estoque=estoque)
    except Exception as e:
        flash("Erro ao carregar estoque.", "erro")
        return redirect(url_for("listar_estoques"))

# ATUALIZAR ESTOQUE
@app.route("/estoque/<int:id>/atualizar", methods=["POST"])
def atualizar_estoque(id):
    dados = get_estoque_form()
    estoque = Estoque(**dados)
    erros = estoque.validate()
    if erros:
        for erro in erros:
            flash(erro, "erro")
        dados["id"] = id
        return render_template("estoque.html", estoque=dados)
    try:
        estoque_existente = Estoque.find_by_id(id)
        if not estoque_existente:
            flash("Estoque não encontrado.", "erro")
            return redirect(url_for("listar_estoques"))
        linhas_afetadas = estoque.update(id)
        if linhas_afetadas == 0:
            flash("Nenhuma alteração realizada.", "erro")
            return redirect(url_for("buscar_estoque", id=id))
        flash("Estoque atualizado com sucesso.", "sucesso")
        return redirect(url_for("buscar_estoque", id=id))
    except Exception as e:
        flash("Erro ao atualizar estoque.", "erro")
        return render_template("estoque.html", estoque=dados)

# EXCLUIR ESTOQUE
@app.route("/estoque/<int:id>/excluir")
def excluir_estoque(id):
    try:
        estoque = Estoque.find_by_id(id)
        if not estoque:
            flash("Estoque não encontrado.", "erro")
            return redirect(url_for("listar_estoques"))
        Estoque.safe_delete(id)
        flash("Estoque excluído com sucesso.", "sucesso")
    except ValueError as e:
        flash(str(e), "erro")
    except Exception as e:
        flash("Erro ao excluir estoque.", "erro")
    return redirect(url_for("listar_estoques"))








#(itens entrada)============================================================================================
itens_entrada = []
# LISTAR ITENS DE ENTRADA
@app.route("/itens_entrada")
def listar_itens_entrada():
    return render_template("itens_entrada_lista.html", itens_entrada=itens_entrada)

# ABRIR FORMULÁRIO (NOVO ITEM)
@app.route("/item_entrada/novo")
def novo_item_entrada():
    return render_template("item_entrada.html", item_entrada=None)

# SALVAR ITEM DE ENTRADA
@app.route("/item_entrada/salvar", methods=["POST"])
def salvar_item_entrada():
    dados = get_item_entrada_form()
    item_entrada = ItemEntrada(**dados)
    erros = item_entrada.validate()
    if erros:
        for erro in erros:
            flash(erro, "erro")
        return render_template("item_entrada.html", item_entrada=dados)
    try:
        item_entrada.insert()
        flash("Item de entrada cadastrado com sucesso.", "sucesso")
        return redirect(url_for("listar_itens_entrada"))
    except Exception as e:
        flash(f"Erro ao cadastrar item de entrada: {e}", "erro")
        return render_template("item_entrada.html", item_entrada=dados)

# BUSCAR ITEM (EDITAR)
@app.route("/item_entrada/<int:id>/editar")
def buscar_item_entrada(id):
    item_entrada = next((i for i in itens_entrada if i["id"] == id), None)
    if not item_entrada:
        flash("Item não encontrado", "erro")
        return redirect(url_for("listar_itens_entrada"))
    return render_template("item_entrada.html", item_entrada=item_entrada)

# ATUALIZAR ITEM
@app.route("/item_entrada/atualizar/<int:id>", methods=["POST"])
def atualizar_item_entrada(id):
    dados = get_item_entrada_form()
    item_entrada = ItemEntrada(**dados)
    erros = item_entrada.validate()
    if erros:
        for erro in erros:
            flash(erro, "erro")
        dados["id"] = id
        return render_template("item_entrada.html", item_entrada=dados)
    try:
        if not ItemEntrada.find_by_id(id):
            flash("Item não encontrado.", "erro")
            return redirect(url_for("listar_itens_entrada"))
        item_entrada.update(id)
        flash("Item atualizado com sucesso.", "sucesso")
        return redirect(url_for("listar_itens_entrada"))
    except Exception as e:
        dados["id"] = id
        flash(f"Erro ao atualizar item: {e}", "erro")
        return render_template("item_entrada.html", item_entrada=dados)

# DELETAR ITEM
@app.route("/item_entrada/excluir/<int:id>")
def excluir_item_entrada(id):
    try:
        ItemEntrada.safe_delete(id)
        flash("Item excluído com sucesso.", "sucesso")
    except ValueError as e:
        flash(str(e), "erro")
    except Exception as e:
        flash(f"Erro ao excluir item: {e}", "erro")
    return redirect(url_for("listar_itens_entrada"))













#(itens saida)============================================================================================
itens_saida = []
# LISTAR ITENS DE SAÍDA
@app.route("/itens_saida")
def listar_itens_saida():
    return render_template("itens_saida_lista.html", itens_saida=itens_saida)

# ABRIR FORMULÁRIO (NOVO ITEM)
@app.route("/item_saida/novo")
def novo_item_saida():
    return render_template("item_saida.html", item_saida=None)

# SALVAR ITEM DE SAÍDA
@app.route("/item_saida/salvar", methods=["POST"])
def salvar_item_saida():
    dados = get_item_saida_form()
    item_saida = ItemSaida(**dados)
    erros = item_saida.validate()
    if erros:
        for erro in erros:
            flash(erro, "erro")
        return render_template("item_saida.html", item_saida=dados)
    try:
        item_saida.insert()
        flash("Item de saída cadastrado com sucesso.", "sucesso")
        return redirect(url_for("listar_itens_saida"))
    except Exception as e:
        flash(f"Erro ao cadastrar item de saída: {e}", "erro")
        return render_template("item_saida.html", item_saida=dados)

# BUSCAR ITEM (EDITAR)
@app.route("/item_saida/<int:id>/editar")
def buscar_item_saida(id):
    item_saida = next((i for i in itens_saida if i["id"] == id), None)
    if not item_saida:
        flash("Item não encontrado", "erro")
        return redirect(url_for("listar_itens_saida"))
    return render_template("item_saida.html", item_saida=item_saida)

# ATUALIZAR ITEM
@app.route("/item_saida/atualizar/<int:id>", methods=["POST"])
def atualizar_item_saida(id):
    dados = get_item_saida_form()
    item_saida = ItemSaida(**dados)
    erros = item_saida.validate()
    if erros:
        for erro in erros:
            flash(erro, "erro")
        dados["id"] = id
        return render_template("item_saida.html", item_saida=dados)
    try:
        if not ItemSaida.find_by_id(id):
            flash("Item não encontrado.", "erro")
            return redirect(url_for("listar_itens_saida"))
        item_saida.update(id)
        flash("Item atualizado com sucesso.", "sucesso")
        return redirect(url_for("listar_itens_saida"))
    except Exception as e:
        dados["id"] = id
        flash(f"Erro ao atualizar item: {e}", "erro")
        return render_template("item_saida.html", item_saida=dados)

# DELETAR ITEM
@app.route("/item_saida/excluir/<int:id>")
def excluir_item_saida(id):
    try:
        ItemSaida.safe_delete(id)
        flash("Item excluído com sucesso.", "sucesso")
    except ValueError as e:
        flash(str(e), "erro")
    except Exception as e:
        flash(f"Erro ao excluir item: {e}", "erro")
    return redirect(url_for("listar_itens_saida"))














#(Pedidos saida)============================================================================================
# FORMULÁRIO NOVO PEDIDO SAÍDA
@app.route("/pedido_saida/novo", methods=["GET"])
def novo_pedido_saida():
    return render_template("pedido_saida.html", pedidos_saida=None)

# LISTAR PEDIDOS SAÍDA
@app.route("/pedidos_saida", methods=["GET"])
def listar_pedidos_saida():
    try:
        pedidos_saida = PedidoSaida.find_all(order_by="id DESC")
        return render_template("pedido_saida_lista.html", pedidos_saida=pedidos_saida)
    except Exception as e:
        flash("Erro ao carregar pedidos de saída.", "erro")
        return render_template("pedido_saida_lista.html", pedidos_saida=[])

# SALVAR PEDIDO SAÍDA
@app.route("/pedido_saida/salvar", methods=["POST"])
def salvar_pedido_saida():
    dados = get_pedido_saida_form()
    pedido_saida = PedidoSaida(**dados)
    erros = pedido_saida.validate()
    if erros:
        for erro in erros:
            flash(erro, "erro")
        return render_template("pedido_saida.html", pedido_saida=pedido_saida)
    try:
        novo_id = pedido_saida.insert()
        flash("Pedido de saída cadastrado com sucesso.", "sucesso")
        return redirect(url_for('novo_pedido_saida', id=novo_id))
    except Exception as e:
        flash("Erro ao cadastrar pedido de saída.", "erro")
        return render_template("pedido_saida_lista.html", pedido_saida=pedido_saida)

# BUSCAR PEDIDO SAÍDA
@app.route("/pedido_saida/<int:id>/editar", methods=["GET"])
def buscar_pedido_saida(id):
    try:
        pedido_saida = PedidoSaida.find_by_id(id)
        if not pedido_saida:
            flash("Pedido de saída não encontrado.", "erro")
            return redirect(url_for('novo_pedido_saida'))
        return render_template("pedido_saida.html", pedido_saida=pedido_saida)
    except Exception as e:
        flash("Erro ao carregar pedido de saída.", "erro")
        return redirect(url_for('novo_pedido_saida'))

# ATUALIZAR PEDIDO SAÍDA
@app.route("/pedido_saida/<int:id>/atualizar", methods=["POST"])
def atualizar_pedido_saida(id):
    dados = get_pedido_saida_form()
    pedido_saida = PedidoSaida(**dados)
    erros = pedido_saida.validate()
    if erros:
        for erro in erros:
            flash(erro, "erro")
        dados["id"] = id
        return render_template("pedido_saida.html", pedido_saida=dados)
    try:
        pedido_saida_existente = PedidoSaida.find_by_id(id)
        if not pedido_saida_existente:
            flash("Pedido de saída não encontrado.", "erro")
            return redirect(url_for('novo_pedido_saida'))
        linhas_afetadas = pedido_saida.update(id)
        if linhas_afetadas == 0:
            flash("Nenhuma alteração realizada.", "erro")
            return redirect(url_for('novo_pedido_saida', id=id))
        flash("Pedido de saída atualizado com sucesso.", "sucesso")
        return redirect(url_for('novo_pedido_saida', id=id))
    except Exception as e:
        flash("Erro ao atualizar pedido de saída.", "erro")
        return render_template("pedido_saida.html", pedido_saida=dados)

# EXCLUIR PEDIDO SAÍDA
@app.route("/pedido_saida/<int:id>/excluir")
def excluir_pedido_saida(id):
    try:
        pedido_saida = PedidoSaida.find_by_id(id)
        if not pedido_saida:
            flash("Pedido de saída não encontrado.", "erro")
            return redirect(url_for('novo_pedido_saida'))
        PedidoSaida.safe_delete(id)
        flash("Pedido de saída excluído com sucesso.", "sucesso")
    except ValueError as e:
        flash(str(e), "erro")
    except Exception as e:
        flash("Erro ao excluir pedido de saída.", "erro")
    return redirect(url_for('novo_pedido_saida'))
if __name__=="__main__":
    print(app.url_map)
    app.run(debug=True)