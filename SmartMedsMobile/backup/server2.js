const express = require('express');
const mysql = require('mysql2/promise');
const cors = require('cors');
const bcrypt = require('bcrypt');

const app = express();

app.use(cors());
app.use(express.json());


// =====================================================
// CONEXÃO COM O BANCO
// =====================================================

const db = mysql.createPool({
    host: 'localhost',
    user: 'root',
    password: '123456',
    database: 'smartmeds3',
    waitForConnections: true,
    connectionLimit: 10,
});


// =====================================================
// LOGIN
// =====================================================

app.post('/api/login', async (req, res) => {

    const { email, senha } = req.body;

    if (!email || !senha) {
        return res.status(400).json({
            success: false,
            message: 'Email e senha são obrigatórios.'
        });
    }

    try {

        const [rows] = await db.query(
            `
            SELECT
                id,
                nome,
                email,
                senha,
                tipo,
                identificacao,
                permissao
            FROM usuario
            WHERE email = ?
            `,
            [email]
        );

        if (rows.length === 0) {
            return res.status(401).json({
                success: false,
                message: 'Credenciais inválidas.'
            });
        }

        const usuario = rows[0];

        const senhaCorreta = await bcrypt.compare(
            senha,
            usuario.senha
        );

        if (!senhaCorreta) {
            return res.status(401).json({
                success: false,
                message: 'Credenciais inválidas.'
            });
        }

        delete usuario.senha;

        return res.json({
            success: true,
            user: usuario
        });

    } catch (error) {

        console.error(
            'Erro no login:',
            error
        );

        return res.status(500).json({
            success: false,
            message: 'Erro ao realizar login.',
            error: error.message
        });
    }
});


// =====================================================
// DASHBOARD
// =====================================================

app.get('/api/dashboard', async (req, res) => {

    try {

        const [[resultadoProdutos]] =
            await db.query(
                `
                SELECT COUNT(*) AS totalProdutos
                FROM produto
                `
            );

        const [[resultadoMovimentacoes]] =
            await db.query(
                `
                SELECT COUNT(*) AS totalMovimentacoes
                FROM movimentacao
                `
            );

        const [movimentacoes] =
            await db.query(
                `
                SELECT *
                FROM movimentacao
                ORDER BY id DESC
                LIMIT 5
                `
            );

        return res.json({
            totalProdutos:
                resultadoProdutos.totalProdutos || 0,

            totalMovimentacoes:
                resultadoMovimentacoes.totalMovimentacoes || 0,

            movimentacoes:
                movimentacoes
        });

    } catch (error) {

        console.error(
            'Erro no dashboard:',
            error
        );

        return res.status(500).json({
            message: 'Erro ao carregar dashboard.',
            error: error.message
        });
    }
});


// =====================================================
// PRODUTOS
// =====================================================

app.get('/api/produtos', async (req, res) => {

    try {

        const [produtos] =
            await db.query(
                `
                SELECT *
                FROM produto
                ORDER BY nome ASC
                `
            );

        return res.json(produtos);

    } catch (error) {

        console.error(
            'Erro ao buscar produtos:',
            error
        );

        return res.status(500).json({
            message: 'Erro ao carregar produtos.',
            error: error.message
        });
    }
});


// =====================================================
// PRODUTO POR ID
// =====================================================

app.get('/api/produtos/:id', async (req, res) => {

    const { id } = req.params;

    try {

        const [produtos] =
            await db.query(
                `
                SELECT *
                FROM produto
                WHERE id = ?
                `,
                [id]
            );

        if (produtos.length === 0) {

            return res.status(404).json({
                message: 'Produto não encontrado.'
            });
        }

        return res.json(produtos[0]);

    } catch (error) {

        console.error(
            'Erro ao buscar produto:',
            error
        );

        return res.status(500).json({
            message: 'Erro ao buscar produto.',
            error: error.message
        });
    }
});


// =====================================================
// CLIENTES
// =====================================================

app.get('/api/clientes', async (req, res) => {

    try {

        const [clientes] =
            await db.query(
                `
                SELECT
                    id,
                    nome,
                    email,
                    cnpj,
                    usuario_id
                FROM cliente
                ORDER BY nome ASC
                `
            );

        return res.json(clientes);

    } catch (error) {

        console.error(
            'Erro ao buscar clientes:',
            error
        );

        return res.status(500).json({
            message: 'Erro ao carregar clientes.',
            error: error.message
        });
    }
});


// =====================================================
// LOCALIZAÇÕES
// =====================================================

