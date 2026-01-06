from playwright.sync_api import sync_playwright
import os
import time
from database import atualizar_link_afiliado, buscar_ofertas_por_termo_para_converter
from logs import log_info, log_erro

def converter_link_shopee(page, link_original, callback_log=None, checar_parada=None):
    """
    Versão otimizada: Recebe a 'page' aberta e realiza a conversão.
    """
    def avisar(texto):
        if callback_log: callback_log(texto)
        print(texto)
        log_info(texto)

    try:
        if checar_parada and not checar_parada():
            return None

        avisar(f"🔄 Convertendo: {link_original[:40]}...")

        # Garante que está na página de link personalizado
        if "custom_link" not in page.url:
            page.goto("https://affiliate.shopee.com.br/offer/custom_link", wait_until="networkidle", timeout=60000)

        if checar_parada and not checar_parada(): return None

        # Localiza e preenche o link
        textarea = page.wait_for_selector('textarea', timeout=20000)
        textarea.fill("")
        textarea.fill(link_original)

        # Clica no botão de gerar
        page.click('button:has-text("Obter Link"), button:has-text("Get Link")')

        # Espera o modal de sucesso com o link pronto
        seletor_modal_link = ".success-modal-content textarea"
        page.wait_for_selector(seletor_modal_link, timeout=15000)

        link_final = page.locator(seletor_modal_link).input_value()

        if link_final and "shopee.com.br" in link_final:
            page.keyboard.press("Escape") # Fecha o modal para o próximo item
            return link_final.strip()

        return None

    except Exception as e:
        if "closed" in str(e).lower() or "target" in str(e).lower():
            return None
        if "timeout" in str(e).lower():
            avisar("⚠️ Timeout na Shopee. Tentando limpar para o próximo...")
            page.reload()
            return None

        avisar(f"❌ Erro no conversor: {e}")
        log_erro(f"Erro no conversor: {e}")
        return None


def executar_conversao_em_lote(limite=5, callback_log=None, checar_parada=None, usuario="padrao", termo_pesquisa=""):
    """
    Agora filtra as ofertas pelo TERMO_PESQUISA para evitar misturar categorias.
    """
    # ALTERAÇÃO CHAVE: Busca apenas o que pertence ao assunto atual
    ofertas = buscar_ofertas_por_termo_para_converter(termo=termo_pesquisa, limite=limite, usuario=usuario)

    if not ofertas:
        msg = f"📭 Sem ofertas de '{termo_pesquisa or 'Flash Sale'}' para converter."
        if callback_log: callback_log(msg)
        return False

    user_data_dir = os.path.join(os.getcwd(), f"perfil_{usuario}")

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
                atualizar_link_afiliado(id_db, link_afiliado, usuario=usuario)
                if callback_log: callback_log(f"✅ Oferta {id_db} convertida e salva!")
            else:
                if callback_log: callback_log(f"❌ Falha na oferta {id_db}")

        browser.close()

    return True