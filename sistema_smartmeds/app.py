from datetime import date, datetime, timedelta
import os
from flask import Flask, jsonify, render_template, request, redirect, session, url_for, flash
from core.database import Database
from models.item_saida import ItemSaida
from models.localizacao import Localizacao
from models.pedido_saida import PedidoSaida
from models.produto import Produto
from models.movimentacao import Movimentacao
from models.pedido_entrada import PedidoEntrada
from models.cliente import Cliente
from models.usuario import Usuario
from core.permissoes import permissao_obrigatoria
from models.item_entrada import ItemEntrada
from core.security import login_obrigatorio
from config import FLASK_SECRET_KEY, MQTT_BROKER, MQTT_TOPIC, SENSOR_TEMP_MIN, SENSOR_TEMP_MAX
from iot.sensor_leitura import SensorLeitura
from iot.mqtt_manager import mqtt_manager
import atexit
import threading

LIMITE_ESTOQUE_BAIXO = 50  # Produtos com menos de 50 unidades entram no alerta de estoque baixo.

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")

_iot_lock = threading.Lock()
_iot_tentado = False
_schema_lock = threading.Lock()
_coluna_refrigeracao_ok = False
_erro_migracao_refrigeracao_registrado = False


def garantir_coluna_refrigeracao():
    """Garante a coluna usada pelo cadastro de produtos em bancos antigos.

    A alteração é aditiva: cria somente a coluna ausente, com valor padrão 0,
    sem apagar nem modificar os produtos já cadastrados. Se o usuário do banco
    não tiver permissão ALTER, o erro fica registrado no log e há uma migração
    SQL manual em migracao_produtos_refrigerados.sql.
    """
    global _coluna_refrigeracao_ok, _erro_migracao_refrigeracao_registrado

    if _coluna_refrigeracao_ok:
        return True

    with _schema_lock:
        if _coluna_refrigeracao_ok:
            return True

        conexao = None
        cursor = None
        try:
            conexao = Database.connect()
            cursor = conexao.cursor()
            cursor.execute(
                """SELECT COUNT(*)
                   FROM information_schema.tables
                   WHERE table_schema = DATABASE() AND table_name = 'produto'"""
            )
            tabela_existe = cursor.fetchone()[0] > 0
            if not tabela_existe:
                # O banco pode ainda não ter recebido o esquema inicial.
                return False

            cursor.execute(
                """SELECT COUNT(*)
                   FROM information_schema.columns
                   WHERE table_schema = DATABASE()
                     AND table_name = 'produto'
                     AND column_name = 'precisa_temperatura_baixa'"""
            )
            coluna_existe = cursor.fetchone()[0] > 0

            if not coluna_existe:
                cursor.execute(
                    """ALTER TABLE produto
                       ADD COLUMN precisa_temperatura_baixa TINYINT(1)
                       NOT NULL DEFAULT 0 AFTER quantidade"""
                )
                conexao.commit()
                app.logger.warning(
                    "Migração automática: coluna produto.precisa_temperatura_baixa criada."
                )

            _coluna_refrigeracao_ok = True
            _erro_migracao_refrigeracao_registrado = False
            return True
        except Exception:
            if not _erro_migracao_refrigeracao_registrado:
                app.logger.exception(
                    "Não foi possível preparar a coluna de refrigeração. "
                    "Confira as permissões do MySQL e execute "
                    "migracao_produtos_refrigerados.sql no banco configurado."
                )
                _erro_migracao_refrigeracao_registrado = True
            return False
        finally:
            if cursor:
                cursor.close()
            if conexao:
                conexao.close()


def iniciar_integracao_iot():
    global _iot_tentado
    if _iot_tentado:
        return
    with _iot_lock:
        if _iot_tentado:
            return
        try:
            SensorLeitura.criar_tabela()
            mqtt_manager.start()
            _iot_tentado = True
        except Exception as erro:
            print(f"Aviso: integração IoT indisponível: {erro}")


@app.before_request
def preparar_iot():
    # Atualiza bancos antigos antes de qualquer rota consultar/salvar produtos.
    garantir_coluna_refrigeracao()
    iniciar_integracao_iot()


atexit.register(mqtt_manager.stop)


@app.route("/")
def index():
    if "usuario_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_obrigatorio
def dashboard():
    user_id = session.get("usuario_id")
    DIAS_ALERTA_VALIDADE = 30

    produtos = Produto.find_all(usuario_id=user_id)
    movimentacoes = (
        Movimentacao.find_all_with_product(usuario_id=user_id)
        if hasattr(Movimentacao, "find_all_with_product")
        else Movimentacao.find_all(usuario_id=user_id)
    )
    clientes = Cliente.find_all(usuario_id=user_id)

    hoje = date.today()
    limite_validade = hoje + timedelta(days=DIAS_ALERTA_VALIDADE)
    produtos_baixo = sorted(
        (p for p in produtos if int(p.get("quantidade") or 0) < LIMITE_ESTOQUE_BAIXO),
        key=lambda p: int(p.get("quantidade") or 0),
    )
    produtos_vencendo = [
        p for p in produtos
        if p.get("data_de_validade")
        and hoje <= p["data_de_validade"] <= limite_validade
    ]

    entradas = sum(
        1 for m in movimentacoes
        if (m.get("tipo") or m.get("tipo_movimentacao") or "").upper() == "ENTRADA"
    )
    saidas = sum(
        1 for m in movimentacoes
        if (m.get("tipo") or m.get("tipo_movimentacao") or "").upper() in {"SAIDA", "SAÍDA"}
    )

    produtos_ordenados = sorted(
        produtos, key=lambda p: int(p.get("quantidade") or 0), reverse=True
    )[:8]

    try:
        sensores = SensorLeitura.dispositivos_temperatura()
    except Exception as erro:
        print(f"Erro ao carregar sensores no dashboard: {erro}")
        sensores = []

    for sensor in sensores:
        temperatura = sensor.get("temperatura")
        sensor["temp_min"] = SENSOR_TEMP_MIN
        sensor["temp_max"] = SENSOR_TEMP_MAX
        sensor["status"] = (
            "critico"
            if temperatura is not None and (temperatura < SENSOR_TEMP_MIN or temperatura > SENSOR_TEMP_MAX)
            else "normal"
        )
        sensor["produtos_armazenados"] = 0

    alertas_temperatura = [s for s in sensores if s["status"] == "critico"]

    return render_template(
        "index.html",
        total_produtos=len(produtos),
        total_clientes=len(clientes),
        total_movimentacoes=len(movimentacoes),
        produtos_baixo=produtos_baixo,
        produtos_vencendo=produtos_vencendo,
        entradas=entradas,
        saidas=saidas,
        movimentacoes_recentes=movimentacoes[:6],
        labels_estoque=[p["nome"] for p in produtos_ordenados],
        quantidades_estoque=[int(p.get("quantidade") or 0) for p in produtos_ordenados],
        sensores_temperatura=sensores,
        alertas_temperatura=alertas_temperatura,
        iot_conectado=mqtt_manager.conectado,
        limite_estoque_baixo=LIMITE_ESTOQUE_BAIXO,
    )


