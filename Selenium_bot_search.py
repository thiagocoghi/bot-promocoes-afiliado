import os

from playwright.sync_api import sync_playwright
import time
import random


def buscar_promos():
    # Verifica se o arquivo de sessão existe
    if not os.path.exists("auth.json"):
        print("❌ Erro: arquivo 'auth.json' não encontrado! Rode o 'gerar_sessao.py' primeiro.")
        return

    with sync_playwright() as p:

        print("🚀 Iniciando navegador com sua sessão logada...")
        # Lançamos o navegador com argumentos que ajudam a evitar detecção
        browser = p.chromium.launch(headless=False, args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox"
        ])

        context = browser.new_context(
            storage_state="auth.json",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 720}
        )

        page = context.new_page()

        # Scripts manuais para esconder que é um bot (o que o stealth faria)
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'languages', {get: () => ['pt-BR', 'pt', 'en']});
        """)

        try:
            print("Acessando Shopee...")
            # Vamos para a home primeiro para "aquecer" a sessão
            page.goto("https://shopee.com.br", wait_until="domcontentloaded", timeout=60000)
            time.sleep(random.uniform(3, 5))

            # Agora vamos para as ofertas relâmpago
            page.goto("https://shopee.com.br/flash_sale", wait_until="domcontentloaded")

            print("Aguardando carregamento dos produtos...")
            # Espera 10 segundos para o conteúdo dinâmico carregar
            time.sleep(10)

            # Rola a página para ativar o lazy load
            page.mouse.wheel(0, 1500)
            time.sleep(2)

            # Busca os nomes dos produtos
            # Seletor atualizado para garantir a captura
            produtos = page.query_selector_all(".flash-sale-item-card")

            if produtos:
                print(f"✅ Sucesso! Encontrados {len(produtos)} produtos.")
                for item in produtos[:5]:
                    nome = item.query_selector(".flash-sale-item-card__item-name").inner_text()
                    print(f"📦 {nome}")
            else:
                print("⚠️ Nenhum produto encontrado. Verifique a imagem 'debug.png'")
                page.screenshot(path="debug.png")

        except Exception as e:
            print(f"❌ Erro: {e}")
            page.screenshot(path="erro_fatal.png")

        finally:
            print("Fechando navegador...")
            time.sleep(5)
            browser.close()


if __name__ == "__main__":
    dados = buscar_promos()
    print(f"\nBusca finalizada. {len(dados)} itens prontos para conversão.")