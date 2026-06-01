# 💡 SmartLight — Dashboard IoT para Iluminação Inteligente

Uma interface web moderna e responsiva em tempo real para monitorização e controlo manual de um sistema de iluminação automatizado com o **Raspberry Pi Pico W**. O projeto comunica via **WebSockets** utilizando o protocolo **MQTT** para receber dados de luminosidade (LDR), presença (PIR) e estado atual do LED, permitindo também o controlo remoto imediato através de um painel tátil.

---

## 🚀 Funcionalidades

- **Monitorização em Tempo Real:** Visualização instantânea do estado da luz, nível de luminosidade em `lux` e deteção de movimento.
- **Controlo Dual Manual/Automático:** Alternância inteligente entre o modo automático (baseado nos sensores) e o controlo forçado via botões.
- **Histórico de Logs Activo:** Um terminal embutido que exibe as mensagens brutas de entrada e saída do Broker MQTT para facilitar a depuração.
- **Relógio de Sistema Sincronizado:** Indicação visual de data e hora exatas da última atualização recebida do hardware.

---

## 🛠️ Arquitetura do Sistema

O fluxo de comunicação segue a estrutura Publish/Subscribe (Pub/Sub):

1. **Pico W (Hardware):** Lê os sensores e publica um JSON no tópico `senai/+/hello`. Fica à escuta de comandos no tópico `senai/seu-nome/comando`.
2. **Mosquitto Broker (MQTT):** Intermeia as mensagens usando a porta WebSocket (ex: `8000`).
3. **Dashboard (Frontend):** Conecta-se via `mqtt.js`, interpreta o JSON e atualiza os cards dinamicamente.