app.get('/api/localizacoes', async (req, res) => {

    try {

        const [localizacoes] =
            await db.query(
                `
                SELECT *
                FROM localizacao
                ORDER BY id DESC
                `
            );

        return res.json(localizacoes);

    } catch (error) {

        console.error(
            'Erro ao buscar localizações:',
            error
        );

        return res.status(500).json({
            message: 'Erro ao carregar localizações.',
            error: error.message
        });
    }
});


// =====================================================
// ENTRADAS - LISTAGEM
// =====================================================

app.get('/api/entradas', async (req, res) => {

    try {

        const [entradas] =
            await db.query(
                `
                SELECT *
                FROM pedido_entrada
                ORDER BY id_pedido_entrada DESC
                `
            );

        return res.json(entradas);

    } catch (error) {

        console.error(
            'Erro ao buscar entradas:',
            error
        );

        return res.status(500).json({
            message: 'Erro ao carregar entradas.',
            error: error.message
        });
    }
});


// =====================================================
// ITENS DE ENTRADA
// =====================================================

app.get('/api/itens-entrada', async (req, res) => {

    try {

        const [itens] =
            await db.query(
                `
                SELECT *
                FROM item_entrada
                ORDER BY id DESC
                `
            );

        return res.json(itens);

    } catch (error) {

        console.error(
            'Erro ao buscar itens de entrada:',
            error
        );

        return res.status(500).json({
            message: 'Erro ao carregar itens de entrada.',
            error: error.message
        });
    }
});


// =====================================================
// SAÍDAS - LISTAGEM
// =====================================================

app.get('/api/saidas', async (req, res) => {

    try {

        const [saidas] =
            await db.query(
                `
                SELECT *
                FROM pedido_saida
                ORDER BY id DESC
                `
            );

        return res.json(saidas);

    } catch (error) {

        console.error(
            'Erro ao buscar saídas:',
            error
        );

        return res.status(500).json({
            message: 'Erro ao carregar saídas.',
            error: error.message
        });
    }
});


// =====================================================
// ITENS DE SAÍDA
// =====================================================

app.get('/api/itens-saida', async (req, res) => {

    try {

        const [itens] =
            await db.query(
                `
                SELECT *
                FROM item_saida
                ORDER BY id DESC
                `
            );

        return res.json(itens);

    } catch (error) {

        console.error(
            'Erro ao buscar itens de saída:',
            error
        );

        return res.status(500).json({
            message: 'Erro ao carregar itens de saída.',
            error: error.message
        });
    }
});


// =====================================================
// MOVIMENTAÇÕES
// =====================================================

app.get('/api/movimentacoes', async (req, res) => {

    try {

        const [movimentacoes] =
            await db.query(
                `
                SELECT *
                FROM movimentacao
                ORDER BY id DESC
                `
            );

        return res.json(movimentacoes);

    } catch (error) {

        console.error(
            'Erro ao buscar movimentações:',
            error
        );

        return res.status(500).json({
            message: 'Erro ao carregar movimentações.',
            error: error.message
        });
    }
});


// =====================================================
// HISTÓRICO PARA O APLICATIVO
// =====================================================

app.get('/api/history', async (req, res) => {

    try {

        const [movimentacoes] =
            await db.query(
                `
                SELECT
                    m.id,
                    m.tipo_movimentacao,
                    m.data_movimentacao,
                    m.quantidade,
                    m.produto_id,
                    p.nome AS produto_nome
                FROM movimentacao AS m
                LEFT JOIN produto AS p
                    ON p.id = m.produto_id
                ORDER BY m.id DESC
                `
            );


        const historico =
            movimentacoes.map((item) => {

                const tipoBanco =
                    String(
                        item.tipo_movimentacao || ''
                    ).toUpperCase();


                const tipo =
                    tipoBanco === 'SAIDA' ||
                    tipoBanco === 'SAÍDA'
                        ? 'Saída'
                        : 'Entrada';


                let dataFormatada = '';
                let horaFormatada = '';


                if (item.data_movimentacao) {

                    const data =
                        new Date(
                            item.data_movimentacao
                        );


                    if (!Number.isNaN(data.getTime())) {

                        dataFormatada =
                            data.toLocaleDateString(
                                'pt-BR'
                            );


                        horaFormatada =
                            data.toLocaleTimeString(
                                'pt-BR',
                                {
                                    hour: '2-digit',
                                    minute: '2-digit'
                                }
                            );
                    }
                }


                return {

                    id: item.id,

                    product:
                        item.produto_nome ||
                        `Produto #${item.produto_id}`,

                    type:
                        tipo,

                    quantity:
                        Number(item.quantidade) || 0,

                    date:
                        dataFormatada,

                    hour:
                        horaFormatada
                };
            });


        return res.json(historico);

    } catch (error) {

        console.error(
            'Erro ao carregar histórico:',
            error
        );

        return res.status(500).json({

            success: false,

            message:
                'Erro ao carregar histórico.',

            error:
                error.message
        });
    }
});


