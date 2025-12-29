from playwright.sync_api import sync_playwright


def salvar_sessao():
    with sync_playwright() as p:
        # Lançamos o navegador
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print("\n1. Navegador aberto. Faça o login na Shopee.")
        page.goto("https://affiliate.shopee.com.br/login")

        # Em vez de monitorar a janela, o Python espera um comando no terminal
        input("\n2. APÓS logar e entrar no painel, volte aqui e aperte ENTER para salvar...")

        # Salva o estado da sessão
        context.storage_state(path="auth.json")
        print("\n✅ Sucesso! O arquivo 'auth.json' foi gerado na pasta do projeto.")

        browser.close()


if __name__ == "__main__":
    salvar_sessao()
