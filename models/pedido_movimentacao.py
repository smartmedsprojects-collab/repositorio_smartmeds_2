from datetime import datetime
from core.crud_base import CrudBase
from core.database import Database
from core.validator import Validator
#from models.fornecedor import fornecedor
#from models.estoque import estoque
#from models.cliente import cliente

class pedidos(CrudBase):
    table = "pedido_entrada"
    fields = [
        "fornacedor_id",
        "quantidade",
        "pagamento",
        "valor",
        "data_pagamento"
    ]
    table = "pedido_saida"
    fields = [
        "cliente_id",
        "quantidade",
        "pagamento",
        "valor",
        "data_pagamento"
    ]

    def __init__(self, fornecedor_id,cliente_id, quantidade,valor, pagamento, data_pagamento=None):
        self.fornecedor_id = fornacedor_id
        self.cliente = cliente_id
        self.quantidade = quantidade
        self.valor = valor
        self.pagamento = pagamento
        self.data_pagamento = data_pagamento or datetime.now()

    def validate(self):
        erros = []

        erro_pedidos = Validator.positive(self.fornecedor_id, "pedidos")
        if erro_pedidos:
            erros.append(erro_pedidos)
        
        erro_pedidos = Validator.positive(self.cliente_id, "pedidos")
        if erro_pedidos:
            erros.append(erro_pedidos)

        erro_qtd = Validator.positive(self.quantidade, "quantidade")
        if erro_qtd:
            erros.append(erro_qtd)

        if self.tipo not in ["ENTRADA", "SAIDA"]:
            erros.append("O tipo deve ser ENTRADA ou SAIDA.")
            
        if self.fornecedor_id == ["ENTRADA"]:
            erros.append("O tipo deve ser entrada")
            
        if self.cliente_id == ["SAIDA"]:
            erros.append("O tipo deve ser saida")

        return erros

    @classmethod
    def find_all_with_product(cls):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            sql = """
            SELECT pm.*, p.nome AS produto
            FROM pestoque pm
            INNER JOIN produto p ON pm.produto_id = p.id
            ORDER BY pm.data_pagamento DESC
            """
            cursor.execute(sql)
            return cursor.fetchall()
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def pedido_entrada(cls, id):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            conexao.start_transaction()

            cursor.execute("SELECT * FROM pedido_entrada WHERE id = %s FOR UPDATE", (id,))
            pedido_entrada = cursor.fetchone()
            if not pedido:
                raise ValueError("Pedido não encontrado.")

            if pedido_entrada["status"] != "PENDENTE":
                raise ValueError("Somente pedidos pendentes podem ser processados.")

            cursor.execute("SELECT * FROM fornecedor WHERE id = %s FOR UPDATE", (pedido_entrada["fornecedor_id"],))
            produto = cursor.fetchone()
            if not produto:
                raise ValueError("Produto não encontrado.")

            if pedido_entrada["tipo"] == "ENTRADA":
                nova_quantidade = produto["quantidade"] + pedido_entrada["quantidade"]
                raise 
            if pedido_entrada["quantidade"] > produto["quantidade"]:
                raise ValueError("Estoque insuficiente para concluir a saída.")
                nova_quantidade = produto["quantidade"] - pedido_entrada["quantidade"]
            else:
                raise ValueError("Tipo de pedido inválido.")

            Produto.update_quantity(produto["id"], nova_quantidade, connection=conexao)

            mov = estoque(produto["id"], pedido_entrada["valor"], pedido_entrada["quantidade"])
            cursor.execute(
                """
                INSERT INTO estoque (produto_id, quantidade, quantidade_min)
                VALUES (%s, %s, %s)
                """,
                (mov.produto_id, mov.quantidade, mov.quantidade_min)
            )
            cursor.execute(
                """
                UPDATE pedido_entrada
                SET status = %s, data_pagamento = %s
                WHERE id = %s
                """,
                ("CONCLUIDO", datetime.now(), id)
            )

            conexao.commit()
            return "Pedido processado com sucesso."
        except Exception:
            conexao.rollback()
            raise
        finally:
            cursor.close()
            conexao.close()
    @classmethod
    def pedido_saida(cls, id):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            conexao.start_transaction()

            cursor.execute("SELECT * FROM pedido_saida WHERE id = %s FOR UPDATE", (id,))
            pedido_saida = cursor.fetchone()
            if not pedido:
                raise ValueError("Pedido não encontrado.")

            if pedido_saida["status"] != "PENDENTE":
                raise ValueError("Somente pedidos pendentes podem ser processados.")

            cursor.execute("SELECT * FROM fornecedor WHERE id = %s FOR UPDATE", (pedido_saida["saida_id"],))
            produto = cursor.fetchone()
            if not produto:
                raise ValueError("Produto não encontrado.")

            if pedido_saida["tipo"] == "ENTRADA":
                nova_quantidade = produto["quantidade"] + pedido_saida["quantidade"]
            elif pedido_saida["tipo"] == "SAIDA":

                if pedido_saida["quantidade"] > produto["quantidade"]:
                    raise ValueError("Estoque insuficiente para concluir a saída.")
                nova_quantidade = produto["quantidade"] - pedido_saida["quantidade"]
            else:
                raise ValueError("Tipo de pedido inválido.")

            Produto.update_quantity(produto["id"], nova_quantidade, connection=conexao)

            mov = estoque(produto["id"], pedido_saida["valor"], pedido_saida["quantidade"])
            cursor.execute(
                """
                INSERT INTO estoque (produto_id, quantidade, quantidade_min)
                VALUES (%s, %s, %s)
                """,
                (mov.produto_id, mov.quantidade, mov.quantidade_min)
            )
            cursor.execute(
                """
                UPDATE pedido_saida
                SET status = %s, data_pagamento = %s
                WHERE id = %s
                """,
                ("CONCLUIDO", datetime.now(), id)
            )

            conexao.commit()
            return "Pedido processado com sucesso."
        except Exception:
            conexao.rollback()
            raise
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def cancelar(cls, id):
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM pedido_entrada WHERE id = %s", (id,))
            pedido_entrada = cursor.fetchone()
            if not pedido_entrada:
                raise ValueError("Pedido não encontrado.")
            if pedido_entrada["status"] != "PENDENTE":
                raise ValueError("Somente pedidos pendentes podem ser cancelados.")

            cursor = conexao.cursor()
            cursor.execute(
                """
                UPDATE pedido_entrada
                SET status = %s, data_pagamento = %s
                WHERE id = %s
                """,
                ("CANCELADO", datetime.now(), id)
            )
            conexao.commit()
            return "Pedido cancelado com sucesso."
        except Exception:
            conexao.rollback()
            raise
        finally:
            cursor.close()
            conexao.close()