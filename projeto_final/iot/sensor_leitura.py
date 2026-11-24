from core.database import Database
from config import MQTT_DEVICE_ID
from .device_identity import normalizar_device_id, ids_device_permitidos


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
        device_id = normalizar_device_id(device_id)
        if device_id is None:
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
                    str(device_id).strip()[:50],
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
        if device_id is not None and normalizar_device_id(device_id) is None:
            return []
        ids_permitidos = ids_device_permitidos()
        if not ids_permitidos:
            return []
        placeholders = ", ".join(["%s"] * len(ids_permitidos))
        filtros = ["sensor = 'DHT11'", f"LOWER(TRIM(device_id)) IN ({placeholders})"]
        valores = list(ids_permitidos)

        if sensor and str(sensor).strip().upper() != SensorLeitura.SENSOR:
            return []

        # Não usar DATE_FORMAT com parâmetros: o %s da máscara de data pode ser
        # interpretado pelo MySQL Connector como um marcador SQL adicional.
        sql = f"""
            SELECT id, device_id, sensor, temperatura, umidade, timestamp
            FROM sensor_leitura
            WHERE {" AND ".join(filtros)}
            ORDER BY timestamp DESC, id DESC
            LIMIT %s
        """
        valores.append(limite)

        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            cursor.execute(sql, tuple(valores))
            leituras = cursor.fetchall()
            for leitura in leituras:
                leitura["timestamp"] = SensorLeitura._formatar_data(
                    leitura.get("timestamp")
                )
            return leituras
        finally:
            cursor.close()
            conexao.close()

    @staticmethod
    def resumo():
        ids_permitidos = ids_device_permitidos()
        if not ids_permitidos:
            return {
                "temperatura": None,
                "umidade": None,
                "device_id": None,
                "ultima_leitura": None,
            }
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT temperatura, umidade, timestamp, device_id
                FROM sensor_leitura
                WHERE sensor = 'DHT11'
                  AND LOWER(TRIM(device_id)) IN ({})
                ORDER BY timestamp DESC, id DESC
                LIMIT 1
                """.format(", ".join(["%s"] * len(ids_permitidos))),
                tuple(ids_permitidos),
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
        ids_permitidos = ids_device_permitidos()
        if not ids_permitidos:
            return None
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT device_id, temperatura, umidade,
                       DATE_FORMAT(timestamp, '%Y-%m-%d %H:%i:%s') AS timestamp
                FROM sensor_leitura
                WHERE sensor = 'DHT11'
                  AND LOWER(TRIM(device_id)) IN ({})
                  AND temperatura IS NOT NULL
                ORDER BY timestamp DESC, id DESC
                LIMIT 1
                """.format(", ".join(["%s"] * len(ids_permitidos))),
                tuple(ids_permitidos),
            )
            return cursor.fetchone()
        finally:
            cursor.close()
            conexao.close()

    @staticmethod
    def dispositivos_temperatura():
        ids_permitidos = ids_device_permitidos()
        if not ids_permitidos:
            return []
        conexao = Database.connect()
        cursor = conexao.cursor(dictionary=True)
        try:
            cursor.execute(
                """
                SELECT %s AS nome,
                       temperatura, umidade,
                       DATE_FORMAT(timestamp, '%d/%m/%Y %H:%i:%s') AS ultima_leitura
                FROM sensor_leitura
                WHERE sensor = 'DHT11'
                  AND LOWER(TRIM(device_id)) IN ({})
                  AND temperatura IS NOT NULL
                ORDER BY timestamp DESC, id DESC
                LIMIT 1
                """.format(", ".join(["%s"] * len(ids_permitidos))),
                tuple([MQTT_DEVICE_ID] + ids_permitidos),
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
