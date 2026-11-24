"""Validação e padronização do identificador do sensor SmartMeds.

O firmware legado publica device_id='SmartMeds', enquanto o firmware atual
usa 'esp32-01'. Os dois valores representam o mesmo sensor autorizado.
Qualquer outro identificador continua sendo rejeitado.
"""

from config import MQTT_DEVICE_ID


def normalizar_device_id(valor):
    """Retorna o identificador canônico do sensor autorizado ou None."""
    device_recebido = str(valor or "").strip()
    device_configurado = str(MQTT_DEVICE_ID or "").strip()

    if not device_configurado or not device_recebido:
        return None

    identificador = device_recebido.casefold()
    permitidos = {device_configurado.casefold()}
    if device_configurado.casefold() in {"smartmeds", "esp32-01"}:
        permitidos.update({"smartmeds", "esp32-01"})

    if identificador not in permitidos:
        return None

    # Centraliza todos os registros no identificador configurado no Flask.
    return device_configurado


def ids_device_permitidos():
    """Lista IDs aceitos para consultar leituras antigas e atuais."""
    device_configurado = str(MQTT_DEVICE_ID or "").strip()
    if not device_configurado:
        return []

    valores = [device_configurado]
    if device_configurado.casefold() in {"smartmeds", "esp32-01"}:
        valores.extend(["SmartMeds", "esp32-01"])
    resultado = []
    vistos = set()
    for valor in valores:
        chave = valor.casefold()
        if chave not in vistos:
            vistos.add(chave)
            resultado.append(chave)
    return resultado
