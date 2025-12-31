from playwright.sync_api import sync_playwright
import os
import time
from database import buscar_proxima_oferta_para_postar, marcar_como_postada
from logs import log_info, log_erro


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
        log_info("📭 Fila vazia no banco de dados.")
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
            log_info(f"🚀 Tentando postar: {nome[:30]}...")
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
            log_info("📸 Aguardando 6s para carregar a prévia da imagem...")
            time.sleep(10)  # Tempo para revisar a mensagem antes de enviar
            page.keyboard.press("Enter")
            time.sleep(2)  # Espera o envio processar

            marcar_como_postada(id_db)
            log_info(f"✅ Postado com sucesso: {nome[:20]}")
            print(f"✅ Postado com sucesso: {nome[:20]}")
            return True

        except Exception as e:
            # Captura de tela em caso de erro
            print(f"❌ Erro detectado. Tirando print da tela...")
            if not os.path.exists("prints_erro"):
                os.makedirs("prints_erro")

            timestamp = datetime.now().strftime("%H-%M-%S")
            caminho_print = f"prints_erro/erro_{id_db}_{timestamp}.png"
            page.screenshot(path=caminho_print)

            log_erro(f"Falha na postagem ID {id_db}: {e}. Print salvo em: {caminho_print}")
            return False

        finally:
            browser.close()