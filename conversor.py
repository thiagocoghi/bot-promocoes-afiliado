from playwright.sync_api import sync_playwright
import os
import time
from database import buscar_ofertas_nao_convertidas, atualizar_link_afiliado
from logs import log_info, log_erro


def converter_link_shopee(page, link_original, callback_log=None, checar_parada=None):
    """
    Versão otimizada: Agora recebe a 'page' já aberta para economizar tempo.
    """

    def avisar(texto):
        if callback_log: callback_log(texto)
        print(texto)
        log_info(texto)

    try:
        if checar_parada and not checar_parada():
            return None

        avisar(f"🔄 Convertendo: {link_original[:40]}...")

        # Vai para a página de conversão (apenas se já não estiver nela)
        if page.url != "https://affiliate.shopee.com.br/offer/custom_link":
            page.goto("https://affiliate.shopee.com.br/offer/custom_link", wait_until="networkidle", timeout=60000)

        if checar_parada and not checar_parada(): return None

        # Limpa e preenche a textarea
        textarea = page.wait_for_selector('textarea', timeout=20000)
        textarea.fill("")  # Garante que está vazio
        textarea.fill(link_original)

        page.click('button:has-text("Obter Link"), button:has-text("Get Link")')

        # Espera o modal de sucesso
        seletor_modal_link = ".success-modal-content textarea"
        page.wait_for_selector(seletor_modal_link, timeout=15000)

        link_final = page.locator(seletor_modal_link).input_value()

        if link_final and "shopee.com.br" in link_final:
            # Fecha o modal para a próxima conversão não bugar
            page.keyboard.press("Escape")
            return link_final.strip()

        return None

    except Exception as e:
        if "closed" in str(e).lower() or "target" in str(e).lower():
            return None

        # Erro de timeout (ex: site da shopee lento)
        if "timeout" in str(e).lower():
            avisar("⚠️ Timeout na Shopee. Tentando limpar para o próximo...")
            page.reload()
            return None

        avisar(f"❌ Erro no conversor: {e}")
        log_erro(f"Erro no conversor: {e}")
        return None


def executar_conversao_em_lote(limite=5, callback_log=None, checar_parada=None):
    from database import buscar_ofertas_nao_convertidas, atualizar_link_afiliado

    ofertas = buscar_ofertas_nao_convertidas(limite=limite)

    if not ofertas:
        if callback_log: callback_log("📭 Sem ofertas para converter.")
        return False

    user_data_dir = os.path.join(os.getcwd(), "perfil_shopee")

    # ABRIMOS O BROWSER UMA ÚNICA VEZ PARA O LOTE TODO
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = browser.new_page()

        for id_db, link_original in ofertas:
            if checar_parada and not checar_parada():
                break

            link_afiliado = converter_link_shopee(page, link_original, callback_log, checar_parada)

            if link_afiliado:
                atualizar_link_afiliado(id_db, link_afiliado)
                if callback_log: callback_log(f"✅ Oferta {id_db} salva!")
            else:
                # Se falhou por parada do usuário, não loga erro
                if checar_parada and checar_parada():
                    if callback_log: callback_log(f"❌ Falha na oferta {id_db}")

        browser.close()

    return True