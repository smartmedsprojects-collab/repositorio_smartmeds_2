import os
from datetime import datetime, timedelta
from functools import wraps

from cryptography.fernet import Fernet, InvalidToken
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import check_password_hash, generate_password_hash

from database import get_db, init_db

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "troque-esta-chave-antes-de-publicar")
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.environ.get("COOKIE_SECURE", "0") == "1"
CSRFProtect(app)

def get_cipher():
    key = os.environ.get("CPF_ENCRYPTION_KEY")
    if not key:
        key_path = os.path.join(BASE_DIR, "cpf.key")
        if not os.path.exists(key_path):
            with open(key_path, "wb") as f:
                f.write(Fernet.generate_key())
            try:
                os.chmod(key_path, 0o600)
            except OSError:
                pass
        with open(key_path, "rb") as f:
            key = f.read().strip().decode()
    return Fernet(key.encode() if isinstance(key, str) else key)

def criptografar_cpf(cpf):
    return get_cipher().encrypt("".join(c for c in cpf if c.isdigit()).encode()).decode()

def descriptografar_cpf(valor):
    try:
        return get_cipher().decrypt(valor.encode()).decode()
    except (InvalidToken, ValueError):
        return ""

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Faça login para acessar o sistema.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped

@app.before_request
def enforce_session_expiration():
    if session.get("user_id"):
        now = datetime.utcnow().timestamp()
        last = session.get("last_activity", now)
        if now - last > app.config["PERMANENT_SESSION_LIFETIME"].total_seconds():
            session.clear()
            flash("Sua sessão expirou. Entre novamente.", "warning")
            if request.endpoint != "login":
                return redirect(url_for("login"))
        else:
            session["last_activity"] = now

@app.route("/")
def index():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")
        db = get_db()
        user = db.execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()
        db.close()
        if user and check_password_hash(user["senha_hash"], senha):
            session.clear()
            session.permanent = True
            session["user_id"] = user["id"]
            session["user_name"] = user["nome"]
            session["last_activity"] = datetime.utcnow().timestamp()
            return redirect(url_for("dashboard"))
        flash("E-mail ou senha inválidos. Confira os dados e tente novamente.", "danger")
    return render_template("login.html")

@app.route("/sair", methods=["POST"])
@login_required
def logout():
    session.clear()
    flash("Você saiu do sistema com segurança.", "success")
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    stats = {
        "alunos": db.execute("SELECT COUNT(*) FROM alunos").fetchone()[0],
        "planos": db.execute("SELECT COUNT(*) FROM planos").fetchone()[0],
        "agendamentos": db.execute("SELECT COUNT(*) FROM agendamentos").fetchone()[0],
    }
    proximos = db.execute("""
        SELECT ag.id, ag.data_hora, a.nome AS aluno, p.nome AS plano
        FROM agendamentos ag
        JOIN alunos a ON a.id = ag.aluno_id
        JOIN planos p ON p.id = ag.plano_id
        WHERE ag.data_hora >= ?
        ORDER BY ag.data_hora LIMIT 5
    """, (datetime.now().strftime("%Y-%m-%dT%H:%M"),)).fetchall()
    db.close()
    return render_template("dashboard.html", stats=stats, proximos=proximos)

@app.route("/alunos", methods=["GET", "POST"])
@login_required
def alunos():
    db = get_db()
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()
        telefone = request.form.get("telefone", "").strip()
        cpf = "".join(c for c in request.form.get("cpf", "") if c.isdigit())
        if len(nome) < 2 or len(cpf) != 11:
            flash("Informe um nome válido e um CPF com 11 dígitos.", "danger")
        else:
            try:
                db.execute("INSERT INTO alunos (nome,email,telefone,cpf_criptografado,criado_em) VALUES (?,?,?,?,?)",
                           (nome, email, telefone, criptografar_cpf(cpf), datetime.now().isoformat(timespec="minutes")))
                db.commit()
                flash("Aluno cadastrado com sucesso.", "success")
                db.close()
                return redirect(url_for("alunos"))
            except Exception:
                db.rollback()
                flash("Não foi possível cadastrar. Verifique se o e-mail já está em uso.", "danger")
    termo = request.args.get("q", "").strip()
    if termo:
        rows = db.execute("SELECT * FROM alunos WHERE nome LIKE ? OR email LIKE ? OR telefone LIKE ? ORDER BY nome",
                          (f"%{termo}%", f"%{termo}%", f"%{termo}%")).fetchall()
    else:
        rows = db.execute("SELECT * FROM alunos ORDER BY nome").fetchall()
    lista = []
    for row in rows:
        item = dict(row)
        cpf = descriptografar_cpf(item.pop("cpf_criptografado"))
        item["cpf_exibicao"] = f"***.***.{cpf[6:9]}-{cpf[9:]}" if len(cpf) == 11 else "Indisponível"
        lista.append(item)
    db.close()
    return render_template("alunos.html", alunos=lista, termo=termo)

