import time
import random
from Playright_bot_search import buscar_promos_perfil_real
from conversor import executar_conversao_em_lote
from postador_whatsapp import postar_no_whatsapp
from database import iniciar_db, buscar_proxima_oferta_para_postar
from logs import log_info
from datetime import datetime


def iniciar_sistema_automatico(callback_log=None, checar_parada=None, usuario="padrao", termo_pesquisa="",
                               nome_grupo=""):
    def avisar(texto):
        if callback_log: callback_log(texto)
        log_info(texto)

    if checar_parada and not checar_parada(): return

    avisar(f"🤖 Perfil: {usuario.upper()} | Grupo: {nome_grupo}")
    iniciar_db(usuario=usuario)

    # 1. Busca
    tem_no_estoque = buscar_proxima_oferta_para_postar(termo=termo_pesquisa, usuario=usuario)
    if not tem_no_estoque:
        avisar(f"🔍 Buscando novas ofertas para {termo_pesquisa}...")
        buscar_promos_perfil_real(usuario=usuario, termo=termo_pesquisa)

    # 2. Conversão
    executar_conversao_em_lote(limite=10, callback_log=callback_log, checar_parada=checar_parada, usuario=usuario,
                               termo_pesquisa=termo_pesquisa)

    # 3. Postagem
    for i in range(5):
        if checar_parada and not checar_parada(): break
        sucesso = postar_no_whatsapp(callback_log=callback_log, checar_parada=checar_parada, usuario=usuario,
                                     termo_pesquisa=termo_pesquisa, nome_grupo=nome_grupo)

        if sucesso and i < 4:
            tempo = random.randint(900, 1500)
            avisar(f"⏳ Pausa de segurança: {tempo // 60} min...")
            for _ in range(tempo):
                if checar_parada and not checar_parada(): break
                time.sleep(1)
        elif not sucesso:
            break


def ciclo_misto_aleatorio(callback_log=None, checar_parada=None, usuario="padrao", nome_grupo=""):
    if callback_log: callback_log(f"🎲 Modo Aleatório iniciado para o grupo: {nome_grupo}")

    # Converte qualquer item pendente
    executar_conversao_em_lote(limite=5, callback_log=callback_log, checar_parada=checar_parada, usuario=usuario,
                               termo_pesquisa="")

    # Posta de forma aleatória
    sucesso = postar_no_whatsapp(
        callback_log=callback_log,
        checar_parada=checar_parada,
        usuario=usuario,
        modo_aleatorio=True,
        nome_grupo=nome_grupo
    )
    return sucesso