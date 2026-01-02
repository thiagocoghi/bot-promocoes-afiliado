import time
import random
from Playright_bot_search import buscar_promos_perfil_real
from conversor import executar_conversao_em_lote
from postador_whatsapp import postar_no_whatsapp
from database import buscar_ofertas_nao_convertidas
from logs import log_info
from datetime import datetime



def iniciar_sistema_automatico():
    log_info("\n" + "-" *40 + "\n" + "🤖 Sistema de Orquestração Iniciado.\n" + "-" * 40)
    while True:
        # Modo Dormir (00h às 07h)
        hora_atual = datetime.now().hour
        hora_atual -=5
        if 0 <= hora_atual< 7:
            log_info(f"💤 Horário de descanso ({hora_atual}h). Aguardando amanhecer...")
            time.sleep(1800)
            continue

        # Início do Ciclo
        log_info("🔄 Verificando banco de dados...")
        print("\n" + "=" * 40)
        print("🤖 VERIFICANDO FILA DE TRABALHO")
        print("=" * 40)

        # 1. Checa se precisa de novos links da Shopee
        links_brutos = buscar_ofertas_nao_convertidas(limite=1)
        if not links_brutos:
            log_info("📭 Estoque vazio. Buscando novas promoções na Shopee...")

            print("📭 Estoque vazio. Buscando novas promoções na Shopee...")
            buscar_promos_perfil_real()
        else:
            log_info("📦 Links pendentes encontrados no banco. Pulando busca." + "\n" + "-" * 80)
            print("📦 Links pendentes encontrados no banco. Pulando busca.")

        # 2. Converte o que houver no banco (até 5 por vez)
        log_info("🔗 Iniciando conversão de lote...")
        print("🔗 Convertendo links para afiliado...")
        executar_conversao_em_lote(limite=5)

        # 3. Postagem das 5 ofertas
        log_info("📱 Iniciando ciclo de 5 postagens... \n" + "-" * 80)
        print("📱 Iniciando ciclo de postagem...")
        for i in range(5):
            sucesso = postar_no_whatsapp()

            if sucesso:
                # Se for a última das 5, não precisa esperar 20 min para fechar o ciclo
                if i < 4:
                    tempo = random.randint(900, 1500)  # Entre 15 e 25 minutos
                    log_info(f"⏳ Pausa de segurança: {tempo // 60} minutos.\n" + "-" * 80)
                    print(f"⏳ Pausa de segurança: {tempo // 60} minutos...")
                    time.sleep(tempo)
            else:
                print("📭 Sem mais ofertas convertidas no momento.")
                break
        log_info("✅ Ciclo de lote finalizado. Reiniciando em 10s...\n" + "-" * 80)
        print("\n✅ Ciclo concluído. Reiniciando em 10 segundos...")
        time.sleep(10)


if __name__ == "__main__":
    iniciar_sistema_automatico()