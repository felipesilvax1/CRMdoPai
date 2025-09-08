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

def _scrape_and_validate(url):
    """
    Raspa uma URL em busca de CNPJs e valida o primeiro encontrado na BrasilAPI.
    Retorna o primeiro CNPJ válido encontrado ou None.
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        cnpj_pattern = re.compile(r'\d{2}\.?\d{3}\.?\d{3}\/?\d{4}-?\d{2}')
        text_content = soup.get_text()

        potential_cnpjs = cnpj_pattern.findall(text_content)
        cleaned_cnpjs = {re.sub(r'[^0-9]', '', cnpj) for cnpj in potential_cnpjs}

        for cnpj in cleaned_cnpjs:
            if len(cnpj) == 14:
                dados, _ = get_cnpj_details(cnpj)
                if dados:
                    return cnpj
        return None
    except requests.exceptions.RequestException as e:
        print(f"Erro durante o scraping na URL {url}: {e}")
        return None

def _find_official_site_url(nome_empresa):
    """
    Busca no Google pelo site oficial de uma empresa.
    Retorna a URL do primeiro resultado de busca.
    """
    try:
        query = f'site oficial "{quote_plus(nome_empresa)}"'
        url = f"https://www.google.com/search?q={query}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Encontra o link dentro do primeiro resultado de busca do Google
        # A estrutura pode mudar, mas 'div.g' e 'a' são seletores comuns.
        first_result = soup.find('div', class_='g')
        if first_result:
            link_tag = first_result.find('a')
            if link_tag and link_tag.has_attr('href'):
                return link_tag['href']

        return None
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar site oficial no Google: {e}")
        return None

def encontrar_cnpj(nome_empresa, localizacao=None):
    """
    Orquestra a busca em cascata por um CNPJ, tentando várias estratégias.
    Retorna um CNPJ válido ou None.
    """
    # Estratégia 1: Busca Direta no Google
    print("Tentando Estratégia 1: Busca Direta no Google...")
    query1 = f'"{quote_plus(nome_empresa)}" CNPJ'
    url1 = f"https://www.google.com/search?q={query1}"
    cnpj_encontrado = _scrape_and_validate(url1)
    if cnpj_encontrado:
        print("Estratégia 1 bem-sucedida.")
        return cnpj_encontrado

    # Estratégia 2: Busca Geolocalizada no Google
    if localizacao:
        print("Tentando Estratégia 2: Busca Geolocalizada...")
        query2 = f'"{quote_plus(nome_empresa)}" "{quote_plus(localizacao)}" CNPJ'
        url2 = f"https://www.google.com/search?q={query2}"
        cnpj_encontrado = _scrape_and_validate(url2)
        if cnpj_encontrado:
            print("Estratégia 2 bem-sucedida.")
            return cnpj_encontrado

    # Estratégia 3: Caça ao Site Oficial
    print("Tentando Estratégia 3: Caça ao Site Oficial...")
    site_url = _find_official_site_url(nome_empresa)
    if site_url:
        print(f"Site oficial encontrado: {site_url}. Verificando CNPJ no site...")
        cnpj_encontrado = _scrape_and_validate(site_url)
        if cnpj_encontrado:
            print("Estratégia 3 bem-sucedida.")
            return cnpj_encontrado

    print("Nenhuma estratégia foi bem-sucedida.")
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
    query_nome = None
    query_localizacao = None

    if request.method == 'POST':
        query_nome = request.form.get('nome')
        query_localizacao = request.form.get('localizacao')

        if not query_nome:
            erro = "Por favor, digite um CNPJ ou nome de empresa."
        else:
            # Limpa a query para ver se é um CNPJ
            cleaned_query = re.sub(r'[^0-9]', '', query_nome)

            # Se a query limpa for apenas dígitos e tiver 14 caracteres, trata como CNPJ
            if cleaned_query.isdigit() and len(cleaned_query) == 14:
                dados, erro = get_cnpj_details(cleaned_query)
            # Senão, trata como nome de empresa e usa o detetive
            else:
                cnpj_encontrado = encontrar_cnpj(query_nome, query_localizacao)
                if cnpj_encontrado:
                    dados, erro = get_cnpj_details(cnpj_encontrado)
                    if dados and not erro:
                        dados['nota_busca'] = f"CNPJ encontrado por busca para o termo: '{query_nome}'"
                else:
                    erro = f"Não foi possível encontrar um CNPJ para '{query_nome}'. Tente ser mais específico ou adicionar uma localização."

    return render_template('index.html', dados=dados, erro=erro, query_nome=query_nome, query_localizacao=query_localizacao)

if __name__ == '__main__':
    app.run(debug=True)