// =====================================================
// REGISTRAR ENTRADA
// =====================================================

app.post('/api/entradas', async (req, res) => {

    const {
        produto_id,
        quantidade,
        usuario_id
    } = req.body;


    if (!produto_id || !quantidade) {

        return res.status(400).json({
            success: false,
            message:
                'produto_id e quantidade são obrigatórios.'
        });
    }


    const quantidadeEntrada =
        Number(quantidade);


    if (
        !Number.isInteger(quantidadeEntrada) ||
        quantidadeEntrada <= 0
    ) {

        return res.status(400).json({
            success: false,
            message:
                'A quantidade deve ser um número inteiro maior que zero.'
        });
    }


    const usuarioId =
        Number(usuario_id) || 15;


    let connection;


    try {

        connection =
            await db.getConnection();

        await connection.beginTransaction();


        // Buscar produto
        const [produtos] =
            await connection.query(
                `
                SELECT
                    id,
                    nome,
                    quantidade
                FROM produto
                WHERE id = ?
                FOR UPDATE
                `,
                [produto_id]
            );


        if (produtos.length === 0) {

            await connection.rollback();

            return res.status(404).json({
                success: false,
                message:
                    'Produto não encontrado.'
            });
        }


        const produto =
            produtos[0];


        const estoqueAtual =
            Number(produto.quantidade) || 0;


        const novoEstoque =
            estoqueAtual +
            quantidadeEntrada;


        // Atualizar estoque
        await connection.query(
            `
            UPDATE produto
            SET quantidade = ?
            WHERE id = ?
            `,
            [
                novoEstoque,
                produto_id
            ]
        );


        // Criar movimentação
        const [movimentacaoResult] =
            await connection.query(
                `
                INSERT INTO movimentacao
                (
                    tipo_movimentacao,
                    data_movimentacao,
                    quantidade,
                    produto_id
                )
                VALUES
                (
                    'ENTRADA',
                    NOW(),
                    ?,
                    ?
                )
                `,
                [
                    quantidadeEntrada,
                    produto_id
                ]
            );


        const movimentacaoId =
            movimentacaoResult.insertId;


        // Criar pedido de entrada
        const [pedidoResult] =
            await connection.query(
                `
                INSERT INTO pedido_entrada
                (
                    numero_documento,
                    fornecedor,
                    data_entrada,
                    usuario_id,
                    observacao,
                    status
                )
                VALUES
                (
                    NULL,
                    NULL,
                    CURDATE(),
                    ?,
                    NULL,
                    'ABERTO'
                )
                `,
                [
                    usuarioId
                ]
            );


        const pedidoEntradaId =
            pedidoResult.insertId;


        // Criar item de entrada
        await connection.query(
            `
            INSERT INTO item_entrada
            (
                quantidade,
                valor,
                pedido_entrada_id,
                movimentacao_id
            )
            VALUES
            (
                ?,
                NULL,
                ?,
                ?
            )
            `,
            [
                quantidadeEntrada,
                pedidoEntradaId,
                movimentacaoId
            ]
        );


        await connection.commit();


        console.log(
            `Entrada registrada: produto ${produto_id} | ` +
            `+${quantidadeEntrada} | ` +
            `estoque: ${novoEstoque}`
        );


        return res.json({

            success: true,

            message:
                'Entrada registrada com sucesso.',

            produto: {

                id:
                    produto.id,

                nome:
                    produto.nome,

                quantidadeAnterior:
                    estoqueAtual,

                quantidadeEntrada:
                    quantidadeEntrada,

                quantidadeAtual:
                    novoEstoque
            },

            movimentacaoId:
                movimentacaoId,

            pedidoEntradaId:
                pedidoEntradaId
        });


    } catch (error) {

        if (connection) {
            await connection.rollback();
        }

        console.error(
            'Erro ao registrar entrada:',
            error
        );

        return res.status(500).json({

            success: false,

            message:
                'Erro ao registrar entrada.',

            error:
                error.message
        });

    } finally {

        if (connection) {
            connection.release();
        }
    }
});


// =====================================================
// REGISTRAR SAÍDA
// =====================================================

