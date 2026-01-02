from playwright.sync_api import sync_playwright
import os
import time
import random
from database import iniciar_db, salvar_oferta
from logs import log_info, log_erro


def buscar_promos_perfil_real():
    # 1. Inicializa o Banco de Dados
    iniciar_db()

    user_data_dir = os.path.join(os.getcwd(), "perfil_shopee")
    novas_ofertas= 0

    with sync_playwright() as p:
        print("🚀 Abrindo navegador...")
        context = p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
            viewport={'width': 1280, 'height': 720}
        )

        page = context.new_page()

        try:
            print("🔗 Acessando Ofertas Relâmpago...")
            page.goto("https://shopee.com.br/flash_sale", wait_until="load", timeout=90000)

            time.sleep(8)

            print("🖱️ Rolando para carregar produtos...")
            for i in range(5):
                page.mouse.wheel(0, 600)
                time.sleep(1.5)

            # Localiza os elementos
            print("🔍 Analisando elementos da página...")
            # Definimos como lista vazia por segurança antes de buscar
            produtos_encontrados = page.locator('a[href*="-i."]').all()

            if len(produtos_encontrados) > 0:
                print(f"✅ Encontrei {len(produtos_encontrados)} possíveis links.")

                for i, link_element in enumerate(produtos_encontrados[:20]):
                    try:
                        # 1. Captura o Link e o Texto Bruto para análise rápida
                        link = link_element.get_attribute("href")
                        link_completo = f"https://shopee.com.br{link}" if link.startswith("/") else link

                        # 2. Captura o Nome do Produto (Classe EAIlz5)
                        nome_el = link_element.locator('.EAIlz5')
                        nome = nome_el.inner_text().strip() if nome_el.count() > 0 else "Produto sem nome"

                        # 3. Captura o Preço ANTIGO (Classe qukW3P - o valor riscado)
                        # No seu HTML: <strong class="iwH3_q">253,89</strong> dentro da div qukW3P
                        preco_antigo_el = link_element.locator('.qukW3P .iwH3_q')
                        preco_antigo = f"R$ {preco_antigo_el.inner_text().strip()}" if preco_antigo_el.count() > 0 else "---"

                        # 4. Captura o Preço ATUAL (Classe w6Dcnx - o valor da oferta)
                        # No seu HTML: <strong class="iwH3_q">182,90</strong> dentro da div w6Dcnx
                        preco_atual_el = link_element.locator('.w6Dcnx .iwH3_q')
                        preco_atual = f"R$ {preco_atual_el.inner_text().strip()}" if preco_atual_el.count() > 0 else "Consultar"

                        # 5. Captura a Porcentagem de Desconto (Opcional, mas ótimo para o post)
                        desconto_el = link_element.locator('.EKx6p6')
                        desconto = desconto_el.inner_text().strip() if desconto_el.count() > 0 else ""

                        # SALVAR NO BANCO
                        if nome and preco_atual != "Consultar":
                            # Podemos concatenar o desconto ao nome ou criar uma coluna nova
                            nome_com_desconto = f"{nome} ({desconto})" if desconto else nome

                            foi_salvo = salvar_oferta(nome_com_desconto, preco_atual, preco_antigo, link_completo)
                            if foi_salvo:
                                novas_ofertas += 1  # Incrementa apenas se for uma oferta nova
                                print(f"✨ SALVO: {preco_antigo} -> {preco_atual} | {nome[:30]}...")

                    except Exception as e:
                        print(f"⚠️ Erro ao processar item: {e}")
                        continue
            else:
                print("⚠️ Nenhum produto encontrado na página.")
                log_info("⚠️ Nenhum produto encontrado na página de Ofertas Relâmpago." + "-" * 80)

        except Exception as e:
            print(f"❌ Erro crítico: {e}")
            log_erro(f"❌ Erro crítico na busca de promoções: {e}\n" + "-" * 80)

        finally:
            print(f"\n📊 Resumo: {novas_ofertas} novas ofertas salvas no Banco de Dados.")
            log_info(f"📊 Resumo: {novas_ofertas} novas ofertas salvas no Banco de Dados.\n Fechando busca de promoções.\n" + "-" * 80)
            print("Encerrando...")
            time.sleep(5)
            context.close()



if __name__ == "__main__":
    buscar_promos_perfil_real()

