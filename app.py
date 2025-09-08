import re
import requests
from flask import Flask, render_template, request
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

app = Flask(__name__)

# URLs das APIs
BRASIL_API_URL = "https://brasilapi.com.br/api/cnpj/v1"
# A URL do CNPJ.ws não será mais usada, mas vou deixar comentada por enquanto.
# CNPJ_WS_API_URL = "https://cnpj.ws/api/v1/cnpj/search"

def buscar_cnpj_no_google(nome_empresa):
    """
    Busca no Google por CNPJs associados ao nome da empresa e valida-os.
    Retorna o primeiro CNPJ válido encontrado ou None.
    """
    try:
        query = f'"{quote_plus(nome_empresa)}" CNPJ'
        url = f"https://www.google.com/search?q={query}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        cnpj_pattern = re.compile(r'\d{2}\.?\d{3}\.?\d{3}\/?\d{4}-?\d{2}')
        text_content = soup.get_text()

        # Encontra todos os potenciais CNPJs na página
        potential_cnpjs = cnpj_pattern.findall(text_content)

        # Limpa e cria um conjunto de CNPJs únicos para evitar checagens repetidas
        cleaned_cnpjs = {re.sub(r'[^0-9]', '', cnpj) for cnpj in potential_cnpjs}

        # Valida cada CNPJ encontrado
        for cnpj in cleaned_cnpjs:
            if len(cnpj) == 14:
                # Usa a função existente para verificar se o CNPJ é válido na BrasilAPI
                dados, _ = get_cnpj_details(cnpj)
                if dados:
                    # Se encontrou dados válidos, retorna este CNPJ
                    return cnpj

        return None  # Retorna None se nenhum CNPJ válido for encontrado

    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar no Google: {e}")
        return None

def get_cnpj_details(cnpj):
    """Busca os detalhes de um CNPJ na BrasilAPI."""
    try:
        # Sanitiza o CNPJ para garantir que tenha apenas números
        cnpj_limpo = re.sub(r'[^0-9]', '', cnpj)
        if len(cnpj_limpo) != 14:
            return None, "CNPJ inválido. O CNPJ deve conter 14 dígitos."

        response = requests.get(f"{BRASIL_API_URL}/{cnpj_limpo}")

        if response.status_code == 200:
            return response.json(), None
        elif response.status_code == 404:
            return None, "CNPJ não encontrado na base de dados."
        else:
            return None, f"Erro na API ao buscar detalhes: Status {response.status_code}"

    except requests.exceptions.RequestException:
        return None, "Erro de conexão ao buscar detalhes do CNPJ."

@app.route('/', methods=['GET', 'POST'])
def index():
    dados = None
    erro = None
    query = None

    if request.method == 'POST':
        query = request.form.get('query')
        if not query:
            erro = "Por favor, digite um CNPJ ou nome de empresa."
        else:
            # Limpa a query para ver se é um CNPJ
            cleaned_query = re.sub(r'[^0-9]', '', query)

            # Se a query limpa for apenas dígitos, trata como CNPJ
            if cleaned_query.isdigit() and len(cleaned_query) == 14:
                dados, erro = get_cnpj_details(cleaned_query)
            # Senão, trata como nome de empresa
            else:
                cnpj_encontrado = buscar_cnpj_no_google(query)
                if cnpj_encontrado:
                    dados, erro = get_cnpj_details(cnpj_encontrado)
                    if dados and not erro:
                        # Adiciona uma nota de que o CNPJ foi encontrado via busca
                        dados['nota_busca'] = f"CNPJ encontrado por busca para o termo: '{query}'"
                else:
                    erro = f"Não foi possível encontrar um CNPJ para o nome '{query}'. Tente ser mais específico."

    return render_template('index.html', dados=dados, erro=erro, query=query)

if __name__ == '__main__':
    app.run(debug=True)
