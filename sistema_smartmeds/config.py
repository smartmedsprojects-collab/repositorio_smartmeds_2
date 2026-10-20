import os


DB_CONFIG = {
    "host": os.getenv("SMARTMEDS_DB_HOST", "localhost"),
    "user": os.getenv("SMARTMEDS_DB_USER", "root"),
    "password": os.getenv("SMARTMEDS_DB_PASSWORD", "123456"),
    "database": os.getenv("SMARTMEDS_DB_NAME", "smartmeds3"),
    "auth_plugin": os.getenv("SMARTMEDS_DB_AUTH_PLUGIN", "mysql_native_password"),
}

MQTT_BROKER = os.getenv(
    "SMARTMEDS_MQTT_BROKER",
    "b1600c60a35c4520b32b9507d0b47b02.s1.eu.hivemq.cloud",
)
MQTT_PORT = int(os.getenv("SMARTMEDS_MQTT_PORT", "8883"))
MQTT_USER = os.getenv("SMARTMEDS_MQTT_USER", "IOT-SENAI")
MQTT_PASSWORD = os.getenv("SMARTMEDS_MQTT_PASSWORD", "12345678")
MQTT_TOPIC = os.getenv("SMARTMEDS_MQTT_TOPIC", "sensores/leitura")

SENSOR_TEMP_MIN = float(os.getenv("SMARTMEDS_SENSOR_TEMP_MIN", "15"))
SENSOR_TEMP_MAX = float(os.getenv("SMARTMEDS_SENSOR_TEMP_MAX", "30"))
