# config.py — Configurações do projeto
# ─────────────────────────────────────────────────────────────────
# Arquivo central de configurações.
# Quando precisar mudar rede, broker ou nome, muda AQUI.
# O main.py importa tudo daqui — não precisa tocar nele.

# ── WiFi ──────────────────────────────────────────────────────────
WIFI_SSID = "WIFI_IOT"           # nome exato da rede (maiúsculas importam)
WIFI_PASS = "Ac1ce2ss5@IOT"     # senha da rede

# ── Broker MQTT ───────────────────────────────────────────────────
# IP do notebook que está rodando o Mosquitto
# Descubra com: ipconfig → Endereço IPv4 da rede WiFi
BROKER_IP   = "10.132.112.4"
BROKER_PORT = 1883           # porta TCP padrão do MQTT

# ── Identificação do dispositivo ──────────────────────────────────
# CLIENT_ID identifica este Pico no broker
# Dois dispositivos com o mesmo ID se desconectam mutuamente
MEU_NOME  = "SmartLight"                    # ← coloque seu nome aqui
CLIENT_ID = f"pico_{MEU_NOME.lower()}"  # ex: pico_joao

# ── Tópico MQTT ───────────────────────────────────────────────────
# Endereço da mensagem — como uma pasta: projeto/quem/dado
# O dashboard precisa assinar o mesmo tópico para receber
TOPIC_PUB = f"senai/{MEU_NOME.lower()}/temp"