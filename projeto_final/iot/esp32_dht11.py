"""Envio das leituras do DHT11 (GPIO 13) ao SmartMeds pelo HiveMQ Cloud.

Antes de enviar ao ESP32, preencha Wi-Fi e senha MQTT abaixo. Instale a
biblioteca MicroPython umqtt.simple no dispositivo (por exemplo, pelo Thonny).
"""
import network
import time
import dht
import json
from machine import Pin
from umqtt.simple import MQTTClient

# Preencha com os dados da sua rede Wi-Fi.
WIFI_SSID = "COLOQUE_O_NOME_DO_WIFI"
WIFI_PASSWORD = "COLOQUE_A_SENHA_DO_WIFI"

# Devem ser iguais aos valores usados pelo Flask em config.py/variáveis de ambiente.
MQTT_BROKER = "b1600c60a35c4520b32b9507d0b47b02.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_USER = "IOT-SENAI"
MQTT_PASSWORD = "12345678"  # igual ao valor padrão de config.py; altere se necessário
MQTT_TOPIC = b"sensores/leitura"
DEVICE_ID = "esp32-01"
INTERVALO = 10

sensor = dht.DHT11(Pin(13))
wlan = network.WLAN(network.STA_IF)


def conectar_wifi():
    wlan.active(True)
    if wlan.isconnected():
        return
    print("Conectando ao Wi-Fi...")
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    inicio = time.ticks_ms()
    while not wlan.isconnected():
        if time.ticks_diff(time.ticks_ms(), inicio) > 20000:
            raise OSError("Tempo esgotado ao conectar ao Wi-Fi")
        time.sleep(1)
    print("Wi-Fi conectado:", wlan.ifconfig()[0])


def conectar_mqtt():
    cliente = MQTTClient(
        client_id=DEVICE_ID.encode(),
        server=MQTT_BROKER,
        port=MQTT_PORT,
        user=MQTT_USER,
        password=MQTT_PASSWORD,
        keepalive=60,
        ssl=True,
        ssl_params={"server_hostname": MQTT_BROKER},
    )
    cliente.connect()
    print("Conectado ao HiveMQ; tópico:", MQTT_TOPIC.decode())
    return cliente


cliente = None
while True:
    try:
        conectar_wifi()
        if cliente is None:
            cliente = conectar_mqtt()

        sensor.measure()
        payload = {
            "device_id": DEVICE_ID,
            "sensor": "DHT11",
            "temperatura": sensor.temperature(),
            "umidade": sensor.humidity(),
        }
        cliente.publish(MQTT_TOPIC, json.dumps(payload).encode(), qos=1)
        print("Leitura enviada:", json.dumps(payload))
        time.sleep(INTERVALO)
    except Exception as erro:
        print("Falha ao ler/enviar DHT11:", erro)
        if cliente is not None:
            try:
                cliente.disconnect()
            except Exception:
                pass
            cliente = None
        time.sleep(5)
