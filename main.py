import time
import random  # <--- Faltava este import
from database import buscar_ofertas_nao_convertidas, atualizar_link_afiliado
from Playright_bot_search import buscar_promos_perfil_real
from conversor import converter_link_shopee


def executar_ciclo_completo():
    # 1. Busca novas ofertas
    print("\n--- 🔎 INICIANDO BUSCA DE OFERTAS ---")
    buscar_promos_perfil_real()

    # 2. Busca o que precisa converter
    print("\n--- 🔗 INICIANDO CONVERSÃO DE LINKS ---")
    ofertas = buscar_ofertas_nao_convertidas()

    if not ofertas:
        print("✅ Tudo atualizado!")
        return

    print(f"Encontradas {len(ofertas)} ofertas para converter.")

    for id_db, link_orig in ofertas:
        try:
            link_afiliado = converter_link_shopee(link_orig)

            if link_afiliado:
                atualizar_link_afiliado(id_db, link_afiliado)
                print(f"✅ ID {id_db} convertido: {link_afiliado}")
            else:
                print(f"⚠️ Falha ao converter ID {id_db}")

            # Pausa para evitar bloqueio por velocidade no painel
            espera = random.uniform(3, 7)
            print(f"Aguardando {espera:.2f}s para o próximo...")
            time.sleep(espera)

        except Exception as e:
            print(f"❌ Erro no ciclo: {e}")


if __name__ == "__main__":
    executar_ciclo_completo()