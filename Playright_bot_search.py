from playwright.sync_api import sync_playwright
import os
import time
import random


def buscar_promos_perfil_real():
    user_data_dir = os.path.join(os.getcwd(), "perfil_shopee")

    with sync_playwright() as p:
        print("🚀 Abrindo navegador com perfil salvo...")

        context = p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
            viewport={'width': 1280, 'height': 720}
        )

        page = context.new_page()

        try:
            print("🔗 Acessando Shopee...")
            # Aumentamos o timeout para lidar com o redirecionamento pós-login
            page.goto("https://shopee.com.br/flash_sale", wait_until="load", timeout=90000)

            print("⏳ Aguardando estabilização da página...")
            # Espera um pouco mais caso o site esteja processando o login
            time.sleep(10)

            # Rola a página aos poucos para carregar os produtos (Lazy Load)
            print("🖱️ Carregando produtos...")
            for _ in range(3):
                page.mouse.wheel(0, 800)
                time.sleep(2)

            # O seletor da Shopee pode mudar. Vamos tentar um mais genérico se o específico falhar
            selector = ".flash-sale-item-card"

            try:
                page.wait_for_selector(selector, timeout=15000)
                cards = page.query_selector_all(selector)

                if cards:
                    print(f"✅ Sucesso! Encontrados {len(cards)} produtos.")
                    for item in cards[:5]:
                        nome = item.query_selector(".flash-sale-item-card__item-name").inner_text()
                        print(f"📦 {nome}")
                else:
                    print("⚠️ Seletor encontrado, mas sem itens dentro.")
            except:
                print("⚠️ Seletor específico não encontrado. Tentando captura alternativa...")
                # Backup: tenta pegar qualquer link que pareça um produto
                links = page.query_selector_all("a[href*='product']")
                print(f"Encontrados {len(links)} links de produtos via backup.")

        except Exception as e:
            print(f"❌ Erro: {e}")

        finally:
            print("Encerrando... Não feche a janela manualmente, o script fará isso.")
            time.sleep(5)
            context.close()


if __name__ == "__main__":
    buscar_promos_perfil_real()