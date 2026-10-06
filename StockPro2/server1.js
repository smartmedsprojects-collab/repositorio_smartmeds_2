const express = require('express');
const mysql = require('mysql2/promise');
const cors = require('cors');
const bcrypt = require('bcrypt');

const app = express();

app.use(cors());
app.use(express.json());

const db = mysql.createPool({
    host: 'localhost',
    user: 'root',
    password: '123456',
    database: 'smartmeds',
    waitForConnections: true,
    connectionLimit: 10,
});

// CORREÇÃO 1 e 2: Ajustado para /api/login e mapeamento correto de colunas (nome, senha)
app.post('/api/login', async (req, res) => {
  const { email, password } = req.body;

  if (!email || !password) {
    return res.status(400).json({
      success: false,
      message: 'E-mail e senha são obrigatórios.'
    });
  }

  try {
    // Ajustado para buscar 'nome' e 'senha' de acordo com o padrão do seu banco
    const [rows] = await db.query(
      'SELECT id, nome, email, senha FROM usuario WHERE email = ?',
      [email]
    );

    if (rows.length === 0) {
      return res.status(401).json({
        success: false,
        message: 'Credenciais inválidas.'
      });
    }

    const user = rows[0];

    // Compara a senha digitada com o hash criptografado no banco
    const passwordValid = await bcrypt.compare(
      password,
      user.senha
    );

    if (!passwordValid) {
      return res.status(401).json({
        success: false,
        message: 'Credenciais inválidas.'
      });
    }

    res.json({
      success: true,
      message: 'Login realizado com sucesso.',
      user: {
        id: user.id,
        nome: user.nome,
        email: user.email
      }
    });

  } catch (error) {
    console.error('Erro no login:', error);

    res.status(500).json({
      success: false,
      message: 'Erro interno do servidor.',
      error: error.message
    });
  }
});

app.get('/api/usuarios', async (req, res) => {
    try {
        const [usuarios] = await db.query(
            `
            SELECT id, nome, email
            FROM usuario
            ORDER BY nome ASC
            `
        );
        res.json(usuarios);
    } catch (error) {
        console.error('Erro ao buscar usuários:', error);
        res.status(500).json({ message: 'Erro ao carregar usuários.', error: error.message });
    }
});

app.get('/api/dashboard', async (req, res) => {
    try {
        const [[resultadoProdutos]] = await db.query('SELECT COUNT(*) AS totalProdutos FROM produto');
        const [[resultadoMovimentacoes]] = await db.query('SELECT COUNT(*) AS totalMovimentacoes FROM movimentacao');
        const [movimentacoes] = await db.query('SELECT * FROM movimentacao ORDER BY id DESC LIMIT 5');

        res.json({
            totalProdutos: resultadoProdutos.totalProdutos || 0,
            totalMovimentacoes: resultadoMovimentacoes.totalMovimentacoes || 0,
            movimentacoes: movimentacoes
        });
    } catch (error) {
        console.error('Erro no dashboard:', error);
        res.status(500).json({ message: 'Erro ao carregar dashboard.', error: error.message });
    }
});

app.get('/api/produtos', async (req, res) => {
    try {
        const [produtos] = await db.query('SELECT * FROM produto ORDER BY id DESC');
        res.json(produtos);
    } catch (error) {
        console.error('Erro ao buscar produtos:', error);
        res.status(500).json({ message: 'Erro ao carregar produtos.', error: error.message });
    }
});

app.get('/api/produtos/:id', async (req, res) => {
    const { id } = req.params;
    try {
        const [produtos] = await db.query('SELECT * FROM produto WHERE id = ?', [id]);
        if (produtos.length === 0) {
            return res.status(404).json({ message: 'Produto não encontrado.' });
        }
        res.json(produtos[0]);
    } catch (error) {
        console.error('Erro ao buscar produto:', error);
        res.status(500).json({ message: 'Erro ao buscar produto.', error: error.message });
    }
});

app.get('/api/clientes', async (req, res) => {
    try {
        const [clientes] = await db.query('SELECT id, nome, email, cnpj, usuario_id FROM cliente ORDER BY nome ASC');
        res.json(clientes);
    } catch (error) {
        console.error('Erro ao buscar clientes:', error);
        res.status(500).json({ message: 'Erro ao carregar clientes.', error: error.message });
    }
});

app.get('/api/localizacoes', async (req, res) => {
    try {
        const [localizacoes] = await db.query('SELECT * FROM localizacao ORDER BY id DESC');
        res.json(localizacoes);
    } catch (error) {
        console.error('Erro ao buscar localizações:', error);
        res.status(500).json({ message: 'Erro ao carregar localizações.', error: error.message });
    }
});

app.get('/api/entradas', async (req, res) => {
    try {
        const [entradas] = await db.query('SELECT * FROM pedido_entrada ORDER BY id DESC');
        res.json(entradas);
    } catch (error) {
        console.error('Erro ao buscar entradas:', error);
        res.status(500).json({ message: 'Erro ao carregar entradas.', error: error.message });
    }
});

app.get('/api/itens-entrada', async (req, res) => {
    try {
        const [itens] = await db.query('SELECT * FROM item_entrada ORDER BY id DESC');
        res.json(itens);
    } catch (error) {
        console.error('Erro ao buscar itens de entrada:', error);
        res.status(500).json({ message: 'Erro ao carregar itens de entrada.', error: error.message });
    }
});

app.get('/api/saidas', async (req, res) => {
    try {
        const [saidas] = await db.query('SELECT * FROM pedido_saida ORDER BY id DESC');
        res.json(saidas);
    } catch (error) {
        console.error('Erro ao buscar saídas:', error);
        res.status(500).json({ message: 'Erro ao carregar saídas.', error: error.message });
    }
});

app.get('/api/itens-saida', async (req, res) => {
    try {
        const [itens] = await db.query('SELECT * FROM item_saida ORDER BY id DESC');
        res.json(itens);
    } catch (error) {
        console.error('Erro ao buscar itens de saída:', error);
        res.status(500).json({ message: 'Erro ao carregar itens de saída.', error: error.message });
    }
});

app.get('/api/movimentacoes', async (req, res) => {
    try {
        const [movimentacoes] = await db.query('SELECT * FROM movimentacao ORDER BY id DESC');
        res.json(movimentacoes);
    } catch (error) {
        console.error('Erro ao buscar movimentações:', error);
        res.status(500).json({ message: 'Erro ao carregar movimentações.', error: error.message });
    }
});

const PORT = 3000;

// CORREÇÃO 3: Escuta em '0.0.0.0' para aceitar chamadas de celulares e emuladores da rede
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Servidor SmartMeds rodando na porta ${PORT}`);
});