@app.route("/alunos/<int:aluno_id>/editar", methods=["GET", "POST"])
@login_required
def editar_aluno(aluno_id):
    db = get_db()
    aluno = db.execute("SELECT * FROM alunos WHERE id=?", (aluno_id,)).fetchone()
    if not aluno:
        db.close()
        flash("Aluno não encontrado.", "danger")
        return redirect(url_for("alunos"))
    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip().lower()
        telefone = request.form.get("telefone", "").strip()
        cpf = "".join(c for c in request.form.get("cpf", "") if c.isdigit())
        if len(nome) < 2 or (cpf and len(cpf) != 11):
            flash("Confira o nome e informe um CPF válido com 11 dígitos, se desejar alterá-lo.", "danger")
        else:
            try:
                if cpf:
                    db.execute("UPDATE alunos SET nome=?,email=?,telefone=?,cpf_criptografado=? WHERE id=?",
                               (nome,email,telefone,criptografar_cpf(cpf),aluno_id))
                else:
                    db.execute("UPDATE alunos SET nome=?,email=?,telefone=? WHERE id=?",(nome,email,telefone,aluno_id))
                db.commit()
                db.close()
                flash("Dados do aluno atualizados.", "success")
                return redirect(url_for("alunos"))
            except Exception:
                db.rollback()
                flash("Não foi possível salvar. Verifique se o e-mail já está em uso.", "danger")
    db.close()
    return render_template("editar_aluno.html", aluno=aluno)

@app.route("/planos", methods=["GET", "POST"])
@login_required
def planos():
    db = get_db()
    if request.method == "POST":
        aluno_id = request.form.get("aluno_id", type=int)
        nome = request.form.get("nome", "").strip()
        descricao = request.form.get("descricao", "").strip()
        duracao = request.form.get("duracao_semanas", type=int)
        if not aluno_id or not nome or not duracao or duracao < 1:
            flash("Preencha o nome, a duração e selecione um aluno cadastrado.", "danger")
        elif not db.execute("SELECT id FROM alunos WHERE id=?", (aluno_id,)).fetchone():
            flash("Selecione um aluno existente.", "danger")
        else:
            db.execute("INSERT INTO planos (nome,descricao,duracao_semanas,aluno_id) VALUES (?,?,?,?)",
                       (nome,descricao,duracao,aluno_id))
            db.commit()
            db.close()
            flash("Plano cadastrado com sucesso.", "success")
            return redirect(url_for("planos"))
    lista = db.execute("""SELECT p.*, a.nome AS aluno_nome FROM planos p
                          JOIN alunos a ON a.id=p.aluno_id ORDER BY p.nome""").fetchall()
    alunos_lista = db.execute("SELECT id,nome FROM alunos ORDER BY nome").fetchall()
    db.close()
    return render_template("planos.html", planos=lista, alunos=alunos_lista)

@app.route("/agendamentos", methods=["GET", "POST"])
@login_required
def agendamentos():
    db = get_db()
    if request.method == "POST":
        aluno_id = request.form.get("aluno_id", type=int)
        plano_id = request.form.get("plano_id", type=int)
        data_hora = request.form.get("data_hora", "").strip()
        if not aluno_id or not plano_id or not data_hora:
            flash("Preencha o aluno, o plano e a data do agendamento.", "danger")
        else:
            plano = db.execute("SELECT id FROM planos WHERE id=? AND aluno_id=?", (plano_id,aluno_id)).fetchone()
            if not plano:
                flash("O plano selecionado não pertence ao aluno escolhido.", "danger")
            else:
                try:
                    datetime.strptime(data_hora, "%Y-%m-%dT%H:%M")
                    db.execute("INSERT INTO agendamentos (aluno_id,plano_id,data_hora) VALUES (?,?,?)",
                               (aluno_id,plano_id,data_hora))
                    db.commit()
                    db.close()
                    flash("Agendamento criado com sucesso.", "success")
                    return redirect(url_for("agendamentos"))
                except ValueError:
                    flash("Data e horário inválidos.", "danger")
    lista = db.execute("""SELECT ag.id,ag.data_hora,a.nome AS aluno_nome,p.nome AS plano_nome
                          FROM agendamentos ag JOIN alunos a ON a.id=ag.aluno_id
                          JOIN planos p ON p.id=ag.plano_id ORDER BY ag.data_hora""").fetchall()
    alunos_lista = db.execute("SELECT id,nome FROM alunos ORDER BY nome").fetchall()
    planos_lista = db.execute("SELECT id,nome,aluno_id FROM planos ORDER BY nome").fetchall()
    db.close()
    return render_template("agendamentos.html", agendamentos=lista, alunos=alunos_lista, planos=planos_lista)

@app.route("/agendamentos/<int:agendamento_id>/editar", methods=["GET", "POST"])
@login_required
def editar_agendamento(agendamento_id):
    db = get_db()
    ag = db.execute("SELECT * FROM agendamentos WHERE id=?", (agendamento_id,)).fetchone()
    if not ag:
        db.close()
        flash("Agendamento não encontrado.", "danger")
        return redirect(url_for("agendamentos"))
    if request.method == "POST":
        data_hora = request.form.get("data_hora", "").strip()
        try:
            datetime.strptime(data_hora, "%Y-%m-%dT%H:%M")
            db.execute("UPDATE agendamentos SET data_hora=? WHERE id=?", (data_hora,agendamento_id))
            db.commit()
            db.close()
            flash("Data do agendamento atualizada.", "success")
            return redirect(url_for("agendamentos"))
        except ValueError:
            flash("Informe uma data e horário válidos.", "danger")
    db.close()
    return render_template("editar_agendamento.html", agendamento=ag)

@app.route("/api/planos/<int:aluno_id>")
@login_required
def api_planos(aluno_id):
    db = get_db()
    rows = db.execute("SELECT id,nome FROM planos WHERE aluno_id=? ORDER BY nome",(aluno_id,)).fetchall()
    db.close()
    return {"planos":[dict(r) for r in rows]}

@app.cli.command("init-db")
def init_db_command():
    init_db()
    print("Banco inicializado com dados de demonstração.")

if __name__ == "__main__":
    init_db()
    app.run(debug=os.environ.get("FLASK_DEBUG", "0") == "1")
