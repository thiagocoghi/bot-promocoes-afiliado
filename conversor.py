from playwright.sync_api import sync_playwright
import os
import time


def converter_link_shopee(link_original):
    user_data_dir = os.path.join(os.getcwd(), "perfil_shopee")

    with sync_playwright() as p:
        # Usa o mesmo perfil do scraper
        browser = p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,  # Mantenha False para ver se ele acerta o campo
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = browser.new_page()  # Aqui definimos o 'page' corretamente

        try:
            print(f"🔄 Acessando painel para converter...")
            page.goto("https://affiliate.shopee.com.br/promotion/custom_link", wait_until="networkidle", timeout=60000)

            # Aguarda o campo de texto (textarea)
            page.wait_for_selector('textarea', timeout=15000)
            page.fill('textarea', link_original)

            # Clica no botão de obter link
            # Tentamos pelo texto do botão que é mais estável
            page.click('button:has-text("Obter Link"), button:has-text("Get Link")')

            # Aguarda o link curto aparecer (geralmente em um input ou div específica)
            time.sleep(5)

            # Captura o link curto gerado
            # O seletor abaixo busca o input que contém o link convertido
            link_convertido = page.locator(
                'div.short-link-display input, .final-link-input, input[readonly]').first.get_attribute('value')

            if link_convertido and "shope.ee" in link_convertido:
                return link_convertido
            return None

        except Exception as e:
            print(f"❌ Erro interno no conversor: {e}")
            return None
        finally:
            browser.close()