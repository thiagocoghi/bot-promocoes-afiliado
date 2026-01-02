import time
import random
from Playright_bot_search import buscar_promos_perfil_real
from conversor import executar_conversao_em_lote
from postador_whatsapp import postar_no_whatsapp
from database import buscar_ofertas_nao_convertidas
from logs import log_info
from datetime import datetime


def iniciar_sistema_automatico(callback_log=None, checar_parada=None):
    """Executa UM ciclo completo de trabalho (Busca -> Conversão -> Postagem)"""

    def avisar(texto):
        if callback_log:
            callback_log(texto)
        print(texto)
        log_info(texto)

    # --- VERIFICAÇÃO DE PARADA INICIAL ---
    if checar_parada and not checar_parada(): return

    # Modo Dormir (00h às 07h) - Ajustado para -3h (Horário de Brasília comum) ou seu offset
    hora_atual = datetime.now().hour
    hora_atual-=5
    if 0 <= hora_atual < 7:
        avisar(f"💤 Horário de descanso ({hora_atual}h).")
        return

    avisar("\n" + "=" * 40)
    avisar("🤖 VERIFICANDO FILA DE TRABALHO")
    avisar("=" * 40)

    # 1. BUSCA DE PROMOÇÕES
    if checar_parada and not checar_parada(): return

    links_brutos = buscar_ofertas_nao_convertidas(limite=1)
    if not links_brutos:
        avisar("📭 Estoque vazio. Buscando novas promoções na Shopee...")
        # Adicione suporte a interrupção dentro da buscar_promos_perfil_real se necessário
        buscar_promos_perfil_real()
    else:
        avisar("📦 Links pendentes encontrados no banco. Pulando busca.")

    # 2. CONVERSÃO EM LOTE
    if checar_parada and not checar_parada(): return

    avisar("🔗 Convertendo links para afiliado...")
    # Passamos os controles para dentro do conversor
    executar_conversao_em_lote(limite=5, callback_log=callback_log, checar_parada=checar_parada)

    # 3. POSTAGEM (Ciclo de 5)
    avisar("📱 Iniciando ciclo de postagem...")
    for i in range(5):
        # --- VERIFICAÇÃO DE PARADA ANTES DE CADA POSTAGEM ---
        if checar_parada and not checar_parada():
            avisar("🛑 Interrompendo ciclo de postagens conforme solicitado.")
            break

        # Passamos os controles para dentro do postador
        sucesso = postar_no_whatsapp(callback_log=callback_log, checar_parada=checar_parada)

        if sucesso:
            if i < 4:  # Se não for a última
                tempo = random.randint(900, 1500)  # 15 a 25 min
                avisar(f"⏳ Pausa de segurança: {tempo // 60} minutos...")

                # Sleep inteligente: permite desligar o bot DURANTE a pausa
                for _ in range(tempo):
                    if checar_parada and not checar_parada(): break
                    time.sleep(1)
        else:
            avisar("📭 Sem mais ofertas prontas para postar agora.")
            break

    avisar("\n✅ Ciclo finalizado com sucesso.")


if __name__ == "__main__":
    # Para testes manuais via terminal
    iniciar_sistema_automatico()