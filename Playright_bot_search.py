from playwright.sync_api import sync_playwright
import os
import time
import random
from database import iniciar_db, salvar_oferta


def buscar_promos_perfil_real():
    # 1. Inicializa o Banco de Dados
    iniciar_db()

    user_data_dir = os.path.join(os.getcwd(), "perfil_shopee")
    novas_ofertas_count = 0

    with sync_playwright() as p:
        print("🚀 Abrindo navegador...")
        context = p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
            viewport={'width': 1280, 'height': 720}
        )

        page = context.new_page()

        try:
            print("🔗 Acessando Ofertas Relâmpago...")
            page.goto("https://shopee.com.br/flash_sale", wait_until="load", timeout=90000)

            time.sleep(8)

            print("🖱️ Rolando para carregar produtos...")
            for i in range(5):
                page.mouse.wheel(0, 600)
                time.sleep(1.5)

            # Localiza os elementos
            print("🔍 Analisando elementos da página...")
            # Definimos como lista vazia por segurança antes de buscar
            produtos_encontrados = page.locator('a[href*="-i."]').all()

            if len(produtos_encontrados) > 0:
                print(f"✅ Encontrei {len(produtos_encontrados)} possíveis links.")

                for i, link_element in enumerate(produtos_encontrados[:20]):
                    try:
                        link = link_element.get_attribute("href")
                        if not link: continue

                        # Formata o link
                        link_completo = f"https://shopee.com.br{link}" if link.startswith("/") else link

                        # Captura o texto (Nome e Preço)
                        texto = link_element.inner_text().strip()

                        if texto and "\n" in texto:
                            linhas = texto.split("\n")
                            nome = linhas[0]
                            # Tenta achar o preço na estrutura do texto
                            preco = "Consultar"
                            for linha in linhas:
                                if "R$" in linha:
                                    preco = linha
                                    break

                            # TENTA SALVAR NO SQLITE
                            foi_salvo = salvar_oferta(nome, preco, link_completo)

                            if foi_salvo:
                                print(f"✨ NOVA NO BANCO: {nome} | {preco}")
                                novas_ofertas_count += 1
                            else:
                                # Se quiser logar que já existe:
                                # print(f"🔘 Já existe: {nome[:30]}...")
                                pass
                    except Exception as e:
                        continue
            else:
                print("⚠️ Nenhum produto encontrado na página.")

        except Exception as e:
            print(f"❌ Erro crítico: {e}")

        finally:
            print(f"\n📊 Resumo: {novas_ofertas_count} novas ofertas salvas em 'ofertas.db'.")
            print("Encerrando...")
            time.sleep(5)
            context.close()


if __name__ == "__main__":
    buscar_promos_perfil_real()