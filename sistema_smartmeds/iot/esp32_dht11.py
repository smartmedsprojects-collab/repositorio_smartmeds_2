from machine import Pin
from time import sleep
import dht
import json

# ==============================
# DHT11
# ==============================
sensor = dht.DHT11(Pin(13))
DEVICE_ID = "esp32-01"
INTERVALO = 10

# O envio MQTT depende da biblioteca MQTT instalada no ESP32.
# Publique o JSON abaixo no mesmo tópico configurado no SmartMeds.

while True:
    try:
        sensor.measure()
        payload = {
            "device_id": DEVICE_ID,
            "sensor": "DHT11",
            "temperatura": sensor.temperature(),
            "umidade": sensor.humidity(),
        }
        print(json.dumps(payload))
        sleep(INTERVALO)
    except Exception as erro:
        print("Erro ao ler DHT11:", erro)
        sleep(2)
