# main.py — Código principal do Pico 2W
# ─────────────────────────────────────────────────────────────────
from config import * # importa todas as variáveis do config.py
from wifi_connect import conectar_wifi
from umqtt.simple import MQTTClient  # biblioteca MQTT nativa do MicroPython
import utime                         # IMPORTANTE: Importa o módulo completo para usar ticks_ms
from machine import Pin, ADC, PWM

# ── 1. Conexão WiFi ───────────────────────────────────────────────
if not conectar_wifi(WIFI_SSID, WIFI_PASS):
    print("[MAIN] Sem WiFi. Reinicie o dispositivo.")

else:
    # ── 2. Cliente MQTT ───────────────────────────────────────────
    cliente = MQTTClient(CLIENT_ID, BROKER_IP, port=BROKER_PORT)

    try:
        cliente.connect()
        print(f"[MQTT] Conectado ao broker: {BROKER_IP}")
        print(f"[MQTT] Publicando em: {TOPIC_PUB}")

        # =====================================================
        # CONFIGURAÇÕES DA LUMINÁRIA
        # =====================================================
        TEMPO_SEM_MOVIMENTO = 30000   # 30 segundos
        DEBOUNCE_MS = 200
        INTERVALO_MQTT = 3000         # Envia dados ao MQTT a cada 3 segundos

        LIMIAR_ESCURO = 15000         
        LIMIAR_CLARO = 45000          
        PASSO_INTENSIDADE = 5000

        # =====================================================
        # HARDWARE
        # =====================================================
        pir = Pin(2, Pin.IN)
        ldr = ADC(26)

        led = PWM(Pin(14))
        led.freq(1000)

        btn_modo = Pin(3, Pin.IN, Pin.PULL_UP)
        btn_menos = Pin(16, Pin.IN, Pin.PULL_UP)
        btn_mais = Pin(17, Pin.IN, Pin.PULL_UP)

        # =====================================================
        # ESTADOS E VARIÁVEIS DE CONTROLE
        # =====================================================
        MODO_AUTOMATICO = 0
        MODO_ESTUDO = 1
        modo = MODO_AUTOMATICO

        brilho_atual = 0  # Armazena o brilho atual para enviar via MQTT
        ultima_deteccao = utime.ticks_ms()
        ultimo_envio_mqtt = utime.ticks_ms()
        intensidade_manual = 30000

        ultimo_modo_press = 0
        ultimo_menos_press = 0
        ultimo_mais_press = 0

        modo_anterior = 1
        menos_anterior = 1
        mais_anterior = 1

        # =====================================================
        # FUNÇÕES AUXILIARES
        # =====================================================
        def set_brilho(valor):
            global brilho_atual
            valor = max(0, min(65535, valor))
            led.duty_u16(valor)
            brilho_atual = valor

        def ler_luminosidade():
            return ldr.read_u16()

        def brilho_automatico():
            leitura = ler_luminosidade()
            if leitura <= LIMIAR_ESCURO:
                return 65535
            elif leitura >= LIMIAR_CLARO:
                return 0
            else:
                faixa = LIMIAR_CLARO - LIMIAR_ESCURO
                relacao = (LIMIAR_CLARO - leitura) / faixa
                brilho = int(relacao * 65535)
                return max(3000, brilho)

        def botao_pressionado(botao, estado_anterior, ultimo_tempo):
            atual = botao.value()
            agora = utime.ticks_ms()
            pressionado = False

            if estado_anterior == 1 and atual == 0:
                if utime.ticks_diff(agora, ultimo_tempo) > DEBOUNCE_MS:
                    pressionado = True
                    ultimo_tempo = agora

            return pressionado, atual, ultimo_tempo

        def verificar_botoes():
            global modo, intensidade_manual
            global ultimo_modo_press, ultimo_menos_press, ultimo_mais_press
            global modo_anterior, menos_anterior, mais_anterior

            pressionou, modo_anterior, ultimo_modo_press = botao_pressionado(
                btn_modo, modo_anterior, ultimo_modo_press
            )

            if pressionou:
                if modo == MODO_AUTOMATICO:
                    modo = MODO_ESTUDO
                    print(">>> MODO ESTUDO ATIVADO <<<")
                else:
                    modo = MODO_AUTOMATICO
                    print(">>> MODO AUTOMATICO ATIVADO <<<")

            if modo == MODO_ESTUDO:
                pressionou, menos_anterior, ultimo_menos_press = botao_pressionado(
                    btn_menos, menos_anterior, ultimo_menos_press
                )
                if pressionou:
                    intensidade_manual = max(0, intensidade_manual - PASSO_INTENSIDADE)
                    print("Brilho manual:", intensidade_manual)

                pressionou, mais_anterior, ultimo_mais_press = botao_pressionado(
                    btn_mais, mais_anterior, ultimo_mais_press
                )
                if pressionou:
                    intensidade_manual = min(65535, intensidade_manual + PASSO_INTENSIDADE)
                    print("Brilho manual:", intensidade_manual)

        def executar_modo_automatico():
            global ultima_deteccao
            agora = utime.ticks_ms()
            movimento = pir.value()

            if movimento:
                ultima_deteccao = agora
                brilho = brilho_automatico()
                set_brilho(brilho)
            else:
                tempo_sem_movimento = utime.ticks_diff(agora, ultima_deteccao)
                if tempo_sem_movimento >= TEMPO_SEM_MOVIMENTO:
                    set_brilho(0)

        def executar_modo_estudo():
            set_brilho(intensidade_manual)

        # =====================================================
        # INICIALIZAÇÃO
        # =====================================================
        print("================================")
        print("   SISTEMA LUZ INTELIGENTE      ")
        print("================================")
        print("Modo inicial: AUTOMATICO\n")
        
        set_brilho(0)

        # =====================================================
        # LOOP PRINCIPAL
        # =====================================================
        while True:
            verificar_botoes()

            if modo == MODO_AUTOMATICO:
                executar_modo_automatico()
            else:
                executar_modo_estudo()

            # ── Envio de Dados via MQTT (Sem travar o código) ──
            agora_mqtt = utime.ticks_ms()
            if utime.ticks_diff(agora_mqtt, ultimo_envio_mqtt) >= INTERVALO_MQTT:
                # Cria uma mensagem com o status atual do sistema
                nome_modo = "AUTOMATICO" if modo == MODO_AUTOMATICO else "ESTUDO"
                mensagem = f"Modo: {nome_modo} | Brilho LED: {brilho_atual} | LDR: {ler_luminosidade()}"
                
                try:
                    cliente.publish(TOPIC_PUB, mensagem)
                    print(f"[MQTT] Enviado: {mensagem}")
                except Exception as e:
                    print(f"[MQTT] Erro ao publicar: {e}")
                
                ultimo_envio_mqtt = agora_mqtt

            utime.sleep_ms(50)

    except Exception as e:
        print(f"[ERRO] {e}")
        print("[MQTT] Verifique o broker e a conexão WiFi.")

    finally:
        try:
            cliente.disconnect()
            print("[MQTT] Desconectado.")
        except:
            pass