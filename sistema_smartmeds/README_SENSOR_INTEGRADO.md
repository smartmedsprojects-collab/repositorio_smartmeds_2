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
