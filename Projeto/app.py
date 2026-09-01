from flask import Flask, render_template, request, redirect, session, url_for, flash
from core.database import Database
from models.item_saida import ItemSaida
from models.localizaçao import Localizacao
from models.pedido_saida import PedidoSaida
from models.produto import Produto
from models.movimentacao import Movimentacao
from models.pedido_entrada import PedidoEntrada
from models.cliente import Cliente
from models.usuario import Usuario
from models.item_entrada import ItemEntrada
from core.security import login_obrigatorio

app = Flask(__name__)
app.secret_key = "chave_secreta"


@app.route("/")
def index():
    if "usuario_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_obrigatorio
def dashboard():
    return render_template("base.html")

def get_usuario_form(): 
    return {"nome": request.form.get("nome", "").strip(), 
            "email": request.form.get("email", "").strip(), 
            "senha": request.form.get("senha", "").strip(), 
            "identificacao": request.form.get("identificacao", "").strip(), 
            "tipo": request.form.get("tipo", "").strip() 
    }


def get_cliente_form():
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


def get_pedido_entrada_form():
    return {
        "numero_documento": request.form.get("numero_documento", "").strip(),
        "fornecedor": request.form.get("fornecedor", "").strip(),
        "data_entrada": request.form.get("data_entrada", "").strip(),
        "id_usuario": int(request.form.get("id_usuario", 0)),
        "observacao": request.form.get("observacao", "").strip(),
        "status": request.form.get("status", "").strip(),
    }


def get_login_form():
    return {
        "email": request.form.get("email", "").strip(),
        "senha": request.form.get("senha", "").strip(),
    }





def get_pedido_saida_form():
    return {
        "tipo": request.form.get("tipo", "").strip(),
        "pagamento": request.form.get("pagamento", "").strip(),
        "data_pagamento": request.form.get("data_pagamento", "").strip(),
        "cliente_id": int(request.form.get("cliente_id", 0)),
        "usuario_id": int(request.form.get("usuario_id", 0)),
    }


