import os


DB_CONFIG = {
    "host": os.getenv("SMARTMEDS_DB_HOST", "localhost"),
    "user": os.getenv("SMARTMEDS_DB_USER", "root"),
    "password": os.getenv("SMARTMEDS_DB_PASSWORD", "123456"),
    "database": os.getenv("SMARTMEDS_DB_NAME", "smartmeds3"),
    "auth_plugin": os.getenv("SMARTMEDS_DB_AUTH_PLUGIN", "mysql_native_password"),
}

# Só força um plugin de autenticação se ele tiver sido configurado explicitamente.
# Isso evita incompatibilidades com versões do MySQL que usam caching_sha2_password.
_db_auth_plugin = os.getenv("SMARTMEDS_DB_AUTH_PLUGIN", "").strip()
if _db_auth_plugin:
    DB_CONFIG["auth_plugin"] = _db_auth_plugin

FLASK_SECRET_KEY = os.getenv(
    "SMARTMEDS_SECRET_KEY",
    "smartmeds-dev-only-change-this-key",
)

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
