from core.database import Database


class SensorLeitura:
    SENSOR = "DHT11"

    @staticmethod
    def criar_tabela():
        conexao = Database.connect()
        cursor = conexao.cursor()
        try:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS sensor_leitura (
                    id INT NOT NULL AUTO_INCREMENT,
                    device_id VARCHAR(50) NOT NULL,
                    sensor VARCHAR(30) NOT NULL DEFAULT 'DHT11',
                    temperatura FLOAT NULL,
                    umidade FLOAT NULL,
                    distancia FLOAT NULL,
                    rfid_uid VARCHAR(50) NULL,
                    produto VARCHAR(100) NULL,
                    movimento VARCHAR(30) NULL,
                    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (id),
                    INDEX idx_sensor_timestamp (sensor, timestamp),
                    INDEX idx_device_timestamp (device_id, timestamp)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """
            )
            conexao.commit()
        finally:
            cursor.close()
            conexao.close()

    @staticmethod
    def salvar(device_id, sensor, temperatura=None, umidade=None, **_):
        sensor = str(sensor or "").strip().upper()
        if sensor != SensorLeitura.SENSOR:
            return False

        conexao = Database.connect()
        cursor = conexao.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO sensor_leitura
                (device_id, sensor, temperatura, umidade)
                VALUES (%s, 'DHT11', %s, %s)
                """,
                (
                    str(device_id or "esp32-desconhecido").strip()[:50],
                    SensorLeitura._numero(temperatura),
                    SensorLeitura._numero(umidade),
                ),
            )
            conexao.commit()
            return True
        finally:
            cursor.close()
            conexao.close()

    @staticmethod
    def listar(device_id=None, sensor=None, limite=100):
        limite = max(1, min(int(limite), 1000))
        filtros = ["sensor = 'DHT11'"]
        valores = []

        if device_id:
            filtros.append("device_id = %s")
            valores.append(str(device_id).strip())

        if sensor and str(sensor).strip().upper() != SensorLeitura.SENSOR:
            return []

        sql = """
            SELECT id, device_id, sensor, temperatura, umidade,
                   DATE_FORMAT(timestamp, '%Y-%m-%d %H:%i:%s') AS timestamp
            FROM sensor_leitura
            WHERE %s
            ORDER BY timestamp DESC, id DESC
            LIMIT %%s
        """ % " AND ".join(filtros)
        valores.append(limite)

        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            cursor.execute(sql, tuple(valores))
            return cursor.fetchall()
        finally:
            cursor.close()
            conexao.close()

    @staticmethod
    def resumo():
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT temperatura, umidade, timestamp, device_id
                FROM sensor_leitura
                WHERE sensor = 'DHT11'
                ORDER BY timestamp DESC, id DESC
                LIMIT 1
                """
            )
            atual = cursor.fetchone()

            return {
                "temperatura": atual.get("temperatura") if atual else None,
                "umidade": atual.get("umidade") if atual else None,
                "device_id": atual.get("device_id") if atual else None,
                "ultima_leitura": SensorLeitura._formatar_data(atual.get("timestamp") if atual else None),
            }
        finally:
            cursor.close()
            conexao.close()

    @staticmethod
    def temperatura_atual():
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT device_id, temperatura, umidade,
                       DATE_FORMAT(timestamp, '%Y-%m-%d %H:%i:%s') AS timestamp
                FROM sensor_leitura
                WHERE sensor = 'DHT11' AND temperatura IS NOT NULL
                ORDER BY timestamp DESC, id DESC
                LIMIT 1
                """
            )
            return cursor.fetchone()
        finally:
            cursor.close()
            conexao.close()

    @staticmethod
    def dispositivos_temperatura():
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT device_id AS nome,
                       temperatura, umidade,
                       DATE_FORMAT(timestamp, '%d/%m/%Y %H:%i:%s') AS ultima_leitura
                FROM sensor_leitura s
                WHERE sensor = 'DHT11'
                  AND temperatura IS NOT NULL
                  AND NOT EXISTS (
                      SELECT 1
                      FROM sensor_leitura s2
                      WHERE s2.sensor = 'DHT11'
                        AND s2.device_id = s.device_id
                        AND (
                            s2.timestamp > s.timestamp
                            OR (s2.timestamp = s.timestamp AND s2.id > s.id)
                        )
                  )
                ORDER BY s.device_id
                """
            )
            return cursor.fetchall()
        finally:
            cursor.close()
            conexao.close()

    @staticmethod
    def _numero(valor):
        if valor in (None, ""):
            return None
        try:
            return float(valor)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _formatar_data(valor):
        if valor is None:
            return None
        return valor.strftime('%Y-%m-%d %H:%M:%S') if hasattr(valor, 'strftime') else str(valor)
