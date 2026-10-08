import json
import logging
import ssl
import uuid

import certifi
import paho.mqtt.client as mqtt

from config import MQTT_BROKER, MQTT_PASSWORD, MQTT_PORT, MQTT_TOPIC, MQTT_USER
from .sensor_leitura import SensorLeitura


logger = logging.getLogger("smartmeds.iot")


class MQTTManager:
    def __init__(self):
        self.iniciado = False
        self.conectado = False
        self.client = mqtt.Client(
            mqtt.CallbackAPIVersion.VERSION1,
            client_id=f"smartmeds-{uuid.uuid4().hex[:8]}",
            protocol=mqtt.MQTTv311,
        )
        self.client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
        self.client.tls_set(
            ca_certs=certifi.where(),
            tls_version=ssl.PROTOCOL_TLS_CLIENT,
        )
        self.client.reconnect_delay_set(min_delay=2, max_delay=60)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message

    def start(self):
        if self.iniciado:
            return
        self.iniciado = True
        try:
            self.client.loop_start()
            self.client.connect_async(MQTT_BROKER, MQTT_PORT, keepalive=60)
            logger.info("MQTT DHT11 iniciado para %s:%s", MQTT_BROKER, MQTT_PORT)
        except Exception:
            self.iniciado = False
            logger.exception("Não foi possível iniciar o MQTT")

    def stop(self):
        if not self.iniciado:
            return
        try:
            self.client.loop_stop()
            self.client.disconnect()
        finally:
            self.iniciado = False
            self.conectado = False

    def _on_connect(self, client, userdata, flags, rc):
        self.conectado = rc == 0
        if self.conectado:
            client.subscribe(MQTT_TOPIC, qos=1)
            logger.info("Conectado ao HiveMQ e inscrito em %s", MQTT_TOPIC)
        else:
            logger.error("Falha na conexão MQTT. Código: %s", rc)

    def _on_disconnect(self, client, userdata, rc):
        self.conectado = False
        logger.warning("MQTT desconectado. Código: %s", rc)

    def _on_message(self, client, userdata, msg):
        try:
            dados = json.loads(msg.payload.decode("utf-8"))
            sensor = str(dados.get("sensor") or "").strip().upper()
            if sensor != "DHT11":
                logger.warning("Mensagem ignorada: somente DHT11 é aceito (%s)", sensor or "sem sensor")
                return

            if dados.get("temperatura") is None and dados.get("umidade") is None:
                logger.warning("Leitura DHT11 sem temperatura/umidade")
                return

            sucesso = SensorLeitura.salvar(
                device_id=dados.get("device_id"),
                sensor="DHT11",
                temperatura=dados.get("temperatura"),
                umidade=dados.get("umidade"),
            )

            if not sucesso:
                logger.error("Falha ao gravar leitura DHT11")
        except json.JSONDecodeError:
            logger.error("Payload MQTT inválido: %r", msg.payload)
        except Exception:
            logger.exception("Erro ao processar mensagem MQTT")


mqtt_manager = MQTTManager()
