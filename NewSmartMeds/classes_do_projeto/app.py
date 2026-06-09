from flask import Flask, render_template, request, redirect, session, url_for, flash
from models.produto import Produto
from models.movimentacao import Movimentacao
#from models.pedido_movimentacao import Pedidos
#from models.item_entrada import ItemEntrada
from models.fornecedor import Fornecedor
from models.cliente import Cliente


app = Flask(__name__)
app.secret_key = "chave_secreta"

@app.route("/")
def index():
    return render_template("login.html")

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
def get_login_form():
    return {
        "nome": request.form.get("nome", "").strip(),
        "email": request.form.get("email", "").strip(),
    }

#(Login)===========================================================================================
# FORMULÁRIO DE LOGIN
@app.route("/login", methods=["GET"])
def login():
    return render_template("login.html",usuario=None)

    
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
            flash("Cliente não encontrado.","erro")
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
        movimentacao = Movimentacao(produto_id=novo_id,tipo_movimentacao="CADASTRO",quantidade=1)
        movimentacao.insert()
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
    except Exception as e:
        flash(f"Erro ao excluir produto: {e}", "erro")
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
@app.route("/fornecedor/<int:id>/editar", methods=["GET"])
def buscar_fornecedor(id):
    try:
        fornecedor = Fornecedor.find_by_id(id)
        if not fornecedor:
            flash("Fornecedor não encontrado.","erro")
            return redirect(url_for("listar_fornecedor"))
        return render_template("fornecedor.html",fornecedor=fornecedor)
    except Exception:
        flash("Erro ao carregar fornecedor.","erro")
        return redirect(url_for("listar_fornecedor"))

# ATUALIZAR FORNECEDOR
@app.route("/fornecedor/<int:id>/atualizar",methods=["POST"])
def atualizar_fornecedor(id):
    dados = get_fornecedor_form()
    dados["email"] = (dados["email"].lower().strip())
    fornecedor = Fornecedor(**dados)
    erros = fornecedor.validate()
    if erros:
        for erro in erros:
            flash(erro, "erro")
        dados["id"] = id
        return render_template("fornecedor.html",fornecedor=dados)
    try:
        fornecedor_existente = (Fornecedor.find_by_id(id))
        if not fornecedor_existente:
            flash("Fornecedor não encontrado.","erro")
            return redirect(url_for("listar_fornecedor"))
        linhas_afetadas = fornecedor.update(id)
        if linhas_afetadas == 0:
            flash("Nenhuma alteração realizada.","erro")
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



#(Movimentação)===========================================================================================
@app.route("/movimentacoes")
def movimentacoes():
    dados = Movimentacao.find_all_with_product()
    print("DADOS:", dados)
    return render_template("movimentacoes.html",movimentacoes=dados)
if __name__=="__main__":
    app.run(debug=True)

       #print(app.url_map)