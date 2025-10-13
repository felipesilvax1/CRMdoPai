# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify
from flask_cors import CORS
import os

# Importa a nossa lógica refatorada
from gemma_db_logic import processar_pergunta

# Cria a aplicação Flask
app = Flask(__name__)
# Habilita o CORS para permitir que o Next.js (rodando em outra porta) acesse esta API
CORS(app)

# Define o caminho para o banco de dados.
# Mude este caminho se o seu arquivo .db estiver em outro lugar.
DB_PATH = "C:/Users/PwC/Documents/CRM/CNPJ_Processado.db"

@app.route('/query', methods=['POST'])
def handle_query():
    """
    Este é o endpoint que o nosso frontend Next.js vai chamar.
    """
    # Verifica se o caminho do banco de dados é válido
    if not os.path.exists(DB_PATH):
        return jsonify({"erro": f"Caminho do banco de dados não encontrado: {DB_PATH}"}), 500

    # Pega a pergunta enviada pelo frontend
    data = request.get_json()
    pergunta_usuario = data.get('question')

    if not pergunta_usuario:
        return jsonify({"erro": "Nenhuma pergunta foi fornecida."}), 400

    print(f"\nRecebida nova pergunta da interface web: '{pergunta_usuario}'")
    
    # Chama a nossa função de lógica para processar a pergunta
    resultado = processar_pergunta(pergunta_usuario, DB_PATH)
    
    # Devolve o resultado como JSON para o frontend
    return jsonify(resultado)

if __name__ == '__main__':
    # Roda o servidor na porta 5000.
    # O Next.js geralmente roda na porta 3000.
    print("Servidor Flask iniciado em http://127.0.0.1:5000")
    print("Este servidor atua como uma ponte entre o frontend e a lógica de IA.")
    app.run(host='0.0.0.0', port=5000, debug=True)
