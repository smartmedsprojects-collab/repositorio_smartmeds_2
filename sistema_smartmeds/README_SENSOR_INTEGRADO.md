# SmartMeds + DHT11

O monitoramento IoT do SmartMeds foi simplificado para usar somente o **DHT11**.

## O que o DHT11 envia

- Temperatura (°C)
- Umidade (%)

## Fluxo

ESP32 + DHT11 → HiveMQ Cloud → MQTT → SmartMeds Flask → MySQL (`sensor_leitura`)

## Tela

Depois do login, acesse **Menu → Sensor DHT11** ou `/sensores`.

A tela mostra a leitura atual, dispositivo, última leitura, gráficos de temperatura e umidade e as últimas 20 leituras.

## API

- `/api/resumo`
- `/api/sensores`
- `/api/sensores/dht11`
- `/api/leituras`
- `/api/status-iot`

As rotas antigas de HC-SR04 e MFRC522 foram removidas. O backend também ignora mensagens MQTT de qualquer sensor diferente de DHT11.

## Banco

A tabela `sensor_leitura` é criada automaticamente. Em instalações novas, apenas DHT11 é usado. Em bancos antigos, colunas relacionadas aos sensores removidos podem continuar fisicamente existentes por compatibilidade, mas não são utilizadas pelo SmartMeds.

## Executar

```bash
pip install -r requeriments.txt
python app.py
```

## Atualização automática e envio físico

A página `/sensores` consulta as APIs automaticamente a cada **30 segundos**. Ela só mostra leituras novas se o ESP32 publicar mensagens MQTT e o Flask as gravar em `sensor_leitura`.

### Configurar o ESP32

1. Abra `iot/esp32_dht11.py` no Thonny e envie esse arquivo ao ESP32 com MicroPython.
2. Instale a biblioteca `umqtt.simple` no dispositivo caso ainda não exista.
3. Preencha `WIFI_SSID` e `WIFI_PASSWORD`. A `MQTT_PASSWORD` do exemplo coincide com o valor padrão de `config.py`; se você alterou o valor em `config.py` ou na variável `SMARTMEDS_MQTT_PASSWORD`, atualize também a senha no ESP32.
4. Confirme que `MQTT_BROKER`, `MQTT_PORT` e `MQTT_TOPIC` correspondem aos valores do SmartMeds.
5. Execute o programa. No terminal serial devem aparecer `Wi-Fi conectado`, `Conectado ao HiveMQ` e `Leitura enviada` a cada 10 segundos.

Não é necessário atualizar manualmente a página. Se ela continuar igual, confira se o horário da última leitura muda e se o terminal serial mostra `Leitura enviada`; estar com o Flask conectado ao HiveMQ, por si só, não garante que o ESP32 esteja publicando.

