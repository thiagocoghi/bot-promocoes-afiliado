from playwright.sync_api import sync_playwright
import time
import os

def buscar_promos_logado():
    if not os.path.exists("auth.json"):
        print("Erro: Arquivo auth.json não encontrado. Rode o 'gerar_sessao.py' primeiro.")
        return

    with sync_playwright() as p:
        # Iniciamos o navegador usando o estado salvo
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state="auth.json")
        page = context.new_page()

        try:
            print("Acessando Shopee já logado...")
            page.goto("https://shopee.com.br/flash_sale")

            # Rola a página para carregar itens (Lazy Loading)
            page.mouse.wheel(0, 1000)
            time.sleep(3)

            # O Playwright usa seletores CSS de forma muito eficiente
            # Vamos buscar os cards de produtos
            produtos = page.query_selector_all(".flash-sale-item-card")

            print(f"Encontrados {len(produtos)} produtos.")

            for item in produtos[:10]:
                try:
                    nome = item.query_selector(".flash-sale-item-card__item-name").inner_text()
                    preco = item.query_selector(".flash-sale-item-card__current-price").inner_text()
                    # O link geralmente está no elemento pai ou em um 'a' interno
                    link_element = item.query_selector("a")
                    link = "https://shopee.com.br" + link_element.get_attribute(
                        "href") if link_element else "Link não encontrado"

                    print(f"🔥 PROMO: {nome}\n💰 POR: {preco}\n🔗 LINK: {link}\n{'-' * 20}")
                except Exception as e:
                    continue

            print("Sucesso! Aguardando 10 segundos antes de fechar...")
            time.sleep(10)

        finally:
            browser.close()


if __name__ == "__main__":
    buscar_promos_logado()