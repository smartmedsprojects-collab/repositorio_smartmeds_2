-- Esquema SQL de referência para SQLite. O aplicativo cria estas tabelas automaticamente.
PRAGMA foreign_keys = ON;

CREATE TABLE usuarios (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nome TEXT NOT NULL,
  email TEXT NOT NULL UNIQUE,
  senha_hash TEXT NOT NULL
);

CREATE TABLE alunos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nome TEXT NOT NULL,
  email TEXT UNIQUE,
  telefone TEXT,
  cpf_criptografado TEXT NOT NULL,
  criado_em TEXT NOT NULL
);

CREATE TABLE planos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nome TEXT NOT NULL,
  descricao TEXT,
  duracao_semanas INTEGER NOT NULL CHECK (duracao_semanas > 0),
  aluno_id INTEGER NOT NULL,
  FOREIGN KEY (aluno_id) REFERENCES alunos(id) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE agendamentos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  aluno_id INTEGER NOT NULL,
  plano_id INTEGER NOT NULL,
  data_hora TEXT NOT NULL,
  FOREIGN KEY (aluno_id) REFERENCES alunos(id) ON UPDATE CASCADE ON DELETE RESTRICT,
  FOREIGN KEY (plano_id) REFERENCES planos(id) ON UPDATE CASCADE ON DELETE RESTRICT
);

-- Três registros de demonstração de cada tabela são inseridos pelo init_db() do aplicativo.
