const express = require('express');
const mysql = require('mysql2/promise');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

// Configuração da Conexão com o MySQL
const db = mysql.createPool({
  host: 'localhost',
  user: 'sergio',      // Altere para seu usuário do MySQL
  password: 'sergio',      // Altere para sua senha do MySQL
  database: 'stockpro_db',
  waitForConnections: true,
  connectionLimit: 10,
});

// 1. Rota de Login
app.post('/api/login', async (req, res) => {
  const { email, password } = req.body;
  try {
    const [rows] = await db.query(
      'SELECT id, name, email, role FROM users WHERE email = ? AND password = ?',
      [email, password]
    );
    if (rows.length > 0) {
      res.json({ success: true, user: rows[0] });
    } else {
      res.status(401).json({ success: false, message: 'Credenciais inválidas.' });
    }
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 2. Rota de Dashboard (Resumo)
app.get('/api/dashboard', async (req, res) => {
  try {
    const [[{ totalProducts }]] = await db.query('SELECT SUM(stock) as totalProducts FROM products');
    const [[{ lowStockCount }]] = await db.query('SELECT COUNT(*) as lowStockCount FROM products WHERE stock <= 5');
    const [recentActivities] = await db.query(`
      SELECT h.id, h.type, h.quantity, p.name as product 
      FROM history h 
      JOIN products p ON h.product_id = p.id 
      ORDER BY h.id DESC LIMIT 5
    `);

    res.json({
      totalProducts: totalProducts || 0,
      lowStockCount: lowStockCount || 0,
      recentActivities,
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 3. Listar Produtos
app.get('/api/products', async (req, res) => {
  try {
    const [products] = await db.query('SELECT * FROM products ORDER BY name ASC');
    res.json(products);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 4. Buscar Produto Específico por ID ou Código
app.get('/api/products/:identifier', async (req, res) => {
  const { identifier } = req.params;
  try {
    const [rows] = await db.query(
      'SELECT * FROM products WHERE id = ? OR code = ?',
      [identifier, identifier]
    );
    if (rows.length > 0) {
      res.json(rows[0]);
    } else {
      res.status(404).json({ message: 'Produto não encontrado' });
    }
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// 5. Movimentação de Estoque (Entrada / Saída)
app.post('/api/stock/move', async (req, res) => {
  const { productId, type, quantity } = req.body;
  const qtyNum = parseInt(quantity, 10);

  if (!productId || !type || isNaN(qtyNum) || qtyNum <= 0) {
    return res.status(400).json({ message: 'Dados inválidos.' });
  }

  const connection = await db.getConnection();
  try {
    await connection.beginTransaction();

    // Atualiza estoque
    const sqlStock = type === 'Entrada'
      ? 'UPDATE products SET stock = stock + ? WHERE id = ?'
      : 'UPDATE products SET stock = stock - ? WHERE id = ? AND stock >= ?';

    const params = type === 'Entrada' ? [qtyNum, productId] : [qtyNum, productId, qtyNum];
    const [result] = await connection.query(sqlStock, params);

    if (result.affectedRows === 0) {
      await connection.rollback();
      return res.status(400).json({ message: 'Estoque insuficiente ou produto não encontrado.' });
    }

    // Registra Histórico
    const now = new Date();
    const dateStr = now.toLocaleDateString('pt-BR');
    const hourStr = now.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });

    await connection.query(
      'INSERT INTO history (product_id, type, quantity, date, hour) VALUES (?, ?, ?, ?, ?)',
      [productId, type, qtyNum, dateStr, hourStr]
    );

    await connection.commit();
    res.json({ success: true, message: 'Movimentação realizada com sucesso!' });
  } catch (error) {
    await connection.rollback();
    res.status(500).json({ error: error.message });
  } finally {
    connection.release();
  }
});

// 6. Listar Histórico Completo
app.get('/api/history', async (req, res) => {
  try {
    const [rows] = await db.query(`
      SELECT h.id, h.type, h.quantity, h.date, h.hour, p.name as product
      FROM history h
      JOIN products p ON h.product_id = p.id
      ORDER BY h.id DESC
    `);
    res.json(rows);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

const PORT = 3000;
app.listen(PORT, () => console.log(`Servidor rodando em http://localhost:${PORT}`));