# (Form Helpers)=====================================================================================
def get_cliente_form():
    return {
        "nome": request.form.get("nome", "").strip(),
        "email": request.form.get("email", "").strip(),
        "senha": request.form.get("senha", "").strip(),
        "cnpj": request.form.get("cnpj", "").strip(),
        "usuario_id": session.get("usuario_id"),
    }


def get_produto_form():
    qtd_str = request.form.get("quantidade", "0").strip()
    unidade = request.form.get("unidade_medida", "").strip() or "Unidade"
    try:
        quantidade = int(qtd_str)
    except (TypeError, ValueError):
        quantidade = -1

    refrigeracao_raw = request.form.get("precisa_temperatura_baixa", "0").strip()
    try:
        precisa_temperatura_baixa = int(refrigeracao_raw)
    except (TypeError, ValueError):
        precisa_temperatura_baixa = -1

    return {
        "nome": request.form.get("nome", "").strip(),
        "marca": request.form.get("marca", "").strip(),
        "data_de_validade": request.form.get("data_de_validade", "").strip(),
        "especificacao": request.form.get("especificacao", "").strip(),
        "unidade_medida": unidade,
        "quantidade": quantidade,
        "precisa_temperatura_baixa": precisa_temperatura_baixa,
        "usuario_id": session.get("usuario_id"),
    }



def get_pedido_entrada_form():
    return {
        "numero_documento": request.form.get("numero_documento", "").strip(),
        "fornecedor": request.form.get("fornecedor", "").strip(),
        "data_entrada": request.form.get("data_entrada", "").strip(),
        "usuario_id": session.get("usuario_id"),
        "observacao": request.form.get("observacao", "").strip(),
        "status": request.form.get("status", "").strip(),
    }


def get_login_form():
    return {
        "email": request.form.get("email", "").strip(),
        "senha": request.form.get("senha", "").strip(),
    }


def get_pedido_saida_form():
    cliente_raw = request.form.get("cliente_id", "").strip()
    qtd_raw = request.form.get("quantidade", "").strip()
    valor_raw = request.form.get("valor", "").strip().replace(",", ".")

    try:
        cliente_id = int(cliente_raw) if cliente_raw.isdigit() and int(cliente_raw) > 0 else None
    except (TypeError, ValueError):
        cliente_id = None
    try:
        quantidade = int(qtd_raw) if qtd_raw else None
    except (TypeError, ValueError):
        quantidade = None
    try:
        valor = float(valor_raw) if valor_raw else None
    except (TypeError, ValueError):
        valor = None

    return {
        "tipo": request.form.get("tipo", "").strip(),
        "pagamento": request.form.get("pagamento", "").strip(),
        "cliente_id": cliente_id,
        # Nunca confiar no usuário enviado por um campo oculto ou seletor HTML.
        "usuario_id": session.get("usuario_id"),
        "quantidade": quantidade,
        "valor": valor,
        "data_pagamento": request.form.get("data_pagamento", "").strip(),
    }



