from playwright.sync_api import sync_playwright
import os
import time
from database import buscar_ofertas_nao_convertidas, atualizar_link_afiliado
from logs import log_info, log_erro


def converter_link_shopee(link_original):
    user_data_dir = os.path.join(os.getcwd(), "perfil_shopee")

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = browser.new_page()

        try:
            print(f"🔄 Convertendo: {link_original[:50]}...")
            page.goto("https://affiliate.shopee.com.br/offer/custom_link", wait_until="networkidle")

            # 1. Preenche o link
            page.wait_for_selector('textarea', timeout=20000)
            page.fill('textarea', link_original)

            # 2. Clica no botão de gerar
            page.click('button:has-text("Obter Link"), button:has-text("Get Link")')

            print("⏳ Aguardando Pop-up de sucesso...")

            # 3. Espera o modal aparecer usando a classe que você identificou
            # Vamos esperar especificamente pela textarea dentro do modal
            seletor_modal_link = ".success-modal-content textarea"
            page.wait_for_selector(seletor_modal_link, timeout=15000)

            # 4. CAPTURA DO LINK
            # No caso de textareas, usamos .input_value() ou .inner_text()
            link_final = page.locator(seletor_modal_link).input_value()

            if not link_final or "shopee.com.br" not in link_final:
                # Backup caso o input_value falhe
                link_final = page.locator(seletor_modal_link).inner_text()

            if link_final:
                log_info(f"✅ Link capturado: {link_final}")
                print(f"✅ Link capturado: {link_final}")
                return link_final.strip()

            return None

        except Exception as e:
            print(f"❌ Erro no conversor: {e}")
            log_erro(f"❌ Erro no conversor: {e}❌")
            page.screenshot(path="debug_modal.png")  # Para análise caso mude de novo
            return None
        finally:
            browser.close()

    # Certifique-se de que NÃO existam espaços antes do 'def' abaixo


def executar_conversao_em_lote(limite=5):
    """Busca links brutos no banco e converte para link de afiliado."""
    from database import buscar_ofertas_nao_convertidas, atualizar_link_afiliado

    ofertas = buscar_ofertas_nao_convertidas(limite=limite)

    if not ofertas:
        log_info("📭 info: Nenhuma oferta nova para converter no banco.")
        print("📭 info: Nenhuma oferta nova para converter no banco.")
        return False  # Retorna False para avisar o orquestrador que não houve trabalho

    for id_db, link_original in ofertas:
        link_afiliado = converter_link_shopee(link_original)

        if link_afiliado:
            atualizar_link_afiliado(id_db, link_afiliado)
            print(f"✅ Oferta {id_db} convertida com sucesso.")
            log_info(f"✅ Oferta {id_db} convertida com sucesso. \n" + "-" * 80)
        else:
            print(f"❌ Falha ao converter oferta {id_db}.")
            log_erro(f"❌ Falha ao converter oferta {id_db}.❌")
    return True