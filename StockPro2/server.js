const express = require('express');
const mysql = require('mysql2/promise');
const cors = require('cors');
const bcrypt = require('bcrypt');

const app = express();


// =====================================================
// CONFIGURAÇÕES
// =====================================================

app.use(cors());
app.use(express.json());


// =====================================================
// BANCO DE DADOS
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
// TESTE DA CONEXÃO
// =====================================================

async function testarBanco() {

    try {

        const connection =
            await db.getConnection();

        console.log(
            'Banco de dados conectado: smartmeds3'
        );

        connection.release();

    } catch (error) {

        console.error(
            'ERRO AO CONECTAR AO BANCO:',
            error.message
        );
    }
}

testarBanco();


// =====================================================
// LOGIN
// =====================================================

app.post('/api/login', async (req, res) => {

    const {
        email,
        senha
    } = req.body;


    if (!email || !senha) {

        return res.status(400).json({

            success: false,

            message:
                'Email e senha são obrigatórios.'
        });
    }


    try {

        const [usuarios] =
            await db.query(
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


        if (usuarios.length === 0) {

            return res.status(401).json({

                success: false,

                message:
                    'Credenciais inválidas.'
            });
        }


        const usuario =
            usuarios[0];


        let senhaValida = false;


        // Senhas do banco novo estão criptografadas
        try {

            senhaValida =
                await bcrypt.compare(
                    senha,
                    usuario.senha
                );

        } catch (error) {

            senhaValida = false;
        }


        // Compatibilidade caso exista senha antiga
        if (!senhaValida) {

            senhaValida =
                senha === usuario.senha;
        }


        if (!senhaValida) {

            return res.status(401).json({

                success: false,

                message:
                    'Credenciais inválidas.'
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

            message:
                'Erro ao realizar login.',

            error:
                error.message
        });
    }
});


// =====================================================
// DASHBOARD
// =====================================================

app.get('/api/dashboard', async (req, res) => {

    try {

        const [[produtos]] =
            await db.query(
                `
                SELECT
                    COUNT(*) AS totalProdutos
                FROM produto
                `
            );


        const [[estoqueBaixo]] =
            await db.query(
                `
                SELECT
                    COUNT(*) AS total
                FROM produto
                WHERE quantidade <= 5
                `
            );


        const [movimentacao] =
            await db.query(
                `
                SELECT
                    m.id,
                    m.tipo_movimentacao,
                    m.data_movimentacao,
                    m.quantidade,
                    m.produto_id,
                    p.nome AS produto_nome
                FROM movimentacao m
                LEFT JOIN produto p
                    ON p.id = m.produto_id
                ORDER BY
                    m.id DESC
                LIMIT 5
                `
            );


        return res.json({

            totalProducts:
                Number(
                    produtos.totalProdutos
                ) || 0,

            lowStockCount:
                Number(
                    estoqueBaixo.total
                ) || 0,

            recentActivities:
                movimentacao
        });


    } catch (error) {

        console.error(
            'Erro no dashboard:',
            error
        );


        return res.status(500).json({

            message:
                'Erro ao carregar dashboard.',

            error:
                error.message
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

            message:
                'Erro ao carregar produtos.',

            error:
                error.message
        });
    }
});


// =====================================================
// PRODUTO POR ID
// =====================================================

app.get('/api/produtos/:id', async (req, res) => {

    const {
        id
    } = req.params;


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

                message:
                    'Produto não encontrado.'
            });
        }


        return res.json(
            produtos[0]
        );


    } catch (error) {

        console.error(
            'Erro ao buscar produto:',
            error
        );


        return res.status(500).json({

            message:
                'Erro ao buscar produto.',

            error:
                error.message
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

            message:
                'Erro ao carregar clientes.',

            error:
                error.message
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

            message:
                'Erro ao carregar localizações.',

            error:
                error.message
        });
    }
});


// =====================================================
// ENTRADAS
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

            message:
                'Erro ao carregar entradas.',

            error:
                error.message
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

            message:
                'Erro ao carregar itens de entrada.',

            error:
                error.message
        });
    }
});


// =====================================================
// SAÍDAS
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

            message:
                'Erro ao carregar saídas.',

            error:
                error.message
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

            message:
                'Erro ao carregar itens de saída.',

            error:
                error.message
        });
    }
});


// =====================================================
// MOVIMENTAÇÕES - DADOS BRUTOS
// =====================================================

app.get('/api/movimentacao', async (req, res) => {

    try {

        const [movimentacao] =
            await db.query(
                `
                SELECT
                    *
                FROM movimentacao
                ORDER BY id DESC
                `
            );


        return res.json(
            movimentacao
        );


    } catch (error) {

        console.error(
            'Erro ao buscar movimentações:',
            error
        );


        return res.status(500).json({

            message:
                'Erro ao carregar movimentações.',

            error:
                error.message
        });
    }
});


// =====================================================
// HISTÓRICO DO APLICATIVO
// =====================================================

