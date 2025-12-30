import time
from Playright_bot_search import buscar_promos_perfil_real  # Nome da sua função de busca
from main import processar_conversao  # Nome da sua função que converte links
from postador_whatsapp import postar_no_whatsapp


def ciclo_de_vendas():
    while True:
        print("\n\n🔄 --- INICIANDO NOVO CICLO DE TRABALHO ---")

        # 1. Busca novas ofertas
        print("🔎 Fase 1: Buscando oportunidades...")
        buscar_promos_perfil_real()

        # 2. Converte o que encontrou
        print("🔗 Fase 2: Convertendo links para afiliado...")
        processar_conversao()

        # 3. Postagem com intervalo (para não ser banido e não fazer spam)
        print("📱 Fase 3: Iniciando sequência de postagens...")

        # Tenta postar 5 ofertas por ciclo, com 10 minutos entre elas
        for _ in range(5):
            sucesso = postar_no_whatsapp()
            if sucesso:
                print("⏳ Aguardando 10 minutos para a próxima postagem...")
                time.sleep(600)  # 600 segundos = 10 minutos
            else:
                print("📭 Sem ofertas prontas para postar. Encerrando ciclo de envio.")
                break

        print("💤 Ciclo finalizado. O bot vai descansar por 1 hora antes de buscar mais.")
        time.sleep(3600)  # Espera 1 hora para buscar de novo


if __name__ == "__main__":
    ciclo_de_vendas()