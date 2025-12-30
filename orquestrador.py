import time
import random
from Playright_bot_search import buscar_promos_perfil_real
from conversor import executar_conversao_em_lote
from postador_whatsapp import postar_no_whatsapp
from database import buscar_ofertas_nao_convertidas


def iniciar_sistema_automatico():
    while True:
        print("\n" + "=" * 40)
        print("🤖 VERIFICANDO FILA DE TRABALHO")
        print("=" * 40)

        # 1. Checa se precisa de novos links da Shopee
        links_brutos = buscar_ofertas_nao_convertidas(limite=1)
        if not links_brutos:
            print("📭 Estoque vazio. Buscando novas promoções na Shopee...")
            buscar_promos_perfil_real()
        else:
            print("📦 Links pendentes encontrados no banco. Pulando busca.")

        # 2. Converte o que houver no banco (até 5 por vez)
        print("🔗 Convertendo links para afiliado...")
        executar_conversao_em_lote(limite=5)

        # 3. Postagem das 5 ofertas
        print("📱 Iniciando ciclo de postagem...")
        for i in range(5):
            sucesso = postar_no_whatsapp()

            if sucesso:
                # Se for a última das 5, não precisa esperar 20 min para fechar o ciclo
                if i < 4:
                    tempo = random.randint(900, 1500)
                    print(f"⏳ Pausa de segurança: {tempo // 60} minutos...")
                    time.sleep(tempo)
            else:
                print("📭 Sem mais ofertas convertidas no momento.")
                break

        print("\n✅ Ciclo concluído. Reiniciando em 10 segundos...")
        time.sleep(10)


if __name__ == "__main__":
    iniciar_sistema_automatico()