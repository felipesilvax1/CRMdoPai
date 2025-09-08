import re
import requests
from flask import Flask, render_template, request

app = Flask(__name__)

# URLs das APIs
BRASIL_API_URL = "https://brasilapi.com.br/api/cnpj/v1"
CNPJ_WS_API_URL = "https://cnpj.ws/api/v1/cnpj/search"

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
    resultados_busca = None
    search_term = None

    # Lógica para quando um CNPJ é selecionado da lista de resultados (via GET)
    if request.method == 'GET' and 'cnpj_selecionado' in request.args:
        cnpj_selecionado = request.args.get('cnpj_selecionado')
        dados, erro = get_cnpj_details(cnpj_selecionado)

    if request.method == 'POST':
        # Lógica para busca direta por CNPJ
        if 'cnpj' in request.form:
            cnpj_input = request.form.get('cnpj')
            if cnpj_input:
                dados, erro = get_cnpj_details(cnpj_input)

        # Lógica para busca por nome da empresa
        elif 'nome' in request.form:
            nome_input = request.form.get('nome')
            search_term = nome_input # Para manter o termo na caixa de busca
            if not nome_input or len(nome_input) < 3:
                erro = "Por favor, digite pelo menos 3 caracteres para a busca por nome."
            else:
                try:
                    params = {'q': nome_input}
                    response = requests.get(CNPJ_WS_API_URL, params=params)

                    if response.status_code == 200:
                        json_response = response.json()
                        # A API do CNPJ.ws pode não ter uma chave 'results' e retornar a lista direto
                        # Vamos verificar a estrutura comum
                        if 'data' in json_response and isinstance(json_response['data'], list):
                             resultados_busca = json_response['data']
                        elif isinstance(json_response, list): # Caso a raiz seja a lista
                             resultados_busca = json_response
                        else:
                             resultados_busca = []

                        if not resultados_busca:
                            erro = f"Nenhuma empresa encontrada com o termo '{nome_input}'."
                    else:
                        erro = f"Erro na busca por nome: Status {response.status_code}"

                except requests.exceptions.RequestException:
                    erro = "Erro de conexão ao realizar a busca por nome."

    return render_template('index.html',
                           dados=dados,
                           erro=erro,
                           resultados_busca=resultados_busca,
                           search_term=search_term)

if __name__ == '__main__':
    app.run(debug=True)
