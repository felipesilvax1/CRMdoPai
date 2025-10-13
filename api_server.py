# -*- coding: utf-8 -*-
"""
API Flask para processar consultas em linguagem natural ao banco PostgreSQL
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import ollama

# Cria a aplicação Flask
app = Flask(__name__)
CORS(app)

# Configuração do banco PostgreSQL (Supabase)
DB_CONFIG = {
    'host': 'localhost',
    'port': '54322',
    'database': 'postgres',
    'user': 'postgres',
    'password': 'postgres'
}

def get_db_connection():
    """Cria uma conexão com o banco PostgreSQL"""
    return psycopg2.connect(**DB_CONFIG)

def gerar_sql_com_ia(pergunta: str) -> str:
    """
    Usa o modelo Ollama para gerar SQL a partir da pergunta
    """
    prompt = f"""Você é um especialista em SQL PostgreSQL trabalhando com banco de dados da Receita Federal brasileira.

Tabelas disponíveis:
- empresas: "cnpj basico", "razao social", "natureza juridica", "qualificacao responsavel", "capital social", "porte empresa", "ente federativo responsavel"
- estabelecimentos: "cnpj basico", cnpj_ordem, cnpj_dv, "identificador matriz filial", "nome fantasia", "situacao cadastral", "data situacao cadastral", municipio, bairro, logradouro, numero, complemento, cep, uf, cnae_fiscal_principal, cnae_fiscal_secundaria
- socios: "cnpj basico", "identificador de socio", "nome socio razao social", "cnpj cpf do socio", "qualificacao socio", "data entrada sociedade"
- cnaes: codigo, descricao

REGRAS IMPORTANTES:
1. Campos com espaços devem usar aspas duplas: "cnpj basico", "razao social"
2. Para CNPJ completo: CONCAT("cnpj basico", cnpj_ordem, cnpj_dv)
3. Use ILIKE para buscas case-insensitive: WHERE campo ILIKE '%termo%'
4. Para juntar tabelas use: "cnpj basico"
5. Limite sempre a 50 resultados com LIMIT 50
6. Retorne APENAS o SQL, sem explicações

Pergunta: {pergunta}

SQL:"""
    
    try:
        response = ollama.generate(model='llama3:8b', prompt=prompt)
        sql = response['response'].strip()
        # Remove markdown se houver
        sql = sql.replace('```sql', '').replace('```', '').strip()
        return sql
    except Exception as e:
        print(f"Erro ao gerar SQL com IA: {e}")
        # Fallback para query simples
        return f"SELECT * FROM empresas WHERE \"razao social\" ILIKE '%{pergunta}%' LIMIT 10;"

def executar_query(sql: str):
    """Executa a query SQL e retorna os resultados"""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(sql)
            resultados = cursor.fetchall()
            return [dict(row) for row in resultados]
    finally:
        conn.close()

def gerar_resposta_texto(pergunta: str, resultados: list, sql: str) -> str:
    """Gera uma resposta em linguagem natural"""
    if not resultados:
        return "Não encontrei resultados para sua pergunta."
    
    total = len(resultados)
    preview = str(resultados[:3])
    
    prompt = f"""Com base nos resultados da consulta ao banco de dados, responda em português de forma clara e objetiva.

Pergunta: {pergunta}
Total de resultados: {total}
Amostra dos dados: {preview}

Responda de forma natural e resumida:"""
    
    try:
        response = ollama.generate(model='llama3:8b', prompt=prompt)
        return response['response'].strip()
    except:
        return f"Encontrei {total} resultado(s) para sua consulta."

@app.route('/query', methods=['POST'])
def handle_query():
    """Endpoint principal que recebe a pergunta e retorna os resultados"""
    try:
        data = request.get_json()
        pergunta = data.get('question')
        
        if not pergunta:
            return jsonify({"erro": "Nenhuma pergunta foi fornecida."}), 400
        
        print(f"\n📥 Pergunta recebida: '{pergunta}'")
        
        # 1. Gerar SQL com IA
        print("🤖 Gerando SQL com IA...")
        sql = gerar_sql_com_ia(pergunta)
        print(f"📝 SQL gerado: {sql}")
        
        # 2. Executar query
        print("⚡ Executando query no PostgreSQL...")
        resultados = executar_query(sql)
        print(f"✅ {len(resultados)} resultados encontrados")
        
        # 3. Gerar resposta em texto
        print("💬 Gerando resposta em linguagem natural...")
        resposta_texto = gerar_resposta_texto(pergunta, resultados, sql)
        
        return jsonify({
            "resposta_texto": resposta_texto,
            "sql_gerado": sql,
            "total_resultados": len(resultados),
            "dados_completos": resultados
        })
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return jsonify({
            "erro": f"Erro ao processar consulta: {str(e)}"
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar se a API está funcionando"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
        conn.close()
        return jsonify({
            "status": "ok",
            "database": "connected",
            "message": "API e banco de dados funcionando!"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "database": "disconnected",
            "error": str(e)
        }), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Servidor Flask API iniciando...")
    print("=" * 60)
    print(f"📍 URL: http://localhost:5000")
    print(f"🗄️  PostgreSQL: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    print(f"🤖 Modelo IA: Ollama Llama3:8b")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)

