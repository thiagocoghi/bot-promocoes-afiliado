import os
import time
from datetime import datetime
from playwright.sync_api import sync_playwright
from database import buscar_proxima_oferta_para_postar, marcar_como_postada
from logs import log_info, log_erro

NOME_DO_GRUPO = "Ofertas para você"



def calcular_desconto(de, por):
    try:
        v_de = float(de.replace('R$', '').replace('.', '').replace(',', '.').strip())
        v_por = float(por.replace('R$', '').replace('.', '').replace(',', '.').strip())
        desconto = ((v_de - v_por) / v_de) * 100
        return int(desconto)
    except:
        return None


def postar_no_whatsapp(callback_log=None, checar_parada=None):
    # Função interna para centralizar logs na GUI e Terminal
    def avisar(texto):
        if callback_log: callback_log(texto)
        print(texto)
        log_info(texto)

    # 1. VERIFICAÇÃO INICIAL: Se mandou parar, nem busca no banco
    if checar_parada and not checar_parada():
        return False

    oferta = buscar_proxima_oferta_para_postar()

    if not oferta:
        avisar("📭 Nenhuma oferta pronta para postar.")
        return False

    id_db, nome, preco_atual, preco_antigo, link = oferta

    # Preparação da mensagem
    porcentagem = calcular_desconto(preco_antigo, preco_atual)
    tag_topo = f"🔥 {porcentagem}% DE DESCONTO!" if porcentagem else "🔥 OFERTA RELÂMPAGO!"
    nome_limpo = nome.split('(-')[0].strip()

    mensagem = (
        f"{tag_topo}\n\n"
        f"📦 *{nome_limpo}*\n\n"
        f"❌ De: ~~{preco_antigo}~~\n"
        f"✅ Por: *{preco_atual}*\n\n"
        f"🛒 *Compre aqui:* {link}\n\n"
        f"⚠️ _Preço sujeito a alteração a qualquer momento!_"
    )

    user_data_dir = os.path.join(os.getcwd(), "perfil_shopee")

    with sync_playwright() as p:
        # Lança o navegador
        browser = p.chromium.launch_persistent_context(user_data_dir, headless=False)
        page = browser.new_page()

        try:
            # 2. VERIFICAÇÃO ANTES DE ABRIR O WHATSAPP
            if checar_parada and not checar_parada():
                return False

            avisar(f"🚀 Tentando postar: {nome[:30]}...")
            page.goto("https://web.whatsapp.com")
            avisar("⏳ Aguardando carregamento do WhatsApp...")

            # Espera o campo de busca (ajustado timeout para caso o usuário demore no QR Code)
            page.wait_for_selector('div[contenteditable="true"][data-tab="3"]', timeout=60000)

            # 3. VERIFICAÇÃO ANTES DE DIGITAR O GRUPO
            if checar_parada and not checar_parada(): return False

            page.fill('div[contenteditable="true"][data-tab="3"]', NOME_DO_GRUPO)
            time.sleep(2)
            page.keyboard.press("Enter")
            time.sleep(2)

            # 4. VERIFICAÇÃO ANTES DE ENVIAR A MENSAGEM
            if checar_parada and not checar_parada():
                avisar("🛑 Postagem cancelada antes do envio.")
                return False

            campo_texto = page.locator('footer div[contenteditable="true"][data-tab="10"]')
            campo_texto.fill(mensagem)
            avisar("📸 Aguardando 10s para carregar prévia...")
            time.sleep(10)

            page.keyboard.press("Enter")
            time.sleep(5)

            marcar_como_postada(id_db)
            avisar(f"✅ Postado com sucesso: {nome[:20]}")
            return True

        except Exception as e:
            # Se o erro foi causado pelo fechamento forçado da interface
            if "closed" in str(e).lower():
                return False

            avisar(f"❌ Erro na postagem: {e}")
            if not os.path.exists("prints_erro"): os.makedirs("prints_erro")
            timestamp = datetime.now().strftime("%H-%M-%S")
            caminho_print = f"prints_erro/erro_{id_db}_{timestamp}.png"
            try:
                page.screenshot(path=caminho_print)
            except:
                pass
            return False

        finally:
            browser.close()