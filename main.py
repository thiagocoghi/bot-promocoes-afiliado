import time
from database import iniciar_db, limpar_banco_de_dados
# Supondo que você tenha suas funções principais no orquestrador
from orquestrador import iniciar_sistema_automatico
from logs import log_info, log_erro

# CONFIGURAÇÃO DE TEMPO
INTERVALO_LIMPEZA = 6 * 60 * 60  # 6 horas (em segundos)


def main():
    # 1. Preparação Inicial
    iniciar_db()
    log_info("🤖 Bot iniciado! Banco de dados conectado.")

    # Define a ultima limpeza para AGORA, para ele não limpar logo de cara (ou 0 se quiser que limpe já)
    ultima_limpeza = time.time()

    # 2. Loop Infinito
    while True:
        try:
            # --- TAREFA A: Limpeza do Banco (Manutenção) ---
            agora = time.time()
            if agora - ultima_limpeza > INTERVALO_LIMPEZA:
                log_info("🧹 Iniciando rotina de limpeza agendada...")
                limpar_banco_de_dados(dias=2)
                ultima_limpeza = agora  # Reseta o cronômetro

            # --- TAREFA B: Executar o trabalho real (Orquestrador) ---
            # Aqui chamamos o orquestrador para buscar, converter e postar
            iniciar_sistema_automatico()

            # --- TAREFA C: Descanso ---
            time.sleep(1)

        except KeyboardInterrupt:
            log_info("🛑 Bot parado pelo usuário.")
            break
        except Exception as e:
            log_erro(f"💥 Erro fatal no Loop Principal: {e}")
            time.sleep(10)  # Espera um pouco antes de tentar reiniciar o loop


if __name__ == "__main__":
    main()