app.get('/api/movimentacao', async (req, res) => {

    try {

        console.log(
            'GET /api/movimentacao'
        );


        const [movimentacao] =
            await db.query(
                `
                SELECT
                    m.id,
                    m.tipo_movimentacao,
                    m.data_movimentacao,
                    m.quantidade,
                    m.produto_id,
                    p.nome AS produto_nome,
                    p.marca AS produto_marca
                FROM movimentacao AS m

                LEFT JOIN produto AS p
                    ON p.id = m.produto_id

                ORDER BY
                    m.data_movimentacao DESC,
                    m.id DESC
                `
            );


        const historico =
            movimentacao.map(
                (item) => {

                    const tipoBanco =
                        String(
                            item.tipo_movimentacao || ''
                        )
                        .trim()
                        .toUpperCase();


                    let tipo =
                        'Entrada';


                    if (
                        tipoBanco === 'SAIDA' ||
                        tipoBanco === 'SAÍDA'
                    ) {

                        tipo =
                            'Saída';
                    }


                    let date =
                        '';

                    let hour =
                        '';


                    if (
                        item.data_movimentacao
                    ) {

                        const data =
                            new Date(
                                item.data_movimentacao
                            );


                        if (
                            !Number.isNaN(
                                data.getTime()
                            )
                        ) {

                            date =
                                data.toLocaleDateString(
                                    'pt-BR'
                                );


                            hour =
                                data.toLocaleTimeString(
                                    'pt-BR',
                                    {
                                        hour:
                                            '2-digit',

                                        minute:
                                            '2-digit'
                                    }
                                );
                        }
                    }


                    return {

                        id:
                            item.id,

                        product:
                            item.produto_nome ||
                            `Produto #${item.produto_id}`,

                        brand:
                            item.produto_marca ||
                            '',

                        type:
                            tipo,

                        quantity:
                            Number(
                                item.quantidade
                            ) || 0,

                        date:
                            date,

                        hour:
                            hour
                    };
                }
            );


        console.log(
            `Histórico encontrado: ${historico.length} movimentações`
        );


        return res.json(
            historico
        );


    } catch (error) {

        console.error(
            'ERRO NO /api/movimentacao:',
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


    if (
        !produto_id ||
        !quantidade
    ) {

        return res.status(400).json({

            success: false,

            message:
                'produto_id e quantidade são obrigatórios.'
        });
    }


    const quantidadeEntrada =
        Number(quantidade);


    if (
        !Number.isInteger(
            quantidadeEntrada
        ) ||
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


        if (
            produtos.length === 0
        ) {

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
            Number(
                produto.quantidade
            ) || 0;


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


        // Registrar movimentação
        const [
            movimentacaoResult
        ] =
            await connection.query(
                `
                INSERT INTO movimentacao
                (
                    tipo_movimentacao,
                    data_movimentacao,
                    quantidade,
                    quantidade_min,
                    produto_id
                )
                VALUES
                (
                    'ENTRADA',
                    NOW(),
                    ?,
                    NULL,
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
        const [
            pedidoResult
        ] =
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
            'ENTRADA REGISTRADA:',
            {
                produto_id,
                quantidade:
                    quantidadeEntrada,
                estoqueAnterior:
                    estoqueAtual,
                estoqueAtual:
                    novoEstoque
            }
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
            'ERRO AO REGISTRAR ENTRADA:',
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
        usuario_id,
        cliente_id,
        tipo,
        pagamento,
        valor
    } = req.body;


    if (
        !produto_id ||
        !quantidade
    ) {

        return res.status(400).json({

            success: false,

            message:
                'produto_id e quantidade são obrigatórios.'
        });
    }


    const quantidadeSaida =
        Number(quantidade);


    if (
        !Number.isInteger(
            quantidadeSaida
        ) ||
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


    const clienteId =
        cliente_id
            ? Number(cliente_id)
            : null;


    const tipoSaida =
        tipo || 'VENDA';


    const pagamentoSaida =
        pagamento || null;


    const valorSaida =
        valor !== undefined &&
        valor !== null &&
        valor !== ''
            ? Number(valor)
            : null;


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


        if (
            produtos.length === 0
        ) {

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
            Number(
                produto.quantidade
            ) || 0;


        // Verificar estoque
        if (
            quantidadeSaida >
            estoqueAtual
        ) {

            await connection.rollback();

            return res.status(400).json({

                success: false,

                message:
                    `Estoque insuficiente. Estoque atual: ${estoqueAtual}.`
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


        // Registrar movimentação
        const [
            movimentacaoResult
        ] =
            await connection.query(
                `
                INSERT INTO movimentacao
                (
                    tipo_movimentacao,
                    data_movimentacao,
                    quantidade,
                    quantidade_min,
                    produto_id
                )
                VALUES
                (
                    'SAIDA',
                    NOW(),
                    ?,
                    NULL,
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
        const [
            pedidoResult
        ] =
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
                    ?,
                    ?,
                    ?,
                    ?,
                    CURDATE(),
                    ?,
                    ?
                )
                `,
                [
                    tipoSaida,
                    pagamentoSaida,
                    quantidadeSaida,
                    valorSaida,
                    clienteId,
                    usuarioId
                ]
            );


        const pedidoSaidaId =
            pedidoResult.insertId;


        // Criar item da saída
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
                ?,
                ?,
                ?
            )
            `,
            [
                quantidadeSaida,
                valorSaida,
                pedidoSaidaId,
                movimentacaoId
            ]
        );


        await connection.commit();


        console.log(
            'SAÍDA REGISTRADA:',
            {
                produto_id,
                quantidade:
                    quantidadeSaida,
                estoqueAnterior:
                    estoqueAtual,
                estoqueAtual:
                    novoEstoque
            }
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
            'ERRO AO REGISTRAR SAÍDA:',
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


app.listen(
    PORT,
    '0.0.0.0',
    () => {

        console.log('');
        console.log(
            '========================================'
        );

        console.log(
            '   SMARTMEDS - SERVIDOR'
        );

        console.log(
            '========================================'
        );

        console.log(
            `Banco: smartmeds3`
        );

        console.log(
            `Porta: ${PORT}`
        );

        console.log(
            `API: http://localhost:${PORT}/api`
        );

        console.log(
            '========================================'
        );

        console.log('');
    }
);