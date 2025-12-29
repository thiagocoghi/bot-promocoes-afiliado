from playwright.sync_api import sync_playwright
import os
import time


def converter_link_shopee(link_original):
    if not os.path.exists("auth.json"):
        return "Erro: auth.json não encontrado. Gere a sessão primeiro."

    with sync_playwright() as p:
        # Abrimos o navegador usando a sessão salva
        browser = p.chromium.launch(headless=False)  # Mantenha True depois que testar
        context = browser.new_context(storage_state="auth.json")
        page = context.new_page()

        try:
            print(f"Convertendo link: {link_original}")
            # URL da ferramenta de link personalizado
            page.goto("https://affiliate.shopee.com.br/promotion/custom_link")

            # Aguarda o campo de input aparecer
            # O seletor pode variar, mas geralmente é um textarea ou input
            page.wait_for_selector('textarea[placeholder*="link"]')

            # Limpa e preenche o link
            page.fill('textarea[placeholder*="link"]', link_original)

            # Clica no botão "Obter Link" (Get Link)
            # Vamos usar o texto do botão para facilitar
            page.click('button:has-text("Obter Link"), button:has-text("Get Link")')

            # Espera o link convertido aparecer no campo de resultado
            time.sleep(3)

            # Pega o valor do link curto gerado
            # Geralmente fica em um input novo que aparece na tela
            link_convertido = page.query_selector('div.short-link-display input, .final-link-input').get_attribute(
                'value')

            print(f"✅ Link de Afiliado: {link_convertido}")
            return link_convertido

        except Exception as e:
            print(f"❌ Erro na conversão: {e}")
            return None
        finally:
            browser.close()


# Teste rápido
if __name__ == "__main__":
    link_teste = "https://shopee.com.br/product/123456/78910"
    converter_link_shopee(link_teste)