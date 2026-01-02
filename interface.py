import customtkinter as ctk
import threading
import time
import sys
import os
from database import iniciar_db, limpar_banco_de_dados
from orquestrador import iniciar_sistema_automatico


class AppBot(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configurações da Janela
        self.title("Gerenciador de Ofertas PRO")
        self.geometry("700x600")

        # Variáveis de Estado
        self.bot_ativo = False
        self.thread_bot = None

        # --- UI (Interface) ---
        self.label_titulo = ctk.CTkLabel(self, text="PAINEL DE CONTROLE", font=("Roboto", 22, "bold"))
        self.label_titulo.pack(pady=15)

        self.label_status = ctk.CTkLabel(self, text="Status: Aguardando Comando", text_color="gray",
                                         font=("Roboto", 14))
        self.label_status.pack(pady=5)

        # Container para os botões (Organiza um ao lado do outro ou em sequência)
        self.frame_botoes = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_botoes.pack(pady=10)

        # Botão Principal (Ligar/Desligar)
        self.btn_toggle = ctk.CTkButton(self.frame_botoes, text="LIGAR SISTEMA", command=self.controlar_bot,
                                        fg_color="green", hover_color="darkgreen", font=("Roboto", 14, "bold"),
                                        width=200, height=40)
        self.btn_toggle.grid(row=0, column=0, padx=10)

        # Botão de Limpeza Manual
        self.btn_limpar = ctk.CTkButton(self.frame_botoes, text="LIMPAR BANCO (2 DIAS)",
                                        command=self.executar_limpeza_manual,
                                        fg_color="#3d3d3d", hover_color="#575757", font=("Roboto", 14), width=200,
                                        height=40)
        self.btn_limpar.grid(row=0, column=1, padx=10)

        # Console de Logs
        self.txt_console = ctk.CTkTextbox(self, width=650, height=350, font=("Consolas", 12))
        self.txt_console.pack(pady=20, padx=20)

        # Rodapé
        self.label_footer = ctk.CTkLabel(self, text="Pronto para iniciar.", font=("Roboto", 10))
        self.label_footer.pack(side="bottom", pady=5)

        # Protocolo para fechar o .exe totalmente
        self.protocol("WM_DELETE_WINDOW", self.fechar_programa)

        # Protocolo para fechar o .exe totalmente
        self.protocol("WM_DELETE_WINDOW", self.fechar_programa)

    def log(self, texto):
        """Escreve mensagens na caixa de texto da interface"""
        agora = time.strftime('%H:%M:%S')
        msg = f"[{agora}] {texto}\n"
        # O uso de lambda aqui garante que a UI atualize sem travar
        self.after(0, lambda: self._inserir_texto(msg))

    def _inserir_texto(self, msg):
        self.txt_console.insert("end", msg)
        self.txt_console.see("end")

    def executar_limpeza_manual(self):
        """Chama a função de limpeza e avisa no log"""
        try:
            self.log("🧹 Iniciando limpeza manual do banco de dados...")
            # A função limpar_banco_de_dados agora deve retornar o log_info que criamos antes
            limpar_banco_de_dados(dias=2)
            self.log("✅ Limpeza concluída! Registros com mais de 2 dias foram removidos.")
        except Exception as e:
            self.log(f"⚠️ Erro ao limpar banco: {e}")

    def controlar_bot(self):
        """Gerencia o início e a parada do bot"""
        if not self.bot_ativo:
            # AÇÃO: LIGAR
            self.bot_ativo = True
            self.btn_toggle.configure(text="DESLIGAR SISTEMA", fg_color="red", hover_color="#8B0000", state="normal")
            self.label_status.configure(text="Status: RODANDO", text_color="#00FF00")
            self.log("🚀 Orquestrador iniciado!")

            self.thread_bot = threading.Thread(target=self.loop_trabalho, daemon=True)
            self.thread_bot.start()
        else:
            # AÇÃO: DESLIGAR
            self.bot_ativo = False
            # Desabilitamos o botão temporariamente para evitar cliques múltiplos enquanto ele fecha o Playwright
            self.btn_toggle.configure(text="PARANDO...", state="disabled", fg_color="orange")
            self.log("🛑 Parada solicitada. Fechando processos com segurança...")

    def loop_trabalho(self):
        """Loop que chama o orquestrador"""
        while self.bot_ativo:
            try:
                # Chama o ciclo único do orquestrador
                iniciar_sistema_automatico(callback_log=self.log, checar_parada=lambda: self.bot_ativo)

                if not self.bot_ativo: break

                self.log("💤 Ciclo finalizado. Aguardando 60s...")
                for _ in range(60):
                    if not self.bot_ativo: break
                    time.sleep(1)

            except Exception as e:
                if "closed" not in str(e).lower():
                    self.log(f"❌ ERRO NO CICLO: {e}")
                time.sleep(5)

        # --- ESSA É A PARTE NOVA ---
        # Quando o loop 'while' quebra (bot_ativo virou False), resetamos a UI
        self.resetar_ui_pos_parada()

    def resetar_ui_pos_parada(self):
        """Retorna os botões ao estado original após o encerramento seguro"""
        self.after(0, lambda: self.btn_toggle.configure(
            text="LIGAR SISTEMA",
            state="normal",
            fg_color="green",
            hover_color="darkgreen"
        ))
        self.after(0, lambda: self.label_status.configure(text="Status: PARADO", text_color="gray"))
        self.log("✅ Sistema totalmente parado e pronto para reiniciar.")

    def fechar_programa(self):
        """Fecha a janela de forma segura"""
        self.bot_ativo = False
        self.log("Encerrando processos...")
        # Dá 2 segundos para o orquestrador perceber o self.bot_ativo = False e fechar o browser
        self.after(2000, self.safe_destroy)

    def safe_destroy(self):
        self.destroy()
        os._exit(0)

if __name__ == "__main__":
    iniciar_db()
    app = AppBot()
    app.mainloop()