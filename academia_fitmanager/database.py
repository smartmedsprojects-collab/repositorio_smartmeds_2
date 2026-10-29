import os
import sqlite3
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "academia_db")

def get_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db

def init_db():
    db = get_db()
    db.executescript("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        senha_hash TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS alunos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT UNIQUE,
        telefone TEXT,
        cpf_criptografado TEXT NOT NULL,
        criado_em TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS planos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        descricao TEXT,
        duracao_semanas INTEGER NOT NULL CHECK(duracao_semanas > 0),
        aluno_id INTEGER NOT NULL,
        FOREIGN KEY(aluno_id) REFERENCES alunos(id) ON UPDATE CASCADE ON DELETE RESTRICT
    );
    CREATE TABLE IF NOT EXISTS agendamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        aluno_id INTEGER NOT NULL,
        plano_id INTEGER NOT NULL,
        data_hora TEXT NOT NULL,
        FOREIGN KEY(aluno_id) REFERENCES alunos(id) ON UPDATE CASCADE ON DELETE RESTRICT,
        FOREIGN KEY(plano_id) REFERENCES planos(id) ON UPDATE CASCADE ON DELETE RESTRICT
    );
    """)
    # Dados de demonstração são inseridos apenas quando as tabelas estão vazias.
    if db.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0] == 0:
        db.executemany("INSERT INTO usuarios (nome,email,senha_hash) VALUES (?,?,?)", [
            ("Administrador", "admin@academia.com", generate_password_hash("Academia@123")),
            ("Recepção", "recepcao@academia.com", generate_password_hash("Recepcao@123")),
            ("Gestor", "gestor@academia.com", generate_password_hash("Gestor@123")),
        ])
    if db.execute("SELECT COUNT(*) FROM alunos").fetchone()[0] == 0:
        from app import criptografar_cpf
        exemplos = [
            ("Ana Souza","ana@example.com","11988887777","12345678901"),
            ("Bruno Lima","bruno@example.com","11977776666","23456789012"),
            ("Carla Mendes","carla@example.com","11966665555","34567890123"),
        ]
        from datetime import datetime
        for nome,email,telefone,cpf in exemplos:
            db.execute("INSERT INTO alunos (nome,email,telefone,cpf_criptografado,criado_em) VALUES (?,?,?,?,?)",
                       (nome,email,telefone,criptografar_cpf(cpf),datetime.now().isoformat(timespec="minutes")))
    if db.execute("SELECT COUNT(*) FROM planos").fetchone()[0] == 0:
        ids = db.execute("SELECT id FROM alunos ORDER BY id LIMIT 3").fetchall()
        nomes = [("Musculação iniciante","Adaptação e técnica",8),("Condicionamento","Resistência cardiovascular",12),("Hipertrofia","Treino de força progressivo",16)]
        for aluno, (nome,desc,duracao) in zip(ids, nomes):
            db.execute("INSERT INTO planos (nome,descricao,duracao_semanas,aluno_id) VALUES (?,?,?,?)",
                       (nome,desc,duracao,aluno["id"]))
    if db.execute("SELECT COUNT(*) FROM agendamentos").fetchone()[0] == 0:
        pares = db.execute("SELECT id,aluno_id FROM planos ORDER BY id LIMIT 3").fetchall()
        datas = ["2026-10-28T08:00","2026-10-28T10:00","2026-10-29T18:30"]
        for plano, data in zip(pares,datas):
            db.execute("INSERT INTO agendamentos (aluno_id,plano_id,data_hora) VALUES (?,?,?)",
                       (plano["aluno_id"],plano["id"],data))
    db.commit()
    db.close()
