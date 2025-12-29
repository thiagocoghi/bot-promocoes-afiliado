import requests
import time
import hashlib

# Configurações da API Shopee (Você pega no painel de afiliado)
APP_ID = "SEU_APP_ID_AQUI"
APP_SECRET = "SEU_APP_SECRET_AQUI"


def gerar_link_afiliado(url_produto):
    # Essa função enviará o link do produto para a Shopee
    # e ela devolverá o seu link de afiliado pronto.

    endpoint = "https://open-api.affiliate.shopee.com.br/v2/api/graphql"

    # A Shopee exige uma assinatura (hash) para segurança
    timestamp = int(time.time())
    payload = f'{APP_ID}{timestamp}{APP_SECRET}'
    signature = hashlib.sha256(payload.encode()).hexdigest()

    query = """
    mutation {
        generateShortLink(input: { originUrl: "%s" }) {
            shortLink
        }
    }
    """ % url_produto

    headers = {
        "Authorization": f"SHA256 {signature}",
        "Timestamp": str(timestamp),
        "AppID": APP_ID,
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(endpoint, json={'query': query}, headers=headers)
        dados = response.json()
        return dados['data']['generateShortLink']['shortLink']
    except Exception as e:
        return f"Erro ao gerar link: {e}"


# Exemplo de teste
link_original = "https://shopee.com.br/produto-exemplo"
# print(gerar_link_afiliado(link_original))