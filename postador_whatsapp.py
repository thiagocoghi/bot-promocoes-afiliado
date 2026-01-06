import os
import time
from datetime import datetime
from playwright.sync_api import sync_playwright
from database import buscar_proxima_oferta_para_postar, marcar_como_postada, buscar_oferta_aleatoria_pronta
from logs import log_info, log_erro

def calcular_desconto(de, por):
    try:
        v_de = float(de.replace('R$', '').replace('.', '').replace(',', '.').strip())
        v_por = float(por.replace('R$', '').replace('.', '').replace(',', '.').strip())
        desconto = ((v_de - v_por) / v_de) * 100
        return int(desconto)
    except:
        return None

def postar_no_whatsapp(callback_log=None, checar_parada=None, usuario="padrao", termo_pesquisa="", modo_aleatorio=False, nome_grupo=""):
    def avisar(texto):
        if callback_log: callback_log(texto)
        print(texto)
        log_info(texto)

    if checar_parada and not checar_parada(): return False

    # Escolha da oferta (Normal ou Aleatória)
    if modo_aleatorio:
        oferta = buscar_oferta_aleatoria_pronta(usuario=usuario)
    else:
        oferta = buscar_proxima_oferta_para_postar(termo=termo_pesquisa, usuario=usuario)

    if not oferta:
        avisar(f"📭 Nenhuma oferta pronta disponível.")
        return False

    id_db, nome, preco_atual, preco_antigo, link = oferta
    porcentagem = calcular_desconto(preco_antigo, preco_atual)
    nome_limpo = nome.split('(-')[0].strip()

    # Formatação da mensagem
    if preco_antigo != "---" and porcentagem:
        tag_topo = f"🔥 {porcentagem}% DE DESCONTO!"
        bloco_preco = f"❌ De: ~~{preco_antigo}~~\n✅ Por: *{preco_atual}*"
    else:
        tag_topo = "🔥 OFERTA IMPERDÍVEL!"
        bloco_preco = f"💰 Preço Especial: *{preco_atual}*"

    mensagem = (
        f"{tag_topo}\n\n"
        f"📦 *{nome_limpo}*\n\n"
        f"{bloco_preco}\n\n"
        f"🛒 *Compre aqui:* {link}\n\n"
        f"⚠️ _Preço sujeito a alteração a qualquer momento!_"
    )

    user_data_dir = os.path.join(os.getcwd(), f"perfil_{usuario}")

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = browser.new_page()

        try:
            avisar(f"🚀 Acessando WhatsApp para postar no grupo: {nome_grupo}...")
            page.goto("https://web.whatsapp.com")
            page.wait_for_selector('div[contenteditable="true"][data-tab="3"]', timeout=60000)

            # Busca o grupo usando o nome vindo da interface
            page.fill('div[contenteditable="true"][data-tab="3"]', nome_grupo)
            time.sleep(2)
            page.keyboard.press("Enter")
            time.sleep(2)

            # Preenche a mensagem
            campo_texto = page.locator('footer div[contenteditable="true"][data-tab="10"]')
            campo_texto.fill(mensagem)

            avisar("📸 Aguardando prévia da imagem...")
            for _ in range(15):
                if checar_parada and not checar_parada(): return False
                time.sleep(1)

            page.keyboard.press("Enter")
            time.sleep(5)

            marcar_como_postada(id_db, usuario=usuario)
            avisar(f"✅ Sucesso: {nome[:20]}")
            return True

        except Exception as e:
            avisar(f"❌ Erro na postagem: {e}")
            return False
        finally:
            browser.close()