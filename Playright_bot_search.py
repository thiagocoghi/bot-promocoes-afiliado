from playwright.sync_api import sync_playwright
import os
import time
from database import iniciar_db, salvar_oferta
from logs import log_info, log_erro


def buscar_promos_perfil_real(usuario="padrao", termo=""):
    # 1. Inicializa o Banco de Dados
    iniciar_db(usuario=usuario)

    # AJUSTE: O diretório agora é dinâmico com base no usuário da interface
    user_data_dir = os.path.join(os.getcwd(), f"perfil_{usuario}")
    novas_ofertas = 0

    with sync_playwright() as p:
        print(f"🚀 Abrindo navegador para o perfil: {usuario}...")
        context = p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
            viewport={'width': 1280, 'height': 720}
        )

        page = context.new_page()

        try:
            # LÓGICA DE PESQUISA DINÂMICA
            if not termo or termo.strip() == "":
                print("🔗 Acessando Ofertas Relâmpago...")
                url_alvo = "https://shopee.com.br/flash_sale"
            else:
                print(f"🔍 Pesquisando produtos para: {termo}...")
                url_alvo = f"https://shopee.com.br/search?keyword={termo}"

            page.goto(url_alvo, wait_until="load", timeout=90000)
            time.sleep(8)

            print("🖱️ Rolando para carregar produtos...")
            for i in range(5):
                page.mouse.wheel(0, 800)
                time.sleep(1.5)

            print("🔍 Analisando elementos da página...")
            # Localizador flexível para links de produtos
            produtos_encontrados = page.locator('a[href*="-i."]').all()

            if len(produtos_encontrados) > 0:
                print(f"✅ Encontrei {len(produtos_encontrados)} possíveis links.")

                for i, link_element in enumerate(produtos_encontrados[:25]):
                    try:
                        link = link_element.get_attribute("href")
                        if not link: continue

                        link_completo = f"https://shopee.com.br{link}" if link.startswith("/") else link

                        # --- NOVOS SELETORES BASEADOS NO SEU HTML ---

                        # 1. Nome do Produto (Baseado na estrutura flex-col/line-clamp-2)
                        nome_el = link_element.locator('.line-clamp-2, .EAIlz5')
                        nome = nome_el.first.inner_text().strip() if nome_el.count() > 0 else "Produto sem nome"

                        # 2. Preço Atual (Baseado na classe text-base/5 font-medium)
                        # Procuramos o texto que contém o valor numérico
                        preco_atual_el = link_element.locator('.text-base\/5, .w6Dcnx .iwH3_q')
                        preco_atual = f"R$ {preco_atual_el.first.inner_text().strip()}" if preco_atual_el.count() > 0 else "Consultar"

                        # 3. Preço Antigo (Na busca nem sempre aparece, então tratamos como opcional)
                        preco_antigo_el = link_element.locator('.v0WvST, ._068777, .line-through, .qukW3P .iwH3_q')
                        preco_antigo = f"R$ {preco_antigo_el.first.inner_text().strip()}" if preco_antigo_el.count() > 0 else "---"
                        if preco_antigo_el.count() > 0:
                            preco_antigo = f"R$ {preco_antigo_el.first.inner_text().strip()}"
                        else:
                            # Se não houver preço antigo, definimos como o próprio preço atual
                            # para evitar erro de cálculo (ou mantemos --- para lógica de exibição)
                            preco_antigo = "---"
                        # Evita salvar ofertas sem preço atual válido


                        # 4. Desconto (Baseado na classe bg-shopee-pink)
                        desconto_el = link_element.locator('.bg-shopee-pink, .EKx6p6')
                        desconto = desconto_el.first.inner_text().strip() if desconto_el.count() > 0 else ""

                        if nome and preco_atual != "Consultar":
                            nome_com_desconto = f"{nome} ({desconto})" if desconto else nome

                            # Salvamento no Banco
                            foi_salvo = salvar_oferta(
                                nome=nome_com_desconto,
                                preco_atual=preco_atual,
                                preco_antigo=preco_antigo,
                                link=link_completo,
                                termo=termo,
                                usuario=usuario
                            )

                            if foi_salvo:
                                novas_ofertas += 1
                                print(f"✨ SALVO NO DB: {preco_atual} | {nome[:30]}...")
                            else:
                                print(f"⏭️ Item já cadastrado: {nome[:30]}")

                    except Exception as e:
                        print(f"⚠️ Erro ao processar produto: {e}")
                        continue

        finally:
            print(f"\n📊 Resumo: {novas_ofertas} novas ofertas salvas.")
            context.close()


if __name__ == "__main__":
    # Teste manual
    buscar_promos_perfil_real(usuario="teste", termo="teclado")