# (Login)===========================================================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    if "usuario_id" in session:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        senha = request.form.get("senha", "").strip()
        usuario = Usuario.autenticar(email, senha)
        if usuario:
            session["usuario_id"] = usuario["id"]
            session["usuario_nome"] = usuario["nome"]
            session["usuario_tipo"] = usuario["tipo"]
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for("dashboard"))
        flash("E-mail ou senha inválidos.", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Você saiu do sistema.", "info")
    return redirect(url_for("login"))


# (Cliente)===========================================================================================
# FORMULÁRIO NOVO CLIENTE
@app.route("/cliente/novo", methods=["GET"])
@login_obrigatorio
def novo_cliente():
    return render_template("Cliente.html", cliente=None)


# LISTAR CLIENTES
@app.route("/clientes", methods=["GET"])
@login_obrigatorio
def listar_clientes():
    try:
        clientes = Cliente.find_all(order_by="id DESC")
        return render_template("cliente_lista.html", clientes=clientes)
    except Exception as e:
        flash("Erro ao carregar clientes.", "erro")
        return render_template("cliente_lista.html", clientes=[])


# SALVAR CLIENTE
@app.route("/cliente/salvar", methods=["POST"])
@login_obrigatorio
def salvar_cliente():
    dados = get_cliente_form()
    dados["email"] = dados["email"].lower().strip()
    cliente = Cliente(**dados)
    erros = cliente.validate()
    if erros:
        for erro in erros:
            flash(erro, "erro")
        return render_template("Cliente.html", cliente=cliente)
    try:
        novo_id = cliente.insert()
        flash("Cliente cadastrado com sucesso.", "sucesso")
        return redirect(url_for("listar_clientes", id=novo_id))
    except Exception as e:
        print("ERRO REAL:", e)
        flash("Erro ao cadastrar cliente.", "erro")
        return render_template("cliente_lista.html", cliente=cliente)


# BUSCAR CLIENTE
@app.route("/cliente/<int:id>/editar", methods=["GET"])
@login_obrigatorio
def buscar_cliente(id):
    try:
        cliente = Cliente.find_by_id(id)
        if not cliente:
            flash("Cliente não encontrado.", "erro")
            return redirect(url_for("cliente_lista"))
        return render_template("Cliente.html", cliente=cliente)
    except Exception as e:
        flash("Erro ao carregar cliente.", "erro")
        return redirect(url_for("cliente_lista"))


# ATUALIZAR CLIENTE
@app.route("/cliente/<int:id>/atualizar", methods=["POST"])
@login_obrigatorio
def atualizar_cliente(id):
    dados = get_cliente_form()
    dados["email"] = dados["email"].lower().strip()
    cliente = Cliente(**dados)
    erros = cliente.validate()
    if erros:
        for erro in erros:
            flash(erro, "erro")
        dados["id"] = id
        return render_template("Cliente.html", cliente=dados)
    try:
        cliente_existente = Cliente.find_by_id(id)
        if not cliente_existente:
            flash("Cliente não encontrado.", "erro")
            return redirect(url_for("listar_clientes"))
        linhas_afetadas = cliente.update(id)
        if linhas_afetadas == 0:
            flash("Nenhuma alteração realizada.", "erro")
            return redirect(url_for("buscar_cliente", id=id))
        flash("Cliente atualizado com sucesso.", "sucesso")
        return redirect(url_for("buscar_cliente", id=id))
    except Exception as e:
        flash("Erro ao atualizar cliente.", "erro")
        return render_template("Cliente.html", cliente=dados)


# EXCLUIR CLIENTE
@app.route("/cliente/<int:id>/excluir")
@login_obrigatorio
def excluir_cliente(id):
    try:
        cliente = Cliente.find_by_id(id)
        if not cliente:
            flash("Cliente não encontrado.", "erro")
            return redirect(url_for("listar_clientes"))
        Cliente.safe_delete(id)
        flash("Cliente excluído com sucesso.", "sucesso")
    except ValueError as e:
        flash(str(e), "erro")
    except Exception as e:
        flash("Erro ao excluir cliente.", "erro")
    return redirect(url_for("listar_clientes"))


# (Produto)============================================================================================
# FORMULÁRIO NOVO PRODUTO
@app.route("/produto/novo", methods=["GET"])
@login_obrigatorio
def novo_produto():
    return render_template("produtos.html", produto=None)


# LISTAR PRODUTOS
@app.route("/produtos", methods=["GET"])
@login_obrigatorio
def listar_produtos():
    try:
        produtos = Produto.find_all(order_by="id DESC")
        return render_template("listar_produtos.html", produtos=produtos)
    except Exception as e:
        flash("Erro ao carregar produtos.", "erro")
        return render_template("listar_produtos.html", produtos=[])


# SALVAR PRODUTO
@app.route("/produto/salvar", methods=["POST"])
@login_obrigatorio
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
        movimentacao = Movimentacao(
            produto_id=novo_id, tipo_movimentacao="CADASTRO", quantidade=1
        )
        movimentacao.insert()
        flash("Produto cadastrado com sucesso.", "sucesso")
        return redirect(url_for("listar_produtos"))
    except Exception as e:
        flash(f"Erro ao cadastrar produto: {e}", "erro")
        print("TEMP")
        return render_template("produtos.html", produto=produto)


# BUSCAR PRODUTO
@app.route("/produto/<int:id>/editar", methods=["GET"])
@login_obrigatorio
def buscar_produto(id):
    try:
        produto = Produto.find_by_id(id)
        if not produto:
            flash("Produto não encontrado.", "erro")
            return redirect(url_for("listar_produtos"))
        return render_template("produtos.html", produto=produto)
    except Exception as e:
        flash("Erro ao carregar produto.", "erro")
        return redirect(url_for("listar_produtos"))


# ATUALIZAR PRODUTO
@app.route("/produto/<int:id>/atualizar", methods=["POST"])
@login_obrigatorio
def atualizar_produto(id):
    dados = get_produto_form()
    produto = Produto(**dados)
    erros = produto.validate()
    if erros:
        for erro in erros:
            flash(erro, "erro")
        dados["id"] = id
        return render_template("produtos.html", produto=dados)
    try:
        produto_existente = Produto.find_by_id(id)
        if not produto_existente:
            flash("Produto não encontrado.", "erro")
            return redirect(url_for("listar_produtos"))
        linhas_afetadas = produto.update(id)
        if linhas_afetadas == 0:
            flash("Nenhuma alteração realizada.", "erro")
            return redirect(url_for("buscar_produto", id=id))
        flash("Produto atualizado com sucesso.", "sucesso")
        return redirect(url_for("listar_produtos"))
    except Exception as e:
        flash("Erro ao atualizar produto.", "erro")
        return render_template("produtos.html", produto=dados)


# EXCLUIR PRODUTO
@app.route("/produto/<int:id>/excluir")
@login_obrigatorio
def excluir_produto(id):
    try:
        produto = Produto.find_by_id(id)
        if not produto:
            flash("Produto não encontrado.", "erro")
            return redirect(url_for("listar_produtos"))
        Produto.safe_delete(id)
        flash("Produto excluído com sucesso.", "sucesso")
    except Exception as e:
        flash(f"Erro ao excluir produto: {e}", "erro")
    return redirect(url_for("listar_produtos"))


# (Movimentação)===========================================================================================
@app.route("/movimentacoes")
@login_obrigatorio
def movimentacoes():
    movimentacoes = Movimentacao.find_all_with_product()
    movimentacoes_entrada = PedidoEntrada.listar_movimentacoes()
    movimentacoes_saida = PedidoSaida.listar_movimentacoes()
    return render_template(
        "movimentacoes.html",
        movimentacoes=movimentacoes,
        movimentacoes_entrada=movimentacoes_entrada,
        movimentacoes_saida=movimentacoes_saida,
    )


# (PedidoEntrada)===========================================================================================
# FORMULÁRIO NOVO PEDIDO ENTRADA
@app.route("/pedido_entrada/novo", methods=["GET"])
@login_obrigatorio
def novo_pedido_entrada():
    usuarios = Usuario.find_all(order_by="nome")
    return render_template(
        "pedido_entrada.html", pedido_entrada=None, usuarios=usuarios
    )


# LISTAR PEDIDOS DE ENTRADA
@app.route("/pedido_entrada", methods=["GET"])
@login_obrigatorio
def listar_pedido_entrada():
    try:
        pedidos_entrada = PedidoEntrada.find_all(order_by="id_pedido_entrada DESC")
        return render_template(
            "pedido_entrada_lista.html", pedidos_entrada=pedidos_entrada
        )
    except Exception as e:
        print("ERRO:", e)
        flash(f"Erro ao carregar pedidos de entrada: {e}", "erro")
        return render_template("pedido_entrada_lista.html", pedidos_entrada=[])


# SALVAR PEDIDO ENTRADA
@app.route("/pedido_entrada/salvar", methods=["POST"])
@login_obrigatorio
def salvar_pedido_entrada():
    dados = get_pedido_entrada_form()
    pedido_entrada = PedidoEntrada(**dados)
    erros = pedido_entrada.validate()
    if erros:
        for erro in erros:
            flash(erro, "erro")
        return render_template(
            "pedido_entrada.html",
            pedido_entrada=pedido_entrada,
            usuarios=Usuario.find_all(order_by="nome"),
            movimentacoes=[],
            itens=[],
        )
    try:
        novo_id = pedido_entrada.insert()
        flash("Pedido de entrada cadastrado com sucesso.", "sucesso")
        return redirect(url_for("buscar_pedido_entrada", id=novo_id))
    except Exception as e:
        flash(f"Erro ao cadastrar pedido: {e}", "erro")
        return render_template(
            "pedido_entrada.html",
            pedido_entrada=pedido_entrada,
            usuarios=Usuario.find_all(order_by="nome"),
            movimentacoes=[],
            itens=[],
        )


# BUSCA PEDIDO DE ENTRADA
@app.route("/pedido_entrada/<int:id>/editar")
@login_obrigatorio
def buscar_pedido_entrada(id):
    try:
        pedido_entrada = PedidoEntrada.find_by_id(id)
        if not pedido_entrada:
            flash("Pedido não encontrado.", "erro")
            return redirect(url_for("listar_pedido_entrada"))
        usuarios = Usuario.find_all(order_by="nome")
        movimentacoes = Movimentacao.find_all_with_product()
        itens = ItemEntrada.find_by_pedido(id)
        return render_template(
            "pedido_entrada.html",
            pedido_entrada=pedido_entrada,
            usuarios=usuarios,
            movimentacoes=movimentacoes,
            itens=itens,
        )
    except Exception as e:
        flash(f"Erro ao carregar pedido: {e}", "erro")
        return redirect(url_for("listar_pedido_entrada"))


# ATUALIZAR PEDIDO
@app.route("/pedido_entrada/<int:id>/atualizar", methods=["POST"])
@login_obrigatorio
def atualizar_pedido_entrada(id):
    dados = get_pedido_entrada_form()
    pedido_entrada = PedidoEntrada(**dados)
    erros = pedido_entrada.validate()
    if erros:
        for erro in erros:
            flash(erro, "erro")
        dados["id"] = id
        return render_template(
            "pedido_entrada.html",
            pedido_entrada=dados,
            usuarios=Usuario.find_all(order_by="nome"),
        )
    try:
        pedido_existente = PedidoEntrada.find_by_id(id)
        if not pedido_existente:
            flash("Pedido não encontrado.", "erro")
            return redirect(url_for("listar_pedido_entrada"))
        linhas_afetadas = pedido_entrada.update(id)
        if linhas_afetadas == 0:
            flash("Nenhuma alteração realizada.", "erro")
            return redirect(url_for("buscar_pedido_entrada", id=id))
        flash("Pedido atualizado com sucesso.", "sucesso")
        return redirect(url_for("listar_pedido_entrada"))
    except Exception:
        flash("Erro ao atualizar pedido.", "erro")
        return render_template(
            "pedido_entrada.html",
            pedido_entrada=dados,
            usuarios=Usuario.find_all(order_by="nome"),
        )


# EXCLUIR PEDIDO DE ENTRADA
@app.route("/pedido_entrada/<int:id>/excluir")
@login_obrigatorio
def excluir_pedido_entrada(id):
    try:
        pedido_entrada = PedidoEntrada.find_by_id(id)
        if not pedido_entrada:
            flash("Pedido de entrada não encontrado.", "erro")
            return redirect(url_for("listar_pedido_entrada"))
        PedidoEntrada.safe_delete(id)
        flash("Pedido de entrada excluído com sucesso.", "sucesso")
    except ValueError as e:
        flash(str(e), "erro")
    except Exception as e:
        flash("Erro ao excluir pedido de entrada.", "erro")
    return redirect(url_for("listar_pedido_entrada"))


# (Item Entrada)===========================================================================================
@app.route("/item_entrada/salvar", methods=["POST"])
@login_obrigatorio
def salvar_item_entrada():

    item = ItemEntrada(
        request.form.get("quantidade"),
        request.form.get("valor"),
        request.form.get("pedido_entrada_id"),
        request.form.get("movimentacao_id") or None,
    )
    erros = item.validate()
    if erros:
        for erro in erros:
            flash(erro, "erro")
        return redirect(
            url_for("buscar_pedido_entrada", id=request.form.get("pedido_entrada_id"))
        )
    try:
        item.insert()
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT produto_id
            FROM movimentacao
            WHERE id = %s
            """,
            (item.movimentacao_id,),
        )
        mov = cursor.fetchone()
        cursor.close()
        conexao.close()
        if mov:
            Produto.aumentar_estoque(mov["produto_id"], item.quantidade)
        flash("Item adicionado com sucesso.", "sucesso")
    except Exception as e:
        flash(f"Erro ao adicionar item: {e}", "erro")
    return redirect(
        url_for("buscar_pedido_entrada", id=request.form.get("pedido_entrada_id"))
    )


# (Localização)===========================================================================================
# (nova localização)
@app.route("/localizacao/novo")
@login_obrigatorio
def nova_localizacao():
    produtos = Produto.find_all()
    return render_template("localizacao.html", produtos=produtos)


# (Listar Localizações)
@app.route("/localizacao")
@login_obrigatorio
def listar_localizacao():
    localizacoes = Localizacao.find_all("id DESC")
    return render_template("listar_localizacao.html", localizacoes=localizacoes)


# (Salvar Localização)
@app.route("/localizacao/salvar", methods=["POST"])
@login_obrigatorio
def salvar_localizacao():

    localizacao = Localizacao(
        request.form["rua"], request.form["numero"], request.form["andar"]
    )
    erros = localizacao.validate()
    if erros:
        for erro in erros:
            flash(erro, "erro")
        return redirect(url_for("nova_localizacao"))
    try:
        localizacao_id = localizacao.insert()
        produto_id = request.form["produto_id"]
        conexao = Database.connect()
        cursor = conexao.cursor()
        cursor.execute(
            """
            UPDATE produto
            SET localizacao_id = %s
            WHERE id = %s
            """,
            (localizacao_id, produto_id),
        )
        conexao.commit()
        cursor.close()
        conexao.close()
        flash("Localização cadastrada com sucesso.", "sucesso")
    except Exception as e:
        flash(f"Erro ao cadastrar localização: {e}", "erro")
    return redirect(url_for("listar_localizacao"))


# (Pedido de Saída)============================================================================================
@app.route("/pedido_saida/novo")
@login_obrigatorio
def novo_pedido_saida():
    clientes = Cliente.find_all(order_by="nome")
    usuarios = Usuario.find_all(order_by="nome")
    produtos = Produto.find_all_com_localizacao()
    return render_template(
        "pedido_saida.html",
        pedido_saida=None,
        clientes=clientes,
        usuarios=usuarios,
        produtos=produtos,
        itens=[],
    )


# (Listar Pedidos de Saída)
@app.route("/pedido_saida", methods=["GET"])
@login_obrigatorio
def listar_pedido_saida():
    try:
        pedidos_saida = PedidoSaida.listar_pedidos()
        return render_template("pedido_saida_lista.html", pedidos_saida=pedidos_saida)
    except Exception as e:
        flash(f"Erro ao carregar pedidos: {e}", "erro")
        return render_template("pedido_saida_lista.html", pedidos_saida=[])


# (Buscar Pedido de Saída)
# BUSCAR PEDIDO DE SAÍDA
@app.route("/pedido_saida/<int:id>/editar")
@login_obrigatorio
def buscar_pedido_saida(id):

    try:
        pedido_saida = PedidoSaida.find_by_id(id)
        if not pedido_saida:
            flash("Pedido de saída não encontrado.", "erro")
            return redirect(url_for("listar_pedido_saida"))
        clientes = Cliente.find_all(order_by="nome")
        usuarios = Usuario.find_all(order_by="nome")
        produtos = Produto.find_all_com_localizacao()
        itens = ItemSaida.find_by_pedido(id)
        return render_template(
            "pedido_saida.html",
            pedido_saida=pedido_saida,
            clientes=clientes,
            usuarios=usuarios,
            produtos=produtos,
            itens=itens,
        )
    except Exception as e:
        flash(f"Erro ao carregar pedido: {e}", "erro")
        return redirect(url_for("listar_pedido_saida"))


# (Atualizar peido de saida)
@app.route("/pedido_saida/<int:id>/atualizar", methods=["POST"])
@login_obrigatorio
def atualizar_pedido_saida(id):

    pedido_saida = PedidoSaida(
        request.form["tipo"],
        request.form["pagamento"],
        request.form["quantidade"],
        request.form["valor"],
        request.form["data_pagamento"],
        request.form["cliente_id"],
        request.form["usuario_id"],
    )
    erros = pedido_saida.validate()
    if erros:
        for erro in erros:
            flash(erro, "erro")
        return redirect(url_for("buscar_pedido_saida", id=id))
    try:
        pedido_saida.update(id)
        flash("Pedido de saída atualizado com sucesso.", "sucesso")
    except Exception as e:
        flash(f"Erro ao atualizar pedido: {e}", "erro")
    return redirect(url_for("buscar_pedido_saida", id=id))


# (salvar Pedido de Saída)
@app.route("/pedido_saida/salvar", methods=["POST"])
@login_obrigatorio
def salvar_pedido_saida():
    dados = get_pedido_saida_form()
    pedido_saida = PedidoSaida(**dados)
    erros = pedido_saida.validate()
    if erros:
        for erro in erros:
            flash(erro, "erro")
        return render_template(
            "pedido_saida.html",
            pedido_saida=pedido_saida,
            clientes=Cliente.find_all(order_by="nome"),
            usuarios=Usuario.find_all(order_by="nome"),
            movimentacoes=[],
            itens=[],
        )
    try:
        novo_id = pedido_saida.insert()
        flash("Pedido de saída cadastrado com sucesso.", "sucesso")
        return redirect(url_for("buscar_pedido_saida", id=novo_id))
    except Exception as e:
        flash(f"Erro ao cadastrar pedido: {e}", "erro")
        return render_template(
            "pedido_saida.html",
            pedido_saida=pedido_saida,
            clientes=Cliente.find_all(order_by="nome"),
            usuarios=Usuario.find_all(order_by="nome"),
            movimentacoes=[],
            itens=[],
        )


# (Excluir Pedido de Saída)
@app.route("/pedido_saida/<int:id>/excluir")
@login_obrigatorio
def excluir_pedido_saida(id):
    try:
        PedidoSaida.safe_delete(id)
        flash("Pedido excluído com sucesso.", "sucesso")
    except Exception as e:
        flash(f"Erro ao excluir pedido: {e}", "erro")
    return redirect(url_for("listar_pedido_saida"))


# (Salvar Item de Saída)============================================================================================
@app.route("/item_saida/salvar", methods=["POST"])
@login_obrigatorio
def salvar_item_saida():
    item = ItemSaida(
        request.form["quantidade"],
        request.form["valor"],
        request.form["pedido_saida_id"],
        request.form["produto_id"],
    )
    erros = item.validate()
    if erros:
        for erro in erros:
            flash(erro, "erro")
        return redirect(
            url_for("buscar_pedido_saida", id=request.form["pedido_saida_id"])
        )

    try:
        Produto.diminuir_estoque(item.produto_id, item.quantidade)
        item.insert()
        movimentacao = Movimentacao(
            produto_id=item.produto_id,
            tipo_movimentacao="SAIDA",
            quantidade=item.quantidade,
        )
        movimentacao.insert()
        flash("Item de saída adicionado com sucesso.", "sucesso")
    except Exception as e:
        flash(str(e), "erro")
    return redirect(url_for("listar_produtos"))

if __name__ == "__main__":
    app.run(debug=True)
    print(app.url_map)