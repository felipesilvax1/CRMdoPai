import re
import requests
from flask import Flask, render_template, request

app = Flask(__name__)

BRASIL_API_BASE_URL = "https://brasilapi.com.br/api/cnpj/v1"

@app.route('/', methods=['GET', 'POST'])
def index():
    dados = None
    erro = None

    if request.method == 'POST':
        cnpj = request.form.get('cnpj')

        # 1. Sanitização: Remover caracteres não numéricos
        cnpj_limpo = re.sub(r'[^0-9]', '', cnpj)

        # 2. Validação: Verificar se o CNPJ tem 14 dígitos
        if len(cnpj_limpo) != 14:
            erro = "CNPJ inválido. Por favor, digite um CNPJ com 14 dígitos."
            return render_template('index.html', erro=erro)

        try:
            # 3. Chamada à API
            response = requests.get(f"{BRASIL_API_BASE_URL}/{cnpj_limpo}")

            # 4. Tratamento de Resposta
            if response.status_code == 200:
                dados = response.json()
            elif response.status_code == 404:
                erro = "CNPJ não encontrado na base de dados da BrasilAPI."
            else:
                erro = f"Não foi possível realizar a consulta. A API retornou o status {response.status_code}. Tente novamente mais tarde."

        except requests.exceptions.RequestException:
            erro = "Erro de conexão. Não foi possível se conectar à API. Verifique sua conexão com a internet."

    return render_template('index.html', dados=dados, erro=erro)

if __name__ == '__main__':
    app.run(debug=True)