def get_usuario_form():
    return {
        "nome": request.form.get("nome", "").strip(),
        "email": request.form.get("email", "").strip(),
        "senha": request.form.get("senha", "").strip(),
        "identificacao": request.form.get("identificacao", "").strip(),
        "tipo": request.form.get("tipo", "").strip(),
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
            session.clear()
            session["usuario_id"] = usuario["id"]
            session["usuario_nome"] = usuario["nome"]
            session["usuario_tipo"] = usuario["tipo"]
            flash("Login realizado com sucesso!", "sucesso")
            return redirect(url_for("dashboard"))
        flash("E-mail ou senha inválidos.", "erro")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Você saiu do sistema.", "info")
    return redirect(url_for("login"))


# (Permissões e Usuário)=============================================================================
PERMISSOES = {
    "adm": {
        "usuarios_ver",
        "usuarios_criar",
        "usuarios_editar",
        "usuarios_excluir",
        "clientes_ver",
        "clientes_criar",
        "clientes_editar",
        "clientes_excluir",
        "produtos_ver",
        "produtos_criar",
        "produtos_editar",
        "produtos_excluir",
        "estoque_ver",
        "estoque_editar",
        "pedido_entrada",
        "pedido_saida",
        "localizacoes_ver",
        "localizacoes_criar",
        "localizacoes_editar",
        "localizacoes_excluir",
    },
    "estoquista": {
        "clientes_ver",
        "produtos_ver",
        "produtos_criar",
        "produtos_editar",
        "estoque_ver",
        "estoque_editar",
        "pedido_entrada",
        "pedido_saida",
        "localizacoes_ver",
    },
    "consulta": {
        "clientes_ver",
        "produtos_ver",
        "estoque_ver",
        "localizacoes_ver",
    },
}


def obter_usuario_logado():
    usuario_id = session.get("usuario_id")
    if not usuario_id:
        return None
    try:
        return Usuario.find_by_id(usuario_id)
    except Exception as e:
        print(f"Erro ao buscar usuário logado: {e}")
        return None


def tem_permissao(permissao):
    usuario = obter_usuario_logado()
    if not usuario:
        return False
    tipo = usuario.get("tipo")
    if tipo == "admin":
        tipo = "adm"
    return permissao in PERMISSOES.get(tipo, set())


@app.context_processor
def inject_permissoes():
    return {"usuario_logado": obter_usuario_logado(), "tem_permissao": tem_permissao}


# (Rotas Usuário)===================================================================================
@app.route("/usuarios", methods=["GET"])
@login_obrigatorio
@permissao_obrigatoria("usuarios_ver")
def listar_usuarios():
    try:
        usuarios = Usuario.find_all(order_by="id DESC")
        return render_template("usuario_lista.html", usuarios=usuarios)
    except Exception as e:
        print("ERRO AO LISTAR USUÁRIOS:", e)
        flash("Erro ao carregar usuários.", "erro")
        return render_template("usuario_lista.html", usuarios=[])


@app.route("/usuario/novo", methods=["GET"])
@login_obrigatorio
@permissao_obrigatoria("usuarios_criar")
def novo_usuario():
    return render_template("usuario.html", usuario={})


@app.route("/usuario/salvar", methods=["POST"])
@login_obrigatorio
@permissao_obrigatoria("usuarios_criar")
def salvar_usuario():
    dados = get_usuario_form()
    usuario = Usuario(**dados)
    erros = usuario.validate()
    confirmacao = request.form.get("confirmar_senha", "")
    if dados["senha"] != confirmacao:
        erros.append("A confirmação da senha não corresponde.")

    if erros:
        for erro in erros:
            flash(erro, "erro")
        return render_template("usuario.html", usuario=dados)

    try:
        usuario.insert()
        flash("Usuário cadastrado com sucesso.", "sucesso")
        return redirect(url_for("listar_usuarios"))
    except Exception as erro:
        app.logger.exception("Erro ao cadastrar usuário")
        flash("Não foi possível cadastrar o usuário. Verifique se o e-mail já existe.", "erro")
        return render_template("usuario.html", usuario=dados)




@app.route("/usuario/<int:id>/editar", methods=["GET"])
@login_obrigatorio
@permissao_obrigatoria("usuarios_editar")
def buscar_usuario(id):
    try:
        usuario = Usuario.find_by_id(id)
        if not usuario:
            flash("Usuário não encontrado.", "erro")
            return redirect(url_for("listar_usuarios"))
        return render_template("usuario.html", usuario=usuario)
    except Exception as e:
        print("ERRO AO BUSCAR USUÁRIO:", e)
        flash("Erro ao carregar usuário.", "erro")
        return redirect(url_for("listar_usuarios"))


@app.route("/usuario/<int:id>/atualizar", methods=["POST"])
@login_obrigatorio
@permissao_obrigatoria("usuarios_editar")
def atualizar_usuario(id):
    dados = get_usuario_form()
    usuario = Usuario(**dados)
    erros = usuario.validate(exigir_senha=False)
    confirmacao = request.form.get("confirmar_senha", "")
    if dados["senha"] and dados["senha"] != confirmacao:
        erros.append("A confirmação da senha não corresponde.")

    try:
        usuario_existente = Usuario.find_by_id(id)
        if not usuario_existente:
            flash("Usuário não encontrado.", "erro")
            return redirect(url_for("listar_usuarios"))
        if erros:
            for erro in erros:
                flash(erro, "erro")
            dados["id"] = id
            return render_template("usuario.html", usuario=dados)

        linhas_afetadas = usuario.update(id)
        if linhas_afetadas == 0:
            flash("Nenhuma alteração realizada.", "info")
        else:
            flash("Usuário atualizado com sucesso.", "sucesso")
        return redirect(url_for("listar_usuarios"))
    except Exception:
        app.logger.exception("Erro ao atualizar usuário")
        flash("Não foi possível atualizar o usuário. Verifique se o e-mail já existe.", "erro")
        dados["id"] = id
        return render_template("usuario.html", usuario=dados)




@app.route("/usuario/<int:id>/excluir", methods=["POST"])
@login_obrigatorio
@permissao_obrigatoria("usuarios_excluir")
def excluir_usuario(id):
    try:
        usuario = Usuario.find_by_id(id)
        if not usuario:
            flash("Usuário não encontrado.", "erro")
            return redirect(url_for("listar_usuarios"))

        if id == session.get("usuario_id"):
            raise ValueError("Você não pode excluir o usuário que está conectado.")
        Usuario.safe_delete(id)
        flash("Usuário excluído com sucesso.", "sucesso")
    except ValueError as e:
        flash(str(e), "erro")
    except Exception as e:
        print("ERRO AO EXCLUIR USUÁRIO:", e)
        flash("Erro ao excluir usuário.", "erro")

    return redirect(url_for("listar_usuarios"))


# (Cliente)===========================================================================================
@app.route("/cliente/novo", methods=["GET"])
@login_obrigatorio
@permissao_obrigatoria("clientes_criar")
def novo_cliente():
    return render_template("cliente.html", cliente={})


@app.route("/clientes", methods=["GET"])
@login_obrigatorio
@permissao_obrigatoria("clientes_ver")
def listar_clientes():
    user_id = session.get("usuario_id")
    try:
        clientes = Cliente.find_all(usuario_id=user_id, order_by="id DESC")
        return render_template("cliente_lista.html", clientes=clientes)
    except Exception as e:
        flash("Erro ao carregar clientes.", "erro")
        return render_template("cliente_lista.html", clientes=[])


@app.route("/cliente/salvar", methods=["POST"])
@login_obrigatorio
@permissao_obrigatoria("clientes_criar")
def salvar_cliente():
    dados = get_cliente_form()
    dados["email"] = dados["email"].lower().strip()
    cliente = Cliente(**dados)
    erros = cliente.validate()
    if dados["senha"] != request.form.get("confirmar_senha", ""):
        erros.append("A confirmação da senha não corresponde.")
    if erros:
        for erro in erros:
            flash(erro, "erro")
        return render_template("cliente.html", cliente=cliente)

    try:
        cliente.insert()
        flash("Cliente cadastrado com sucesso.", "sucesso")
        return redirect(url_for("listar_clientes"))
    except Exception:
        app.logger.exception("Erro ao cadastrar cliente")
        flash("Não foi possível cadastrar o cliente. Verifique se o e-mail ou CNPJ já existe.", "erro")
        return render_template("cliente.html", cliente=cliente)




@app.route("/cliente/<int:id>/editar", methods=["GET"])
@login_obrigatorio
@permissao_obrigatoria("clientes_editar")
def buscar_cliente(id):
    user_id = session.get("usuario_id")
    try:
        cliente = Cliente.find_by_id(id, usuario_id=user_id)
        if not cliente:
            flash("Cliente não encontrado ou acesso negado.", "erro")
            return redirect(url_for("listar_clientes"))
        return render_template("cliente.html", cliente=cliente)
    except Exception as e:
        flash("Erro ao carregar cliente.", "erro")
        return redirect(url_for("listar_clientes"))


@app.route("/cliente/<int:id>/atualizar", methods=["POST"])
@login_obrigatorio
@permissao_obrigatoria("clientes_editar")
def atualizar_cliente(id):
    user_id = session.get("usuario_id")
    dados = get_cliente_form()
    dados["email"] = dados["email"].lower().strip()
    cliente = Cliente(**dados)
    erros = cliente.validate(exigir_senha=False)
    senha_confirmacao = request.form.get("confirmar_senha", "")
    if dados["senha"] and dados["senha"] != senha_confirmacao:
        erros.append("A confirmação da senha não corresponde.")

    if erros:
        for erro in erros:
            flash(erro, "erro")
        dados["id"] = id
        return render_template("cliente.html", cliente=dados)

    try:
        cliente_existente = Cliente.find_by_id(id, usuario_id=user_id)
        if not cliente_existente:
            flash("Cliente não encontrado ou acesso negado.", "erro")
            return redirect(url_for("listar_clientes"))
        linhas_afetadas = cliente.update(id, usuario_id=user_id)
        flash(
            "Cliente atualizado com sucesso." if linhas_afetadas else "Nenhuma alteração realizada.",
            "sucesso" if linhas_afetadas else "info",
        )
        return redirect(url_for("buscar_cliente", id=id))
    except Exception:
        app.logger.exception("Erro ao atualizar cliente")
        flash("Não foi possível atualizar o cliente. Verifique se o e-mail ou CNPJ já existe.", "erro")
        dados["id"] = id
        return render_template("cliente.html", cliente=dados)




@app.route("/cliente/<int:id>/excluir", methods=["POST"])
@login_obrigatorio
@permissao_obrigatoria("clientes_excluir")
def excluir_cliente(id):
    user_id = session.get("usuario_id")
    try:
        cliente = Cliente.find_by_id(id, usuario_id=user_id)
        if not cliente:
            flash("Cliente não encontrado ou acesso negado.", "erro")
            return redirect(url_for("listar_clientes"))

        Cliente.safe_delete(id, usuario_id=user_id)

        flash("Cliente excluído com sucesso.", "sucesso")
    except ValueError as e:
        flash(str(e), "erro")
    except Exception as e:
        flash("Erro ao excluir cliente.", "erro")
    return redirect(url_for("listar_clientes"))


# (Produto)============================================================================================
@app.route("/produto/novo", methods=["GET"])
@login_obrigatorio
@permissao_obrigatoria("produtos_criar")
def novo_produto():
    return render_template("produtos.html", produto={})


@app.route("/produtos", methods=["GET"])
@login_obrigatorio
@permissao_obrigatoria("produtos_ver")
def listar_produtos():
    try:
        produtos = Produto.find_all(usuario_id=session.get("usuario_id"), order_by="id DESC")
        return render_template(
            "listar_produtos.html",
            produtos=produtos,
            limite_estoque_baixo=LIMITE_ESTOQUE_BAIXO,
        )
    except Exception as e:
        print(f"Erro ao carregar produtos: {e}")
        flash("Erro ao carregar produtos.", "erro")
        return render_template("listar_produtos.html", produtos=[], limite_estoque_baixo=LIMITE_ESTOQUE_BAIXO)


@app.route("/produto/salvar", methods=["POST"])
@login_obrigatorio
@permissao_obrigatoria("produtos_criar")
def salvar_produto():
    dados = get_produto_form()
    produto = Produto(**dados)
    erros = produto.validate()
    if erros:
        for erro in erros:
            flash(erro, "erro")
        return render_template("produtos.html", produto=produto)

    conexao = None
    cursor = None
    try:
        conexao = Database.connect()
        cursor = conexao.cursor()
        cursor.execute(
            """INSERT INTO produto
               (nome, marca, data_de_validade, especificacao, unidade_medida, quantidade,
                precisa_temperatura_baixa, usuario_id)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (produto.nome, produto.marca, produto.data_de_validade, produto.especificacao,
             produto.unidade_medida, produto.quantidade, produto.precisa_temperatura_baixa,
             produto.usuario_id),
        )
        novo_id = cursor.lastrowid
        if produto.quantidade > 0:
            cursor.execute(
                """INSERT INTO movimentacao
                   (tipo_movimentacao, quantidade, data_movimentacao, produto_id)
                   VALUES (%s, %s, %s, %s)""",
                ("ENTRADA", produto.quantidade, datetime.now(), novo_id),
            )
        conexao.commit()
        flash("Produto cadastrado com sucesso.", "sucesso")
        return redirect(url_for("listar_produtos"))
    except Exception:
        if conexao:
            conexao.rollback()
        app.logger.exception("Erro ao cadastrar produto")
        flash("Não foi possível cadastrar o produto. Verifique os dados e o banco de dados.", "erro")
        return render_template("produtos.html", produto=produto)
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()




@app.route("/produto/<int:id>/editar", methods=["GET"])
@login_obrigatorio
@permissao_obrigatoria("produtos_editar")
def buscar_produto(id):
    try:
        produto = Produto.find_by_id(id, usuario_id=session.get("usuario_id"))
        if not produto:
            flash("Produto não encontrado.", "erro")
            return redirect(url_for("listar_produtos"))
        return render_template("produtos.html", produto=produto)
    except Exception as e:
        print(f"Erro ao buscar produto: {e}")
        flash("Erro ao carregar produto.", "erro")
        return redirect(url_for("listar_produtos"))


@app.route("/produto/<int:id>/atualizar", methods=["POST"])
@login_obrigatorio
@permissao_obrigatoria("produtos_editar")
def atualizar_produto(id):
    dados = get_produto_form()
    produto = Produto(**dados)

    if hasattr(produto, "id"):
        produto.id = id
    elif isinstance(produto, dict):
        produto["id"] = id

    erros = produto.validate() if hasattr(produto, "validate") else []

    if erros:
        for erro in erros:
            flash(erro, "erro")
        return render_template("produtos.html", produto=produto)

    conexao = None
    cursor = None
    try:
        user_id = session.get("usuario_id")
        conexao = Database.connect()
        cursor = conexao.cursor()
        cursor.execute(
            "SELECT quantidade FROM produto WHERE id = %s AND usuario_id = %s FOR UPDATE",
            (id, user_id),
        )
        atual = cursor.fetchone()
        if not atual:
            raise ValueError("Produto não encontrado ou acesso negado.")

        quantidade_anterior = int(atual[0] or 0)
        cursor.execute(
            """UPDATE produto
               SET nome = %s, marca = %s, data_de_validade = %s,
                   especificacao = %s, unidade_medida = %s, quantidade = %s,
                   precisa_temperatura_baixa = %s
               WHERE id = %s AND usuario_id = %s""",
            (
                produto.nome, produto.marca, produto.data_de_validade,
                produto.especificacao, produto.unidade_medida, produto.quantidade,
                produto.precisa_temperatura_baixa, id, user_id,
            ),
        )

        diferenca_estoque = produto.quantidade - quantidade_anterior
        if diferenca_estoque:
            cursor.execute(
                """INSERT INTO movimentacao
                   (tipo_movimentacao, quantidade, data_movimentacao, produto_id)
                   VALUES ('AJUSTE', %s, %s, %s)""",
                (abs(diferenca_estoque), datetime.now(), id),
            )

        conexao.commit()
        flash("Produto atualizado com sucesso.", "sucesso")
        return redirect(url_for("listar_produtos"))
    except ValueError as erro:
        if conexao:
            conexao.rollback()
        flash(str(erro), "erro")
        return redirect(url_for("listar_produtos"))
    except Exception:
        if conexao:
            conexao.rollback()
        app.logger.exception("Erro ao atualizar produto")
        flash("Não foi possível atualizar o produto. Verifique os dados e o banco de dados.", "erro")
        return render_template("produtos.html", produto=produto)
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()


@app.route("/produto/<int:id>/excluir", methods=["POST"])
@login_obrigatorio
@permissao_obrigatoria("produtos_excluir")
def excluir_produto(id):
    user_id = session.get("usuario_id")
    try:
        Produto.safe_delete(id, usuario_id=user_id)
        flash("Produto excluído com sucesso.", "sucesso")
    except ValueError as erro:
        flash(str(erro), "erro")
    except Exception:
        app.logger.exception("Erro ao excluir produto")
        flash("Não foi possível excluir o produto. Verifique os registros vinculados.", "erro")
    return redirect(url_for("listar_produtos"))




# (Movimentação)===========================================================================================
@app.route("/movimentacoes")
@login_obrigatorio
@permissao_obrigatoria("estoque_ver")
def movimentacoes():
    user_id = session.get("usuario_id")
    movimentacoes_list = (
        Movimentacao.find_all_with_product(usuario_id=user_id)
        if hasattr(Movimentacao, "find_all_with_product")
        else Movimentacao.find_all(usuario_id=user_id)
    )
    movimentacoes_entrada = (
        PedidoEntrada.listar_movimentacoes(usuario_id=user_id)
        if hasattr(PedidoEntrada, "listar_movimentacoes")
        else []
    )
    movimentacoes_saida = (
        PedidoSaida.listar_movimentacoes(usuario_id=user_id)
        if hasattr(PedidoSaida, "listar_movimentacoes")
        else []
    )

    return render_template(
        "movimentacoes.html",
        movimentacoes=movimentacoes_list,
        movimentacoes_entrada=movimentacoes_entrada,
        movimentacoes_saida=movimentacoes_saida,
    )


# (PedidoEntrada)===========================================================================================
@app.route("/pedido_entrada/novo", methods=["GET"])
@login_obrigatorio
@permissao_obrigatoria("pedido_entrada")
def novo_pedido_entrada():
    user_id = session.get("usuario_id")
    usuario_atual = [Usuario.find_by_id(user_id)] if user_id else []

    try:
        produtos = Produto.find_all(usuario_id=user_id)
    except Exception as e:
        print("Erro ao buscar produtos:", e)
        produtos = []

    return render_template(
        "pedido_entrada.html",
        pedido_entrada={},
        usuarios=usuario_atual,
        produtos=produtos,
    )


@app.route("/pedido_entrada", methods=["GET"])
@login_obrigatorio
@permissao_obrigatoria("pedido_entrada")
def listar_pedido_entrada():
    user_id = session.get("usuario_id")
    try:
        pedidos_entrada = PedidoEntrada.find_all(
            usuario_id=user_id, order_by="id_pedido_entrada DESC"
        )
        return render_template(
            "pedido_entrada_lista.html", pedidos_entrada=pedidos_entrada
        )
    except Exception as e:
        print("ERRO:", e)
        flash("Erro ao carregar pedidos de entrada.", "erro")
        return render_template("pedido_entrada_lista.html", pedidos_entrada=[])


@app.route("/pedido_entrada/salvar", methods=["POST"])
@login_obrigatorio
@permissao_obrigatoria("pedido_entrada")
def salvar_pedido_entrada():
    user_id = session.get("usuario_id")
    dados = get_pedido_entrada_form()
    pedido_entrada = PedidoEntrada(**dados)
    erros = pedido_entrada.validate() if hasattr(pedido_entrada, "validate") else []
    usuario_atual = [Usuario.find_by_id(user_id)] if user_id else []

    if erros:
        for erro in erros:
            flash(erro, "erro")
        return render_template(
            "pedido_entrada.html",
            pedido_entrada=pedido_entrada,
            usuarios=usuario_atual,
            produtos=Produto.find_all(usuario_id=user_id),
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
            usuarios=usuario_atual,
            produtos=Produto.find_all(usuario_id=user_id),
            movimentacoes=[],
            itens=[],
        )


@app.route("/pedido_entrada/<int:id>/editar")
@login_obrigatorio
@permissao_obrigatoria("pedido_entrada")
def buscar_pedido_entrada(id):
    user_id = session.get("usuario_id")
    try:
        pedido_entrada = PedidoEntrada.find_by_id(id, usuario_id=user_id)
        if not pedido_entrada:
            flash("Pedido não encontrado ou acesso negado.", "erro")
            return redirect(url_for("listar_pedido_entrada"))

        usuario_atual = [Usuario.find_by_id(user_id)] if user_id else []
        movimentacoes_list = (
            Movimentacao.find_all_with_product(usuario_id=user_id)
            if hasattr(Movimentacao, "find_all_with_product")
            else []
        )
        itens = (
            ItemEntrada.find_by_pedido(id) if hasattr(ItemEntrada, "find_by_pedido") else []
        )
        return render_template(
            "pedido_entrada.html",
            pedido_entrada=pedido_entrada,
            usuarios=usuario_atual,
            produtos=Produto.find_all(usuario_id=user_id),
            movimentacoes=movimentacoes_list,
            itens=itens,
        )
    except Exception as e:
        flash("Erro ao carregar pedido.", "erro")
        return redirect(url_for("listar_pedido_entrada"))


@app.route("/pedido_entrada/<int:id>/atualizar", methods=["POST"])
@login_obrigatorio
@permissao_obrigatoria("pedido_entrada")
def atualizar_pedido_entrada(id):
    user_id = session.get("usuario_id")
    dados = get_pedido_entrada_form()
    pedido_entrada = PedidoEntrada(**dados)
    erros = pedido_entrada.validate() if hasattr(pedido_entrada, "validate") else []
    usuario_atual = [Usuario.find_by_id(user_id)] if user_id else []

    if erros:
        for erro in erros:
            flash(erro, "erro")
        dados["id"] = id
        return render_template(
            "pedido_entrada.html",
            pedido_entrada=dados,
            usuarios=usuario_atual,
            produtos=Produto.find_all(usuario_id=user_id),
            movimentacoes=[],
            itens=[],
        )
    try:
        pedido_existente = PedidoEntrada.find_by_id(id, usuario_id=user_id)
        if not pedido_existente:
            flash("Pedido não encontrado ou acesso negado.", "erro")
            return redirect(url_for("listar_pedido_entrada"))

        linhas_afetadas = pedido_entrada.update(id, usuario_id=user_id)
        if linhas_afetadas == 0:
            flash("Nenhuma alteração realizada.", "erro")
            return redirect(url_for("buscar_pedido_entrada", id=id))

        flash("Pedido atualizado com sucesso.", "sucesso")
        return redirect(url_for("listar_pedido_entrada"))
    except Exception:
        flash("Erro ao atualizar pedido.", "erro")
        dados["id"] = id
        return render_template(
            "pedido_entrada.html",
            pedido_entrada=dados,
            usuarios=usuario_atual,
            produtos=Produto.find_all(usuario_id=user_id),
            movimentacoes=[],
            itens=[],
        )


@app.route("/pedido_entrada/<int:id>/excluir", methods=["POST"])
@login_obrigatorio
@permissao_obrigatoria("pedido_entrada")
def excluir_pedido_entrada(id):
    user_id = session.get("usuario_id")
    try:
        pedido_entrada = PedidoEntrada.find_by_id(id, usuario_id=user_id)
        if not pedido_entrada:
            flash("Pedido de entrada não encontrado ou acesso negado.", "erro")
            return redirect(url_for("listar_pedido_entrada"))

        PedidoEntrada.safe_delete(id, usuario_id=user_id)

        flash("Pedido de entrada excluído com sucesso.", "sucesso")
    except ValueError as e:
        flash(str(e), "erro")
    except Exception as e:
        flash("Erro ao excluir pedido de entrada.", "erro")
    return redirect(url_for("listar_pedido_entrada"))


# (Item Entrada)===========================================================================================
@app.route("/item_entrada/salvar", methods=["POST"])
@login_obrigatorio
@permissao_obrigatoria("pedido_entrada")
def salvar_item_entrada():
    user_id = session.get("usuario_id")
    pedido_raw = request.form.get("pedido_entrada_id", "").strip()
    produto_raw = request.form.get("produto_id", "").strip()
    qtd_raw = request.form.get("quantidade", "").strip()
    valor_raw = request.form.get("valor", "").strip().replace(",", ".")

    try:
        pedido_id = int(pedido_raw)
        produto_id = int(produto_raw)
        quantidade = int(qtd_raw)
        valor = float(valor_raw)
    except (TypeError, ValueError):
        flash("Informe pedido, produto, quantidade e valor válidos.", "erro")
        if pedido_raw.isdigit() and int(pedido_raw) > 0:
            return redirect(url_for("buscar_pedido_entrada", id=int(pedido_raw)))
        return redirect(url_for("listar_pedido_entrada"))

    from math import isfinite
    if quantidade < 50:
        flash("A quantidade de entrada deve ser de no mínimo 50 unidades.", "erro")
        return redirect(url_for("buscar_pedido_entrada", id=pedido_id))
    if not isfinite(valor) or valor < 0:
        flash("O valor deve ser um número válido e não pode ser negativo.", "erro")
        return redirect(url_for("buscar_pedido_entrada", id=pedido_id))

    conexao = None
    cursor = None
    try:
        conexao = Database.connect()
        cursor = conexao.cursor()
        coluna_usuario_pedido = PedidoEntrada.coluna_usuario(cursor)
        cursor.execute(
            f"SELECT id_pedido_entrada FROM pedido_entrada WHERE id_pedido_entrada = %s AND {coluna_usuario_pedido} = %s FOR UPDATE",
            (pedido_id, user_id),
        )
        if not cursor.fetchone():
            raise ValueError("Pedido de entrada não encontrado ou acesso negado.")
        cursor.execute(
            "SELECT id FROM produto WHERE id = %s AND usuario_id = %s FOR UPDATE",
            (produto_id, user_id),
        )
        if not cursor.fetchone():
            raise ValueError("Produto não encontrado ou acesso negado.")

        cursor.execute(
            """INSERT INTO movimentacao
               (tipo_movimentacao, quantidade, data_movimentacao, produto_id)
               VALUES ('ENTRADA', %s, %s, %s)""",
            (quantidade, datetime.now(), produto_id),
        )
        movimentacao_id = cursor.lastrowid
        cursor.execute(
            """INSERT INTO item_entrada
               (quantidade, valor, pedido_entrada_id, movimentacao_id)
               VALUES (%s, %s, %s, %s)""",
            (quantidade, valor, pedido_id, movimentacao_id),
        )
        cursor.execute(
            "UPDATE produto SET quantidade = quantidade + %s WHERE id = %s AND usuario_id = %s",
            (quantidade, produto_id, user_id),
        )
        if cursor.rowcount != 1:
            raise ValueError("Não foi possível atualizar o estoque do produto.")
        conexao.commit()
        flash("Item de entrada registrado e estoque atualizado com sucesso.", "sucesso")
    except ValueError as erro:
        if conexao:
            conexao.rollback()
        flash(str(erro), "erro")
    except Exception:
        if conexao:
            conexao.rollback()
        app.logger.exception("Erro ao adicionar item de entrada")
        flash("Não foi possível registrar a entrada. Nenhuma alteração parcial foi salva.", "erro")
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()

    return redirect(url_for("buscar_pedido_entrada", id=pedido_id))




# (Localização)===========================================================================================
@app.route("/localizacao/novo")
@login_obrigatorio
@permissao_obrigatoria("localizacoes_criar")
def nova_localizacao():
    produtos = Produto.find_all(usuario_id=session.get("usuario_id"))
    return render_template("localizacao.html", produtos=produtos)




@app.route("/localizacao")
@login_obrigatorio
@permissao_obrigatoria("localizacoes_ver")
def listar_localizacao():
    user_id = session.get("usuario_id")
    localizacoes = Localizacao.find_all_com_produto(usuario_id=user_id)
    return render_template("listar_localizacao.html", localizacoes=localizacoes)


@app.route("/localizacao/salvar", methods=["POST"])
@login_obrigatorio
@permissao_obrigatoria("localizacoes_criar")
def salvar_localizacao():
    user_id = session.get("usuario_id")
    localizacao = Localizacao(
        rua=request.form.get("rua", "").strip(),
        numero=request.form.get("numero", "").strip(),
        andar=request.form.get("andar", "").strip(),
        usuario_id=user_id,
    )
    produto_raw = request.form.get("produto_id", "").strip()
    erros = localizacao.validate() if hasattr(localizacao, "validate") else []
    if not produto_raw.isdigit() or int(produto_raw) <= 0:
        erros.append("Selecione um produto válido.")
    if erros:
        for erro in erros:
            flash(erro, "erro")
        return redirect(url_for("nova_localizacao"))

    conexao = None
    cursor = None
    try:
        conexao = Database.connect()
        cursor = conexao.cursor()
        cursor.execute(
            "SELECT id FROM produto WHERE id = %s AND usuario_id = %s FOR UPDATE",
            (int(produto_raw), user_id),
        )
        if not cursor.fetchone():
            raise ValueError("Produto não encontrado ou acesso negado.")
        cursor.execute(
            "INSERT INTO localizacao (rua, numero, andar, usuario_id) VALUES (%s, %s, %s, %s)",
            (localizacao.rua, localizacao.numero, localizacao.andar, user_id),
        )
        localizacao_id = cursor.lastrowid
        cursor.execute(
            "UPDATE produto SET localizacao_id = %s WHERE id = %s AND usuario_id = %s",
            (localizacao_id, int(produto_raw), user_id),
        )
        if cursor.rowcount != 1:
            raise ValueError("Não foi possível vincular o produto à localização.")
        conexao.commit()
        flash("Localização cadastrada com sucesso.", "sucesso")
    except ValueError as erro:
        if conexao:
            conexao.rollback()
        flash(str(erro), "erro")
    except Exception:
        if conexao:
            conexao.rollback()
        app.logger.exception("Erro ao salvar localização")
        flash("Não foi possível cadastrar a localização.", "erro")
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()
    return redirect(url_for("listar_localizacao"))



# (Pedido de Saída)============================================================================================
@app.route("/pedido_saida/novo")
@login_obrigatorio
@permissao_obrigatoria("pedido_saida")
def novo_pedido_saida():
    user_id = session.get("usuario_id")
    clientes = Cliente.find_all(usuario_id=user_id, order_by="nome")
    usuario_atual = [Usuario.find_by_id(user_id)] if user_id else []
    produtos = Produto.find_all(usuario_id=user_id)

    return render_template(
        "pedido_saida.html",
        pedido_saida={},
        clientes=clientes,
        usuarios=usuario_atual,
        produtos=produtos,
        itens=[],
    )


@app.route("/pedido_saida", methods=["GET"])
@login_obrigatorio
@permissao_obrigatoria("pedido_saida")
def listar_pedido_saida():
    user_id = session.get("usuario_id")
    try:
        pedidos_saida = (
            PedidoSaida.listar_pedidos(usuario_id=user_id)
            if hasattr(PedidoSaida, "listar_pedidos")
            else PedidoSaida.find_all(usuario_id=user_id)
        )
        return render_template("pedido_saida_lista.html", pedidos_saida=pedidos_saida)
    except Exception as e:
        flash("Erro ao carregar pedidos de saída.", "erro")
        return render_template("pedido_saida_lista.html", pedidos_saida=[])


@app.route("/pedido_saida/<int:id>/editar")
@login_obrigatorio
@permissao_obrigatoria("pedido_saida")
def buscar_pedido_saida(id):
    user_id = session.get("usuario_id")
    try:
        pedido_saida = PedidoSaida.find_by_id(id, usuario_id=user_id)
        if not pedido_saida:
            flash("Pedido de saída não encontrado ou acesso negado.", "erro")
            return redirect(url_for("listar_pedido_saida"))

        clientes = Cliente.find_all(usuario_id=user_id, order_by="nome")
        usuario_atual = [Usuario.find_by_id(user_id)] if user_id else []
        produtos = Produto.find_all(usuario_id=user_id)
        itens = (
            ItemSaida.find_by_pedido(id) if hasattr(ItemSaida, "find_by_pedido") else []
        )
        return render_template(
            "pedido_saida.html",
            pedido_saida=pedido_saida,
            clientes=clientes,
            usuarios=usuario_atual,
            produtos=produtos,
            itens=itens,
        )
    except Exception:
        app.logger.exception("Erro ao carregar pedido de saída")
        flash("Erro ao carregar o pedido de saída.", "erro")
        return redirect(url_for("listar_pedido_saida"))


@app.route("/pedido_saida/salvar", methods=["POST"])
@login_obrigatorio
@permissao_obrigatoria("pedido_saida")
def salvar_pedido_saida():
    user_id = session.get("usuario_id")
    dados = get_pedido_saida_form()
    pedido_saida = PedidoSaida(**dados)
    erros = pedido_saida.validate()
    usuario_atual = [Usuario.find_by_id(user_id)] if user_id else []
    clientes = Cliente.find_all(usuario_id=user_id, order_by="nome")
    if dados.get("cliente_id") and not Cliente.find_by_id(dados["cliente_id"], usuario_id=user_id):
        erros.append("Selecione um cliente cadastrado na sua conta.")

    if erros:
        for erro in erros:
            flash(erro, "erro")
        return render_template(
            "pedido_saida.html",
            pedido_saida=pedido_saida,
            clientes=clientes,
            usuarios=usuario_atual,
            produtos=Produto.find_all(usuario_id=user_id),
            movimentacoes=[],
            itens=[],
        )
    try:
        novo_id = pedido_saida.insert()
        flash("Pedido de saída cadastrado com sucesso.", "sucesso")
        return redirect(url_for("buscar_pedido_saida", id=novo_id, _anchor="itens"))
    except Exception as e:
        flash(f"Erro ao cadastrar pedido: {e}", "erro")
        return render_template(
            "pedido_saida.html",
            pedido_saida=pedido_saida,
            clientes=clientes,
            usuarios=usuario_atual,
            produtos=Produto.find_all(usuario_id=user_id),
            movimentacoes=[],
            itens=[],
        )


@app.route("/pedido_saida/<int:id>/atualizar", methods=["POST"])
@login_obrigatorio
@permissao_obrigatoria("pedido_saida")
def atualizar_pedido_saida(id):
    user_id = session.get("usuario_id")
    dados = get_pedido_saida_form()
    pedido_saida = PedidoSaida(**dados)
    erros = pedido_saida.validate()
    usuario_atual = [Usuario.find_by_id(user_id)] if user_id else []
    clientes = Cliente.find_all(usuario_id=user_id, order_by="nome")
    if dados.get("cliente_id") and not Cliente.find_by_id(dados["cliente_id"], usuario_id=user_id):
        erros.append("Selecione um cliente cadastrado na sua conta.")

    if erros:
        for erro in erros:
            flash(erro, "erro")
        dados["id"] = id
        return render_template(
            "pedido_saida.html",
            pedido_saida=dados,
            clientes=clientes,
            usuarios=usuario_atual,
            produtos=Produto.find_all(usuario_id=user_id),
            movimentacoes=[],
            itens=[],
        )
    try:
        pedido_existente = PedidoSaida.find_by_id(id, usuario_id=user_id)
        if not pedido_existente:
            flash("Pedido de saída não encontrado ou acesso negado.", "erro")
            return redirect(url_for("listar_pedido_saida"))

        linhas_afetadas = pedido_saida.update(id, usuario_id=user_id)
        if linhas_afetadas == 0:
            flash("Nenhuma alteração realizada.", "info")

        flash("Pedido de saída atualizado com sucesso.", "sucesso")
        return redirect(url_for("listar_pedido_saida"))
    except Exception as e:
        flash(f"Erro ao atualizar pedido: {e}", "erro")
        dados["id"] = id
        return render_template(
            "pedido_saida.html",
            pedido_saida=dados,
            clientes=clientes,
            usuarios=usuario_atual,
            produtos=Produto.find_all(usuario_id=user_id),
            movimentacoes=[],
            itens=[],
        )

@app.route("/api/produto/<int:id>", methods=["GET"])
@login_obrigatorio
def api_produto(id):
    produto = Produto.find_by_id(id, usuario_id=session.get("usuario_id"))
    if not produto:
        return {"erro": "Produto não encontrado."}, 404
    if isinstance(produto, dict):
        produto["quantidade"] = int(produto.get("quantidade") or 0)
    else:
        produto.quantidade = int(getattr(produto, "quantidade", 0))
    return produto

@app.route("/item_saida/salvar", methods=["POST"])
@login_obrigatorio
@permissao_obrigatoria("pedido_saida")
def salvar_item_saida():
    user_id = session.get("usuario_id")
    pedido_raw = request.form.get("pedido_saida_id", "").strip()
    produto_raw = request.form.get("produto_id", "").strip()
    qtd_raw = request.form.get("quantidade", "").strip()
    valor_raw = request.form.get("valor", "").strip().replace(",", ".")

    try:
        pedido_id = int(pedido_raw)
        produto_id = int(produto_raw)
        quantidade = int(qtd_raw)
        valor = float(valor_raw)
    except (TypeError, ValueError):
        flash("Informe pedido, produto, quantidade e valor válidos.", "erro")
        if pedido_raw.isdigit() and int(pedido_raw) > 0:
            return redirect(url_for("buscar_pedido_saida", id=int(pedido_raw), _anchor="itens"))
        return redirect(url_for("listar_pedido_saida"))

    from math import isfinite
    if quantidade <= 0:
        flash("A quantidade de saída deve ser maior que zero.", "erro")
        return redirect(url_for("buscar_pedido_saida", id=pedido_id, _anchor="itens"))
    if not isfinite(valor) or valor < 0:
        flash("O valor deve ser um número válido e não pode ser negativo.", "erro")
        return redirect(url_for("buscar_pedido_saida", id=pedido_id, _anchor="itens"))

    conexao = None
    cursor = None
    try:
        conexao = Database.connect()
        cursor = conexao.cursor()
        cursor.execute(
            "SELECT id FROM pedido_saida WHERE id = %s AND usuario_id = %s FOR UPDATE",
            (pedido_id, user_id),
        )
        if not cursor.fetchone():
            raise ValueError("Pedido de saída não encontrado ou acesso negado.")

        cursor.execute(
            "SELECT quantidade FROM produto WHERE id = %s AND usuario_id = %s FOR UPDATE",
            (produto_id, user_id),
        )
        produto = cursor.fetchone()
        if not produto:
            raise ValueError("Produto não encontrado ou acesso negado.")
        estoque = int(produto[0] or 0)
        if quantidade > estoque:
            raise ValueError(f"Estoque insuficiente. Estoque atual: {estoque} unidades.")

        cursor.execute(
            """INSERT INTO movimentacao
               (tipo_movimentacao, quantidade, data_movimentacao, produto_id)
               VALUES ('SAIDA', %s, %s, %s)""",
            (quantidade, datetime.now(), produto_id),
        )
        movimentacao_id = cursor.lastrowid
        cursor.execute(
            """INSERT INTO item_saida
               (quantidade, valor, pedido_saida_id, movimentacao_id)
               VALUES (%s, %s, %s, %s)""",
            (quantidade, valor, pedido_id, movimentacao_id),
        )
        cursor.execute(
            """UPDATE produto SET quantidade = quantidade - %s
               WHERE id = %s AND usuario_id = %s AND quantidade >= %s""",
            (quantidade, produto_id, user_id, quantidade),
        )
        if cursor.rowcount != 1:
            raise ValueError("O estoque mudou durante a operação. Atualize a página e tente novamente.")
        conexao.commit()
        flash("Item de saída registrado e estoque atualizado com sucesso.", "sucesso")
    except ValueError as erro:
        if conexao:
            conexao.rollback()
        flash(str(erro), "erro")
    except Exception:
        if conexao:
            conexao.rollback()
        app.logger.exception("Erro ao adicionar item de saída")
        flash("Não foi possível registrar a saída. Nenhuma alteração parcial foi salva.", "erro")
    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()

    return redirect(url_for("buscar_pedido_saida", id=pedido_id, _anchor="itens"))




@app.route("/pedido_saida/<int:id>/excluir", methods=["POST"])
@login_obrigatorio
@permissao_obrigatoria("pedido_saida")
def excluir_pedido_saida(id):
    user_id = session.get("usuario_id")
    try:
        pedido = PedidoSaida.find_by_id(id, usuario_id=user_id)
        if not pedido:
            flash("Pedido de saída não encontrado ou acesso negado.", "erro")
            return redirect(url_for("listar_pedido_saida"))
        PedidoSaida.safe_delete(id, usuario_id=user_id)
        flash("Pedido de saída excluído com sucesso.", "sucesso")
    except ValueError as e:
        flash(str(e), "erro")
    except Exception as e:
        print("ERRO AO EXCLUIR PEDIDO DE SAÍDA:", e)
        flash("Erro ao excluir pedido de saída.", "erro")
    return redirect(url_for("listar_pedido_saida"))

@app.route("/pedido_saida/<int:id>/nota_fiscal")
@login_obrigatorio
@permissao_obrigatoria("pedido_saida")
def gerar_nota_fiscal_saida(id):
    user_id = session.get("usuario_id")
    try:
        pedido = PedidoSaida.find_by_id(id, usuario_id=user_id)
        if not pedido:
            flash("Pedido de saída não encontrado ou acesso negado.", "erro")
            return redirect(url_for("listar_pedido_saida"))
        cliente = None
        cliente_id = pedido.get("cliente_id") if isinstance(pedido, dict) else getattr(pedido, "cliente_id", None)
        if cliente_id:
            cliente = Cliente.find_by_id(cliente_id, usuario_id=user_id)
        itens = ItemSaida.find_by_pedido(id) if hasattr(ItemSaida, "find_by_pedido") else []
        total_pedido = sum(
            (float(it.get("valor", 0)) if isinstance(it, dict) else float(getattr(it, "valor", 0))) *
            (int(it.get("quantidade", 0)) if isinstance(it, dict) else int(getattr(it, "quantidade", 0)))
            for it in itens
        ) if itens else (pedido.get("valor", 0) if isinstance(pedido, dict) else getattr(pedido, "valor", 0))
        return render_template(
            "nota_fiscal.html",
            pedido=pedido,
            cliente=cliente,
            itens=itens,
            total_pedido=total_pedido,
            data_emissao=datetime.now(),
        )
    except Exception as e:
        print("ERRO AO GERAR NOTA FISCAL:", e)
        flash("Erro ao gerar Nota Fiscal.", "erro")
        return redirect(url_for("buscar_pedido_saida", id=id))


# (Sensor IoT - DHT11)================================================================================
@app.route("/sensores")
@login_obrigatorio
def pagina_sensores():
    return render_template(
        "sensores.html",
        resumo=SensorLeitura.resumo(),
        conectado=mqtt_manager.conectado,
        temperatura_min=SENSOR_TEMP_MIN,
        temperatura_max=SENSOR_TEMP_MAX,
    )


@app.route("/api/resumo")
@login_obrigatorio
def api_resumo_sensor():
    resumo = SensorLeitura.resumo()
    resumo["mqtt_conectado"] = mqtt_manager.conectado
    return jsonify(resumo)


@app.route("/api/leituras")
@login_obrigatorio
def api_leituras_sensor():
    try:
        limite = int(request.args.get("limite", 100))
    except (TypeError, ValueError):
        limite = 100

    resultado = SensorLeitura.listar(
        device_id=request.args.get("device_id"),
        sensor="DHT11",
        limite=limite,
    )
    return jsonify({"sensor": "DHT11", "quantidade": len(resultado), "leituras": resultado})


@app.route("/api/sensores")
@login_obrigatorio
def api_dht11():
    return jsonify(SensorLeitura.listar(sensor="DHT11", limite=100))


@app.route("/api/sensores/dht11")
@login_obrigatorio
def api_dht11_detalhado():
    return jsonify({"sensor": "DHT11", "leituras": SensorLeitura.listar(sensor="DHT11")})


@app.route("/api/status-iot")
@login_obrigatorio
def api_status_iot():
    return jsonify({
        "mqtt": mqtt_manager.conectado,
        "sensor": "DHT11",
        "broker": MQTT_BROKER,
        "topic": MQTT_TOPIC,
    })


# (Páginas de erro)===============================================================================
@app.errorhandler(404)
def pagina_nao_encontrada(erro):
    """Exibe uma página amigável para URLs inexistentes."""
    # APIs devem retornar JSON, em vez de HTML, quando o recurso não existir.
    if request.path.startswith("/api/"):
        return jsonify({
            "erro": "Recurso não encontrado.",
            "status": 404,
        }), 404

    return render_template("404.html"), 404

if __name__ == "__main__":
    debug_ativo = os.getenv("SMARTMEDS_DEBUG", "false").strip().lower() in {"1", "true", "sim", "yes"}
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")), debug=debug_ativo)