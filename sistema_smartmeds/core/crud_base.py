from core.database import Database

class CrudBase:
    table = ""
    fields = []
    pk = "id"
    user_fk = "usuario_id"  

    @classmethod
    def find_all(cls, usuario_id=None, order_by=None):
       
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            if not order_by:
                order_by = cls.pk

            if usuario_id is not None:
                sql = f"SELECT * FROM {cls.table} WHERE {cls.user_fk} = %s ORDER BY {order_by}"
                cursor.execute(sql, (usuario_id,))
            else:
                sql = f"SELECT * FROM {cls.table} ORDER BY {order_by}"
                cursor.execute(sql)

            return cursor.fetchall()
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def find_by_id(cls, id, usuario_id=None):
        
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            if usuario_id is not None:
                sql = f"SELECT * FROM {cls.table} WHERE {cls.pk} = %s AND {cls.user_fk} = %s"
                cursor.execute(sql, (id, usuario_id))
            else:
                sql = f"SELECT * FROM {cls.table} WHERE {cls.pk} = %s"
                cursor.execute(sql, (id,))

            return cursor.fetchone()
        finally:
            cursor.close()
            conexao.close()

    @classmethod
    def delete(cls, id, usuario_id=None):
        
        conexao = Database.connect()
        cursor = conexao.cursor()
        try:
            if usuario_id is not None:
                sql = f"DELETE FROM {cls.table} WHERE {cls.pk} = %s AND {cls.user_fk} = %s"
                cursor.execute(sql, (id, usuario_id))
            else:
                sql = f"DELETE FROM {cls.table} WHERE {cls.pk} = %s"
                cursor.execute(sql, (id,))

            conexao.commit()
            return cursor.rowcount
        except Exception:
            conexao.rollback()
            raise
        finally:
            cursor.close()
            conexao.close()

    def insert(self):
        
        conexao = Database.connect()
        cursor = conexao.cursor()
        try:
            colunas = ", ".join(self.fields)
            marcadores = ", ".join(["%s"] * len(self.fields))
            valores = tuple(getattr(self, campo) for campo in self.fields)
            sql = f"INSERT INTO {self.table} ({colunas}) VALUES ({marcadores})"
            cursor.execute(sql, valores)
            conexao.commit()
            return cursor.lastrowid
        except Exception:
            conexao.rollback()
            raise
        finally:
            cursor.close()
            conexao.close()

    def update(self, id, usuario_id=None):
        
        conexao = Database.connect()
        cursor = conexao.cursor()
        try:
            campos = ", ".join([f"{campo} = %s" for campo in self.fields])
            valores = list(getattr(self, campo) for campo in self.fields) + [id]

            if usuario_id is not None:
                sql = f"""
                    UPDATE {self.table}
                    SET {campos}
                    WHERE {self.pk} = %s AND {self.user_fk} = %s
                """
                valores.append(usuario_id)
            else:
                sql = f"""
                    UPDATE {self.table}
                    SET {campos}
                    WHERE {self.pk} = %s
                """

            cursor.execute(sql, tuple(valores))
            conexao.commit()
            return cursor.rowcount
        except Exception:
            conexao.rollback()
            raise
        finally:
            cursor.close()
            conexao.close()