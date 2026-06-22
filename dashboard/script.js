// script.js — Lógica do Dashboard
// ─────────────────────────────────────────────────────────────────

const BROKER = "ws://10.132.112.4:9001"  
const TOPICO = "senai/smartlight/temp"  // 🛠️ CORREÇÃO: Tudo em minúsculo para bater com o Python!

const CLIENT_ID = "dashboard_" + Math.random().toString(16).slice(2, 8)

// ── Elementos do HTML que vamos atualizar ────────────────────────
const statusDot      = document.getElementById("status-dot")
const statusTexto    = document.getElementById("status-texto")
const logEl          = document.getElementById("log")

// Cards (ldr, pir, status e modo)
const luz = document.getElementById('luz-valor')
const ldr = document.getElementById('ldr-valor')
const movimentoValor = document.getElementById('movimento-valor')
const modoValor = document.getElementById('modo-valor') // Faltava capturar o modo no seu JS original

// ── Funções auxiliares ────────────────────────────────────────────

function adicionarLog(texto, cor = "#8b949e") {
    const hora = new Date().toLocaleTimeString("pt-BR")
    logEl.innerHTML += `<span style="color:${cor}">[${hora}] ${texto}</span>\n`
    logEl.scrollTop = logEl.scrollHeight  
}

function atualizarStatus(conectado, texto) {
    statusDot.className  = "status-dot" + (conectado ? " conectado" : "")
    statusTexto.textContent = texto
}

// ── Exibir mensagem recebida ──────────────────────────────────────
function exibirMensagem(topico, mensagem) {
    try {
        const dados = JSON.parse(mensagem)

        if(luz && dados.status_luz !== undefined){
            luz.textContent = dados.status_luz === 'LIGADA' ? 'Ligada 💡' : 'Desligada 🌑';
        }

        if(ldr && dados.luminosidade !== undefined){
            ldr.textContent =  dados.luminosidade + ' lux';
        }

        if(movimentoValor && dados.movimento !== undefined){
            movimentoValor.textContent =  dados.movimento ? '🚶 Detectado' : 'Sem movimento';
        }

        if(modoValor && dados.modo !== undefined){
            modoValor.textContent = dados.modo;
        }

    } catch (erro) {
        console.error('A mensagem recebida não é um formato JSON válido:', mensagem)
    }

    adicionarLog(`[${topico}] ${mensagem}`, "#ffaa00");
}

// ── Conexão MQTT ──────────────────────────────────────────────────
adicionarLog(`Conectando em ${BROKER}...`)
const cliente = mqtt.connect(BROKER, {
    clientId: CLIENT_ID,
    clean: true  
})

cliente.on("connect", () => {
    atualizarStatus(true, "Conectado ao broker")
    adicionarLog("Conectado com sucesso!", "#00ff88")

    cliente.subscribe(TOPICO, (err) => {
        if (!err) {
            adicionarLog(`Assinando: "${TOPICO}"`)
        }
    })
})

cliente.on("message", (topico, payload) => {
    const mensagem = payload.toString()
    exibirMensagem(topico, mensagem)
})

cliente.on("error", (err) => {
    atualizarStatus(false, "Erro de conexão")
    adicionarLog(`ERRO: ${err.message}`, "#ff4444")
})

cliente.on("close", () => {
    atualizarStatus(false, "Desconectado")
    adicionarLog("Conexão encerrada.", "#ff4444")
})

// Card de Tempo Real
const data = document.querySelector('#data')
const hora = document.querySelector('#hora')

function atualizarRelogio() {
    const agora = new Date()
    data.innerHTML = agora.toLocaleDateString('pt-BR')
    hora.innerHTML = agora.toLocaleTimeString('pt-BR')
}

atualizarRelogio();
setInterval(atualizarRelogio, 1000)

// Configurações Botão
const TOPICO_COMANDO = "senai/smartlight/comando"; // Tópico corrigido com o nome "smartlight" do seu config.py

const btnLigar = document.querySelector('#btn-ligar')
const btnDesligar = document.querySelector('#btn-desligar')


// Evento do botão LIGAR LUZ
if (btnLigar) {
    btnLigar.addEventListener("click", () => {
        cliente.publish(TOPICO_COMANDO, "LIGAR", { qos: 0 }, (err) => {
            if (!err) {
                adicionarLog("[Enviado ➡️] Comando 'LIGAR' enviado para a iluminação.", "#00ff73");
            }
        });
    });
}

// Evento do botão DESLIGAR LUZ
if (btnDesligar) {
    btnDesligar.addEventListener("click", () => {
        cliente.publish(TOPICO_COMANDO, "DESLIGAR", { qos: 0 }, (err) => {
            if (!err) {
                adicionarLog("[Enviado ➡️] Comando 'DESLIGAR' enviado para a iluminação.", "#ff4444");
            }
        });
    });
}