app.post('/api/saidas', async (req, res) => {

    const {
        produto_id,
        quantidade,
        usuario_id
    } = req.body;


    if (!produto_id || !quantidade) {

        return res.status(400).json({
            success: false,
            message:
                'produto_id e quantidade são obrigatórios.'
        });
    }


    const quantidadeSaida =
        Number(quantidade);


    if (
        !Number.isInteger(quantidadeSaida) ||
        quantidadeSaida <= 0
    ) {

        return res.status(400).json({
            success: false,
            message:
                'A quantidade deve ser um número inteiro maior que zero.'
        });
    }


    const usuarioId =
        Number(usuario_id) || 15;


    let connection;


    try {

        connection =
            await db.getConnection();

        await connection.beginTransaction();


        // Buscar produto
        const [produtos] =
            await connection.query(
                `
                SELECT
                    id,
                    nome,
                    quantidade
                FROM produto
                WHERE id = ?
                FOR UPDATE
                `,
                [produto_id]
            );


        if (produtos.length === 0) {

            await connection.rollback();

            return res.status(404).json({
                success: false,
                message:
                    'Produto não encontrado.'
            });
        }


        const produto =
            produtos[0];


        const estoqueAtual =
            Number(produto.quantidade) || 0;


        // Verificar estoque
        if (
            quantidadeSaida >
            estoqueAtual
        ) {

            await connection.rollback();

            return res.status(400).json({
                success: false,
                message:
                    `Estoque insuficiente. ` +
                    `Estoque atual: ${estoqueAtual}.`
            });
        }


        const novoEstoque =
            estoqueAtual -
            quantidadeSaida;


        // Atualizar estoque
        await connection.query(
            `
            UPDATE produto
            SET quantidade = ?
            WHERE id = ?
            `,
            [
                novoEstoque,
                produto_id
            ]
        );


        // Criar movimentação
        const [movimentacaoResult] =
            await connection.query(
                `
                INSERT INTO movimentacao
                (
                    tipo_movimentacao,
                    data_movimentacao,
                    quantidade,
                    produto_id
                )
                VALUES
                (
                    'SAIDA',
                    NOW(),
                    ?,
                    ?
                )
                `,
                [
                    quantidadeSaida,
                    produto_id
                ]
            );


        const movimentacaoId =
            movimentacaoResult.insertId;


        // Criar pedido de saída
        const [pedidoResult] =
            await connection.query(
                `
                INSERT INTO pedido_saida
                (
                    tipo,
                    pagamento,
                    quantidade,
                    valor,
                    data_pagamento,
                    cliente_id,
                    usuario_id
                )
                VALUES
                (
                    'SAIDA',
                    NULL,
                    ?,
                    NULL,
                    NULL,
                    NULL,
                    ?
                )
                `,
                [
                    quantidadeSaida,
                    usuarioId
                ]
            );


        const pedidoSaidaId =
            pedidoResult.insertId;


        // Criar item de saída
        await connection.query(
            `
            INSERT INTO item_saida
            (
                quantidade,
                valor,
                pedido_saida_id,
                movimentacao_id
            )
            VALUES
            (
                ?,
                NULL,
                ?,
                ?
            )
            `,
            [
                quantidadeSaida,
                pedidoSaidaId,
                movimentacaoId
            ]
        );


        // Confirmar tudo
        await connection.commit();


        console.log(
            `Saída registrada: produto ${produto_id} | ` +
            `-${quantidadeSaida} | ` +
            `estoque: ${novoEstoque}`
        );


        return res.json({

            success: true,

            message:
                'Saída registrada com sucesso.',

            produto: {

                id:
                    produto.id,

                nome:
                    produto.nome,

                quantidadeAnterior:
                    estoqueAtual,

                quantidadeSaida:
                    quantidadeSaida,

                quantidadeAtual:
                    novoEstoque
            },

            movimentacaoId:
                movimentacaoId,

            pedidoSaidaId:
                pedidoSaidaId
        });


    } catch (error) {

        if (connection) {
            await connection.rollback();
        }

        console.error(
            'Erro ao registrar saída:',
            error
        );

        return res.status(500).json({

            success: false,

            message:
                'Erro ao registrar saída.',

            error:
                error.message
        });

    } finally {

        if (connection) {
            connection.release();
        }
    }
});


// =====================================================
// INICIAR SERVIDOR
// =====================================================

const PORT = 3000;

app.listen(PORT, () => {

    console.log(
        `Servidor SmartMeds rodando em http://localhost:${PORT}`
    );

});