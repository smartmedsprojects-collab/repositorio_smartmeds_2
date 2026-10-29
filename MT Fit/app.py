from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_wtf.csrf import CSRFProtect
from mysql.connector import IntegrityError, Error

from config import Config
from core.database import fetch_all, fetch_one
from core.validators import limpar_texto, validar_email, validar_cpf, validar_data_hora
from models.usuario import Usuario
from models.aluno import Aluno
from models.plano import Plano
from models.agendamento import Agendamento

app = Flask(__name__)
app.config.from_object(Config)
CSRFProtect(app)


@app.template_filter("hora_hhmm")
def hora_hhmm(valor):
    """Converte TIME do MySQL (timedelta ou string) para HH:MM em inputs HTML."""
    if valor is None:
        return ""
    if hasattr(valor, "total_seconds"):
        total = int(valor.total_seconds())
        return f"{(total // 3600) % 24:02d}:{(total % 3600) // 60:02d}"
    return str(valor)[:5]


def login_obrigatorio(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("usuario_id"):
            flash("Entre na sua conta para continuar.", "warning")
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return wrapper


@app.before_request
def controlar_sessao():
    if request.endpoint in ("login", "static") or request.endpoint is None:
        return
    ultima = session.get("ultima_atividade")
    if session.get("usuario_id") and ultima:
        try:
            ultima_dt = datetime.fromisoformat(ultima)
            if datetime.now() - ultima_dt > timedelta(minutes=app.config["SESSION_TIMEOUT_MINUTES"]):
                session.clear()
                flash("Sua sessão expirou por inatividade. Entre novamente.", "info")
                return redirect(url_for("login"))
        except (ValueError, TypeError):
            session.clear()
            return redirect(url_for("login"))
    if session.get("usuario_id"):
        session["ultima_atividade"] = datetime.now().isoformat()


@app.route("/", methods=["GET", "POST"])
def login():
    if session.get("usuario_id"):
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        email = limpar_texto(request.form.get("email"))
        senha = request.form.get("senha", "")
        if not validar_email(email) or not senha:
            flash("Informe um e-mail válido e a senha.", "danger")
        else:
            try:
                usuario = Usuario.autenticar(email, senha)
                if usuario:
                    session.clear()
                    session.permanent = True
                    session["usuario_id"] = usuario["id"]
                    session["usuario_nome"] = usuario["nome"]
                    session["ultima_atividade"] = datetime.now().isoformat()
                    return redirect(url_for("dashboard"))
                flash("E-mail ou senha inválidos.", "danger")
            except Error:
                app.logger.exception("Falha ao autenticar no MySQL")
                flash("Não foi possível acessar o banco de dados. Confira config.py e o MySQL.", "danger")
    return render_template("login.html")


@app.post("/logout")
@login_obrigatorio
def logout():
    session.clear()
    flash("Você saiu do sistema.", "success")
    return redirect(url_for("login"))


@app.get("/dashboard")
@login_obrigatorio
def dashboard():
    try:
        totais = {
            "alunos": fetch_one("SELECT COUNT(*) AS total FROM alunos")["total"],
            "planos": fetch_one("SELECT COUNT(*) AS total FROM planos")["total"],
            "agendamentos": fetch_one("SELECT COUNT(*) AS total FROM agendamentos")["total"],
        }
        proximos = Agendamento.listar()[:5]
        return render_template("dashboard.html", totais=totais, proximos=proximos)
    except Error:
        app.logger.exception("Erro ao carregar painel")
        flash("Não foi possível consultar o banco. Verifique se o SQL de ajustes foi executado.", "danger")
        return render_template("dashboard.html", totais={"alunos": 0, "planos": 0, "agendamentos": 0}, proximos=[])


@app.route("/alunos", methods=["GET", "POST"])
@login_obrigatorio
def alunos():
    if request.method == "POST":
        nome = limpar_texto(request.form.get("nome"))
        cpf = limpar_texto(request.form.get("cpf"))
        email = limpar_texto(request.form.get("email"))
        telefone = limpar_texto(request.form.get("telefone"))
        if len(nome) < 2 or not validar_cpf(cpf) or not validar_email(email) or not telefone:
            flash("Confira nome, CPF válido, e-mail e telefone.", "danger")
        else:
            try:
                Aluno.criar(nome, cpf, email, telefone)
                flash("Aluno cadastrado com sucesso.", "success")
                return redirect(url_for("alunos"))
            except IntegrityError:
                flash("Já existe um aluno com esse e-mail. Confira também as restrições do banco.", "danger")
            except (ValueError, RuntimeError) as exc:
                flash(str(exc), "danger")
            except Error:
                app.logger.exception("Erro ao cadastrar aluno")
                flash("Não foi possível cadastrar o aluno. Confira o banco e as colunas.", "danger")
    busca = limpar_texto(request.args.get("busca"))
    try:
        lista = Aluno.listar(busca)
    except Error:
        app.logger.exception("Erro ao listar alunos")
        lista = []
        flash("Não foi possível consultar alunos no MySQL.", "danger")
    return render_template("alunos.html", alunos=lista, busca=busca)


@app.route("/alunos/<int:aluno_id>/editar", methods=["GET", "POST"])
@login_obrigatorio
def editar_aluno(aluno_id):
    aluno = Aluno.buscar(aluno_id)
    if not aluno:
        flash("Aluno não encontrado.", "warning")
        return redirect(url_for("alunos"))
    if request.method == "POST":
        nome = limpar_texto(request.form.get("nome"))
        cpf = limpar_texto(request.form.get("cpf"))
        email = limpar_texto(request.form.get("email"))
        telefone = limpar_texto(request.form.get("telefone"))
        if len(nome) < 2 or not validar_cpf(cpf) or not validar_email(email) or not telefone:
            flash("Confira nome, CPF válido, e-mail e telefone.", "danger")
        else:
            try:
                Aluno.atualizar(aluno_id, nome, cpf, email, telefone)
                flash("Dados do aluno atualizados.", "success")
                return redirect(url_for("alunos"))
            except IntegrityError:
                flash("O e-mail informado já está cadastrado.", "danger")
            except (ValueError, RuntimeError) as exc:
                flash(str(exc), "danger")
            except Error:
                app.logger.exception("Erro ao atualizar aluno")
                flash("Não foi possível atualizar o aluno.", "danger")
    return render_template("editar_aluno.html", aluno=aluno)


@app.post("/alunos/<int:aluno_id>/excluir")
@login_obrigatorio
def excluir_aluno(aluno_id):
    try:
        Aluno.excluir(aluno_id)
        flash("Aluno excluído.", "success")
    except IntegrityError:
        flash("Este aluno possui planos ou agendamentos vinculados e não pode ser excluído.", "warning")
    except Error:
        app.logger.exception("Erro ao excluir aluno")
        flash("Não foi possível excluir o aluno.", "danger")
    return redirect(url_for("alunos"))


@app.route("/planos", methods=["GET", "POST"])
@login_obrigatorio
def planos():
    if request.method == "POST":
        descricao = limpar_texto(request.form.get("descricao"))
        objetivo = limpar_texto(request.form.get("objetivo"))
        aluno_id = request.form.get("alunos_id", type=int)
        if not descricao or not aluno_id:
            flash("Informe a descrição e selecione um aluno cadastrado.", "danger")
        elif not Aluno.buscar(aluno_id):
            flash("Selecione um aluno existente.", "danger")
        else:
            try:
                Plano.criar(descricao, objetivo, aluno_id)
                flash("Plano cadastrado com sucesso.", "success")
                return redirect(url_for("planos"))
            except Error:
                app.logger.exception("Erro ao cadastrar plano")
                flash("Não foi possível cadastrar o plano.", "danger")
    try:
        lista = Plano.listar()
        lista_alunos = fetch_all("SELECT id, nome FROM alunos ORDER BY nome")
    except Error:
        app.logger.exception("Erro ao carregar planos")
        lista, lista_alunos = [], []
        flash("Não foi possível consultar planos/alunos no MySQL.", "danger")
    return render_template("planos.html", planos=lista, alunos=lista_alunos)


@app.route("/agendamentos", methods=["GET", "POST"])
@login_obrigatorio
def agendamentos():
    if request.method == "POST":
        data = limpar_texto(request.form.get("data"))
        horario = limpar_texto(request.form.get("horario"))
        observacao = limpar_texto(request.form.get("observacao"))
        plano_id = request.form.get("planos_id", type=int)
        if not validar_data_hora(data, horario) or not observacao or not plano_id:
            flash("Informe uma data, horário, observação e plano válido.", "danger")
        elif not Plano.buscar(plano_id):
            flash("Selecione um plano existente.", "danger")
        else:
            try:
                Agendamento.criar(data, horario, observacao, plano_id)
                flash("Agendamento cadastrado.", "success")
                return redirect(url_for("agendamentos"))
            except Error:
                app.logger.exception("Erro ao cadastrar agendamento")
                flash("Não foi possível cadastrar o agendamento.", "danger")
    try:
        lista = Agendamento.listar()
        lista_planos = Plano.listar()
    except Error:
        app.logger.exception("Erro ao listar agendamentos")
        lista, lista_planos = [], []
        flash("Não foi possível consultar agendamentos no MySQL.", "danger")
    return render_template("agendamentos.html", agendamentos=lista, planos=lista_planos)


@app.route("/agendamentos/<int:agendamento_id>/editar", methods=["GET", "POST"])
@login_obrigatorio
def editar_agendamento(agendamento_id):
    agendamento = Agendamento.buscar(agendamento_id)
    if not agendamento:
        flash("Agendamento não encontrado.", "warning")
        return redirect(url_for("agendamentos"))
    if request.method == "POST":
        data = limpar_texto(request.form.get("data"))
        horario = limpar_texto(request.form.get("horario"))
        observacao = limpar_texto(request.form.get("observacao"))
        plano_id = request.form.get("planos_id", type=int)
        if not validar_data_hora(data, horario) or not observacao or not plano_id:
            flash("Informe uma data, horário, observação e plano válido.", "danger")
        elif not Plano.buscar(plano_id):
            flash("Selecione um plano existente.", "danger")
        else:
            try:
                Agendamento.atualizar(agendamento_id, data, horario, observacao, plano_id)
                flash("Agendamento atualizado.", "success")
                return redirect(url_for("agendamentos"))
            except Error:
                app.logger.exception("Erro ao editar agendamento")
                flash("Não foi possível atualizar o agendamento.", "danger")
    lista_planos = Plano.listar()
    return render_template("editar_agendamento.html", agendamento=agendamento, planos=lista_planos)


@app.get("/api/planos/<int:aluno_id>")
@login_obrigatorio
def api_planos_aluno(aluno_id):
    planos_aluno = fetch_all("SELECT id, descricao, objetivo FROM planos WHERE alunos_id=%s ORDER BY descricao", (aluno_id,))
    return jsonify(planos_aluno)

@app.errorhandler(404)
def pagina_nao_encontrada(erro):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
