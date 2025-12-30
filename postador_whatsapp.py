from playwright.sync_api import sync_playwright
import os
import time
from database import buscar_proxima_oferta_para_postar, marcar_como_postada

NOME_DO_GRUPO = "Meu Numero"

# --- A FUNÇÃO PRECISA ESTAR AQUI ---
def calcular_desconto(de, por):
    try:
        # Limpa as strings de preço para converter em número
        v_de = float(de.replace('R$', '').replace('.', '').replace(',', '.').strip())
        v_por = float(por.replace('R$', '').replace('.', '').replace(',', '.').strip())
        desconto = ((v_de - v_por) / v_de) * 100
        return int(desconto)
    except:
        return None

def postar_no_whatsapp():
    oferta = buscar_proxima_oferta_para_postar()

    if not oferta:
        print("📭 Nenhuma oferta pronta para postar.")
        return False

    id_db, nome, preco_atual, preco_antigo, link = oferta

    porcentagem = calcular_desconto(preco_antigo, preco_atual)
    tag_topo = f"🔥 {porcentagem}% DE DESCONTO!" if porcentagem else "🔥 OFERTA RELÂMPAGO!"
    # Limpa o final do nome se ele tiver a porcentagem da Shopee
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

    # Usamos o 'with' para garantir o fechamento do Playwright
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(user_data_dir, headless=False)
        page = browser.new_page()

        try:
            page.goto("https://web.whatsapp.com")
            print("⏳ Aguardando WhatsApp...")
            page.wait_for_selector('div[contenteditable="true"][data-tab="3"]', timeout=60000)

            # Busca e seleciona o grupo/contato
            page.fill('div[contenteditable="true"][data-tab="3"]', NOME_DO_GRUPO)
            time.sleep(2)
            page.keyboard.press("Enter")
            time.sleep(2)

            # Escreve e envia
            campo_texto = page.locator('footer div[contenteditable="true"][data-tab="10"]')
            campo_texto.fill(mensagem)
            time.sleep(1)
            page.keyboard.press("Enter")
            time.sleep(2)  # Espera o envio processar

            marcar_como_postada(id_db)
            print(f"✅ Postado com sucesso: {nome[:20]}")
            return True

        except Exception as e:
            print(f"❌ Erro ao postar: {e}")
            return False
        finally:
            browser.close()