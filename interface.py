import customtkinter as ctk
import threading
import time
import sys
import os
import random  # Certifique-se de importar o random aqui
from database import iniciar_db, limpar_banco_de_dados
from orquestrador import iniciar_sistema_automatico


class AppBot(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Gerenciador de Ofertas PRO")
        self.geometry("700x750")

        self.bot_ativo = False
        self.thread_bot = None

        # --- UI ---
        self.label_titulo = ctk.CTkLabel(self, text="PAINEL DE CONTROLE", font=("Roboto", 22, "bold"))
        self.label_titulo.pack(pady=15)

        self.frame_config = ctk.CTkFrame(self)
        self.frame_config.pack(pady=10, padx=20, fill="x")

        # Perfil
        ctk.CTkLabel(self.frame_config, text="Perfis Detectados:", font=("Roboto", 12, "bold")).grid(row=0, column=0,
                                                                                                     padx=10, pady=10,
                                                                                                     sticky="e")
        self.perfis_encontrados = self.listar_perfis()
        self.menu_perfis = ctk.CTkOptionMenu(self.frame_config, values=self.perfis_encontrados,
                                             command=self.selecionar_perfil, width=250)
        self.menu_perfis.grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkLabel(self.frame_config, text="Nome do Perfil:", font=("Roboto", 12, "bold")).grid(row=1, column=0,
                                                                                                  padx=10, pady=10,
                                                                                                  sticky="e")
        self.entry_usuario = ctk.CTkEntry(self.frame_config, placeholder_text="Novo perfil ou selecione acima",
                                          width=250)
        self.entry_usuario.grid(row=1, column=1, padx=10, pady=10)

        if self.perfis_encontrados:
            self.entry_usuario.insert(0, self.perfis_encontrados[0])

        # Pesquisa (Row 2)
        ctk.CTkLabel(self.frame_config, text="Termo de Pesquisa:", font=("Roboto", 12, "bold")).grid(row=2, column=0,
                                                                                                     padx=10, pady=10,
                                                                                                     sticky="e")
        self.entry_pesquisa = ctk.CTkEntry(self.frame_config, placeholder_text="Vazio = Ofertas Relâmpago", width=250)
        self.entry_pesquisa.grid(row=2, column=1, padx=10, pady=10)

        # Grupo Whats (Row 3)
        ctk.CTkLabel(self.frame_config, text="Grupo do Whats:", font=("Roboto", 12, "bold")).grid(row=3, column=0,
                                                                                                  padx=10, pady=10,
                                                                                                  sticky="e")
        self.entry_grupo = ctk.CTkEntry(self.frame_config, width=250)
        self.entry_grupo.insert(0, "Achadinhos da mamãe")
        self.entry_grupo.grid(row=3, column=1, padx=10, pady=10)

        # Status e Botoes
        self.label_status = ctk.CTkLabel(self, text="Status: Aguardando Comando", text_color="gray",
                                         font=("Roboto", 14))
        self.label_status.pack(pady=5)

        self.frame_botoes = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_botoes.pack(pady=10)

        self.btn_toggle = ctk.CTkButton(self.frame_botoes, text="LIGAR SISTEMA", command=self.controlar_bot,
                                        fg_color="green", width=200, height=40)
        self.btn_toggle.grid(row=0, column=0, padx=10)

        self.btn_limpar = ctk.CTkButton(self.frame_botoes, text="LIMPAR BANCO (2 DIAS)",
                                        command=self.executar_limpeza_manual, fg_color="#3d3d3d", width=200, height=40)
        self.btn_limpar.grid(row=0, column=1, padx=10)

        self.btn_aleatorio = ctk.CTkButton(self.frame_botoes, text="POSTAGEM ALEATÓRIA (MIX)",
                                           command=self.controlar_aleatorio, fg_color="#6200ea", width=200, height=40)
        self.btn_aleatorio.grid(row=1, column=0, columnspan=2, pady=10)

        self.txt_console = ctk.CTkTextbox(self, width=650, height=300, font=("Consolas", 12))
        self.txt_console.pack(pady=20, padx=20)

        self.protocol("WM_DELETE_WINDOW", self.fechar_programa)

    def controlar_aleatorio(self):
        if not self.bot_ativo:
            usuario = self.entry_usuario.get().strip()
            grupo = self.entry_grupo.get().strip()
            if not usuario or not grupo:
                self.log("⚠️ Erro: Perfil e Grupo são obrigatórios!")
                return

            self.bot_ativo = True
            self.btn_aleatorio.configure(fg_color="red", text="PARAR ALEATÓRIO")
            self.label_status.configure(text="Status: MODO ALEATÓRIO", text_color="#6200ea")

            self.thread_bot = threading.Thread(target=self.loop_aleatorio, args=(usuario, grupo), daemon=True)
            self.thread_bot.start()
        else:
            self.bot_ativo = False
            self.btn_aleatorio.configure(text="PARANDO...", state="disabled")

    def loop_aleatorio(self, usuario, grupo):
        from orquestrador import ciclo_misto_aleatorio
        while self.bot_ativo:
            try:
                ciclo_misto_aleatorio(callback_log=self.log, checar_parada=lambda: self.bot_ativo, usuario=usuario,
                                      nome_grupo=grupo)
                if not self.bot_ativo: break

                tempo = random.randint(900, 1500)
                self.log(f"⏳ Próximo sorteio em {tempo/60} min...")
                for _ in range(tempo):
                    if not self.bot_ativo: break
                    time.sleep(1)
            except Exception as e:
                self.log(f"❌ Erro no Loop Aleatório: {e}")
                time.sleep(5)

        self.after(0, self.resetar_ui_aleatorio)
        self.resetar_ui_pos_parada()

    def resetar_ui_aleatorio(self):
        self.btn_aleatorio.configure(text="POSTAGEM ALEATÓRIA (MIX)", state="normal", fg_color="#6200ea")

    def controlar_bot(self):
        if not self.bot_ativo:
            usuario = self.entry_usuario.get().strip()
            pesquisa = self.entry_pesquisa.get().strip()
            grupo = self.entry_grupo.get().strip()

            if not usuario or not grupo:
                self.log("⚠️ Erro: Perfil e Grupo são obrigatórios!")
                return

            self.bot_ativo = True
            self.btn_toggle.configure(text="DESLIGAR SISTEMA", fg_color="red")
            self.label_status.configure(text="Status: RODANDO", text_color="#00FF00")

            self.thread_bot = threading.Thread(target=self.loop_trabalho, args=(usuario, pesquisa, grupo), daemon=True)
            self.thread_bot.start()
        else:
            self.bot_ativo = False
            self.btn_toggle.configure(text="PARANDO...", state="disabled")

    def loop_trabalho(self, usuario, pesquisa, grupo):
        while self.bot_ativo:
            try:
                iniciar_sistema_automatico(callback_log=self.log, checar_parada=lambda: self.bot_ativo, usuario=usuario,
                                           termo_pesquisa=pesquisa, nome_grupo=grupo)
                if not self.bot_ativo: break
                self.log("💤 Ciclo finalizado. Aguardando intervalo...")
                for _ in range(60):
                    if not self.bot_ativo: break
                    time.sleep(1)
            except Exception as e:
                self.log(f"❌ Erro: {e}")
                time.sleep(5)
        self.resetar_ui_pos_parada()

    # --- FUNÇÕES DE SUPORTE ---
    def listar_perfis(self):
        perfis = ["padrao"]
        try:
            itens = os.listdir(os.getcwd())
            for item in itens:
                if os.path.isdir(item) and item.startswith("perfil_"):
                    nome = item.replace("perfil_", "")
                    if nome not in perfis: perfis.append(nome)
        except:
            pass
        return perfis

    def selecionar_perfil(self, escolha):
        self.entry_usuario.delete(0, "end")
        self.entry_usuario.insert(0, escolha)

    def log(self, texto):
        agora = time.strftime('%H:%M:%S')
        self.after(0, lambda: self.txt_console.insert("end", f"[{agora}] {texto}\n"))
        self.after(0, lambda: self.txt_console.see("end"))

    def executar_limpeza_manual(self):
        try:
            limpar_banco_de_dados(dias=2)
            self.log("✅ Limpeza concluída!")
        except Exception as e:
            self.log(f"⚠️ Erro: {e}")

    def resetar_ui_pos_parada(self):
        self.after(0, lambda: self.btn_toggle.configure(text="LIGAR SISTEMA", state="normal", fg_color="green"))
        self.after(0, lambda: self.label_status.configure(text="Status: PARADO", text_color="gray"))

    def fechar_programa(self):
        self.bot_ativo = False
        os._exit(0)


if __name__ == "__main__":
    iniciar_db()
    app = AppBot()
    app.mainloop()