from flask import Flask, render_template, request, redirect, url_for, flash
from models.produto import Produto
from models.movimentacao import movimentacao
#from models.pedido_movimentacao import Pedidos
from models.localizaçao import Localizacao
from models.item_saida import ItemSaida
from models.item_entrada import ItemEntrada
#from models.fornecedor import Fornecedor
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

def get_produto_form():
    return {
        "nome": request.form.get("nome", "").strip(),
        "descricao": request.form.get("descricao", "").strip(),
        "categoria": request.form.get("categoria", "").strip(),
        "unidade_medida": request.form.get("unidade_medida", "").strip(),
        "quantidade": to_int(request.form.get("quantidade")),
        "estoque_minimo": to_int(request.form.get("estoque_minimo")),
    }
    
#(Cliente)
@app.route("/cliente/novo")
def novo_cliente():
    return render_template("cliente.html", cliente=None)
@app.route("/clientes") #Listar Clientes
def listar_clientes():
    try:
        clientes = Cliente.find_all()
        return render_template(
            "clientes_lista.html",
            clientes=clientes
        )
    except Exception as e:
        flash(f"Erro ao carregar clientes: {e}", "erro")
        return render_template(
        "clientes_lista.html",
        clientes=[]
    )
@app.route("/cliente/salvar", methods=["POST"]) #Salvar Clientes
def salvar_cliente():
    dados = get_cliente_form()
    cliente = Cliente(**dados)
    erros = cliente.validate()
    if erros:
        for erro in erros:
            flash(erro, "erro")
        return render_template("cliente.html", cliente=dados)
    try:
        cliente.insert()
        flash("Cliente cadastrado com sucesso.", "sucesso")
        return redirect(url_for("listar_clientes"))
    except Exception as e:
        flash(f"Erro ao cadastrar cliente: {e}", "erro")
        return render_template("cliente.html", cliente=dados)
@app.route("/cliente/<int:id>/editar") #Buscar Cliente
def buscar_cliente(id):
    cliente = Cliente.find_by_id(id)
    if not cliente:
        flash("Cliente não encontrado", "erro")
        return redirect(url_for("listar_clientes"))
    return render_template(
        "cliente.html",
        cliente=cliente
    )
@app.route("/cliente/atualizar/<int:id>", methods=["POST"]) #Atualizar Cliente
def atualizar_cliente(id):
    dados = get_cliente_form()
    cliente = Cliente(**dados)
    erros = cliente.validate()
    if erros:
        for erro in erros:
            flash(erro, "erro")
        dados["id"] = id
        return render_template("cliente.html", cliente=dados)
    try:
        if not Cliente.find_by_id(id):
            flash("Cliente não encontrado.", "erro")
            return redirect(url_for("listar_clientes"))
        cliente.update(id)
        flash("Cliente atualizado com sucesso.", "sucesso")
        return redirect(url_for("listar_clientes"))
    except Exception as e:
        dados["id"] = id
        flash(f"Erro ao atualizar cliente: {e}", "erro")
        return render_template("cliente.html", cliente=dados)
@app.route("/cliente/excluir/<int:id>", methods=["POST"])# Excluir Cliente
def excluir_cliente(id):
    try:
        Cliente.safe_delete(id)
        flash("Cliente excluído com sucesso.", "sucesso")
    except ValueError as e:
        flash(str(e), "erro")
    except Exception as e:
        flash(f"Erro ao excluir cliente: {e}", "erro")
    return redirect(url_for("listar_clientes"))

#(Produto)
@app.route("/produto/novo")
def novo_produto():
    return render_template("base.html", produto=None)
@app.route("/produtos")  # Listar Produtos
def listar_produtos():
    try:
        produtos = Produto.find_all()
        return render_template(
            "produtos_lista.html",
            produtos=produtos
        )
    except Exception as e:
        flash(f"Erro ao carregar produtos: {e}", "erro")
        return render_template(
            "produtos_lista.html",
            produtos=[]
        )
@app.route("/produto/salvar", methods=["GET"])  # Salvar Produto
def salvar_produto():
    dados = get_produto_form()
    produto = Produto(**dados)
    erros = produto.validate()
    if erros:
        for erro in erros:
            flash(erro, "erro")
        return render_template(
            "produto.html",
            produto=dados
        )
    try:
        produto.insert()
        flash("Produto cadastrado com sucesso.", "sucesso")
        return redirect(url_for("listar_produtos"))
    except Exception as e:
        flash(f"Erro ao cadastrar produto: {e}", "erro")
        return render_template(
            "produto.html",
            produto=dados
        )
@app.route("/produto/<int:id>/editar", methods=["GET"])  # Buscar Produto
def buscar_produto(id):
    produto = Produto.find_by_id(id)
    if not produto:
        flash("Produto não encontrado", "erro")
        return redirect(url_for("listar_produtos"))
    return render_template(
        "produto.html",
        produto=produto
    )
@app.route("/produto/atualizar/<int:id>", methods=["PUT"]) # Atualizar Produto
def atualizar_produto(id):
    dados = get_produto_form()
    produto = Produto(**dados)
    erros = produto.validate()
    if erros:
        for erro in erros:
            flash(erro, "erro")
        dados["id"] = id
        return render_template(
            "produto.html",
            produto=dados
        )
    try:
        if not Produto.find_by_id(id):
            flash("Produto não encontrado.", "erro")
            return redirect(url_for("listar_produtos"))
        produto.update(id)
        flash("Produto atualizado com sucesso.", "sucesso")
        return redirect(url_for("listar_produtos"))
    except Exception as e:
        dados["id"] = id
        flash(f"Erro ao atualizar produto: {e}", "erro")
        return render_template(
            "produto.html",
            produto=dados
        )
@app.route("/produto/excluir/<int:id>", methods=["DELETE"])# Excluir Produto
def excluir_produto(id):
    try:
        Produto.safe_delete(id)
        flash("Produto excluído com sucesso.", "sucesso")
    except ValueError as e:
        flash(str(e), "erro")
    except Exception as e:
        flash(f"Erro ao excluir produto: {e}", "erro")
    return redirect(url_for("listar_produtos"))
if __name__=="__main__":
    app.run(debug=True)