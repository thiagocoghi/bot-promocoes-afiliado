# 🛒 Bot de Promoções Automático (Marketplace Affiliates)

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Playwright](https://img.shields.io/badge/playwright-2EAD33?style=for-the-badge&logo=playwright&logoColor=white)
![Git](https://img.shields.io/badge/git-%23F05033.svg?style=for-the-badge&logo=git&logoColor=white)

Este projeto é uma ferramenta de automação ponta a ponta que identifica ofertas reais, gera links de afiliado e prepara o compartilhamento automático para redes sociais e grupos de mensagens.

---

## 📋 Sumário
* [Fluxo de Funcionamento](#-fluxo-de-funcionamento)
* [Tecnologias](#-tecnologias)
* [Estrutura do Projeto](#-estrutura-do-projeto)
* [Configuração e Instalação](#-configuração-e-instalação)
* [Roadmap](#-roadmap)

---

## 🔄 Fluxo de Funcionamento

O bot opera em um ciclo de quatro etapas principais:

1.  **Busca (Scraping):** Varre páginas de ofertas (ex: Shopee Flash Sale) usando técnicas de evasão de bot.
2.  **Conversão:** Utiliza cookies de sessão para acessar o painel de afiliado e gerar o link personalizado.
3.  **Filtragem:** Verifica em um banco local se a oferta já foi enviada anteriormente.
4.  **Disparo:** Formata a mensagem e envia para grupos de WhatsApp.

---

## 🛠 Tecnologias

| Ferramenta | Função |
| :--- | :--- |
| **Playwright** | Automação de navegador e extração de dados. |
| **Playwright Stealth** | Camuflagem contra sistemas antibot (Cloudflare/Akamai). |
| **Python** | Linguagem principal e lógica de processamento. |
| **Storage State** | Gestão de sessões e cookies para evitar logins repetitivos. |

---

## 📂 Estrutura do Projeto

```bash
bot-promocoes-afiliado/
├── .venv/               # Ambiente virtual isolado
├── auth.json            # 🔑 Cookies de sessão (NÃO SUBIR PRO GIT)
├── gerar_sessao.py      # Script de login manual inicial
├── main_search.py       # Script principal de captura (Stealth)
├── conversor.py         # Módulo de transformação de links
├── requirements.txt     # Dependências do projeto
└── README.md            # Documentação
```
---
## 🚀 Configuração e Instalação
### 1. Clonar e Preparar

```Bash
git clone [https://github.com/seu-usuario/bot-promocoes-afiliado.git](https://github.com/seu-usuario/bot-promocoes-afiliado.git)
cd bot-promocoes-afiliado
python -m venv .venv
.\.venv\Scripts\activate
```

### 2. Instalar Dependências

```Bash
pip install -r requirements.txt
playwright install chromium
```

### 3. Autenticar (Primeira vez)

```Bash
python gerar_sessao.py
Faça o login no painel de afiliado e pressione Enter no terminal.
```
---

## 🗺 Roadmap de Desenvolvimento
* [x] Fase 1: Scraping de ofertas (Shopee) com bypass de antibot.

* [x] Fase 2: Persistência de sessão (Login manual -> Cookies).

* [ ] Fase 3: Conversor automático de links no painel de afiliado.

* [x] Fase 4: Banco de dados simples para evitar duplicatas.

* [ ] Fase 5: Integração com API de WhatsApp/Telegram.

* [ ] Fase 6: Suporte para Amazon e outros marketplaces.

## 🛡 Segurança
### **Aviso: Nunca compartilhe seu arquivo auth.json. Ele contém tokens de acesso que permitem entrada direta na sua conta de afiliado. Certifique-se de que ele está listado no seu .gitignore.**

Desenvolvido por Thiagocoghi