# -*- coding: utf-8 -*-
"""
API Flask para LangChain + Gemma (Ollama)
Integrado com PostgreSQL do CRM
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import pandas as pd
from io import BytesIO
import base64

app = Flask(__name__)
CORS(app)

# Configurações
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://host.docker.internal:11434')
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'cnpj_postgres_final'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'database': os.getenv('DB_NAME', 'cnpj_processed'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'password')
}

# Lazy imports para economizar memória
llm = None
db = None

def init_langchain():
    """Inicializa LangChain e DB apenas quando necessário"""
    global llm, db
    
    if llm is None or db is None:
        from langchain_community.utilities import SQLDatabase
        from langchain_ollama.llms import OllamaLLM
        from sqlalchemy import create_engine
        
        # Criar connection string
        conn_string = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
        
        # Inicializar DB
        db = SQLDatabase.from_uri(conn_string)
        
        # Inicializar LLM (Gemma via Ollama)
        llm = OllamaLLM(
            model="gemma:latest",
            base_url=OLLAMA_HOST,
            temperature=0
        )
        
        print("✅ LangChain + Gemma inicializado com sucesso!")
    
    return llm, db

@app.route('/health', methods=['GET'])
def health_check():
    """Verifica status do serviço"""
    try:
        # Testar conexão com Ollama
        import requests
        ollama_status = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=2).status_code == 200
    except:
        ollama_status = False
    
    return jsonify({
        "status": "ok",
        "service": "LLM Service (LangChain + Gemma)",
        "ollama_connected": ollama_status,
        "ollama_host": OLLAMA_HOST,
        "database": DB_CONFIG['database']
    })

@app.route('/ask', methods=['POST'])
def ask_question():
    """
    Endpoint principal: recebe pergunta em linguagem natural
    e retorna SQL + resposta + dados
    """
    try:
        data = request.get_json()
        pergunta = data.get('question')
        
        if not pergunta:
            return jsonify({"erro": "Nenhuma pergunta fornecida"}), 400
        
        print(f"\n{'='*60}", flush=True)
        print(f"[LLM] 📥 Pergunta recebida: {pergunta}", flush=True)
        print(f"{'='*60}", flush=True)
        
        # Inicializar LangChain
        print("[LLM] 🔄 Inicializando LangChain...", flush=True)
        llm, db = init_langchain()
        print("[LLM] ✅ LangChain inicializado", flush=True)
        
        from langchain.chains import create_sql_query_chain
        from langchain.prompts import PromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        from sqlalchemy import text as sql_text
        
        # Prompt otimizado para PostgreSQL com exemplos e códigos
        PROMPT_TEMPLATE = """Dada uma pergunta do usuário, crie uma consulta SQL para PostgreSQL sintaticamente correta.

REGRAS IMPORTANTES:
- Use APENAS nomes de colunas com underscore (ex: cnpj_basico, razao_social, nome_fantasia)
- NÃO use aspas duplas nos nomes das colunas
- Para perguntas com "QUANTOS", "QUANTO", "TOTAL" use COUNT(*)
- Para perguntas com "MOSTRE", "LISTE", "QUAIS" use SELECT * LIMIT {top_k}
- SEMPRE adicione LIMIT para evitar sobrecarga
- NÃO use WHERE uf = 'BR' (Brasil não é UF válida)
- Para "ativos" ou "ativas" use: situacao_cadastral = '02'
- Para todo o Brasil, NÃO use filtro de UF

CÓDIGOS IMPORTANTES:
- situacao_cadastral: '01'=Nula, '02'=Ativa, '03'=Suspensa, '04'=Inapta, '08'=Baixada
- UFs válidas: SP, RJ, MG, RS, PR, SC, BA, etc (NUNCA use 'BR')

EXEMPLOS:
Pergunta: "Quantos estabelecimentos temos em SP?"
SQL: SELECT COUNT(*) FROM estabelecimentos WHERE uf = 'SP';

Pergunta: "Quantos estabelecimentos ativos no Brasil?"
SQL: SELECT COUNT(*) FROM estabelecimentos WHERE situacao_cadastral = '02';

Pergunta: "Quantos ativos em SP?"
SQL: SELECT COUNT(*) FROM estabelecimentos WHERE uf = 'SP' AND situacao_cadastral = '02';

Pergunta: "Mostre empresas de SP"  
SQL: SELECT * FROM estabelecimentos WHERE uf = 'SP' LIMIT {top_k};

Pergunta: "Liste os CNAEs mais comuns"
SQL: SELECT cnae_fiscal_principal, COUNT(*) as total FROM estabelecimentos GROUP BY cnae_fiscal_principal ORDER BY total DESC LIMIT {top_k};

Esquema do banco de dados:
{table_info}

Pergunta: {input}
Consulta SQL PostgreSQL (apenas o SQL, sem explicações):"""
        
        prompt = PromptTemplate(
            input_variables=["input", "table_info", "top_k"],
            template=PROMPT_TEMPLATE
        )
        
        # Gerar SQL
        print("[LLM] 🤖 Gemma está gerando SQL... (usando GPU)", flush=True)
        generate_query_chain = create_sql_query_chain(llm, db, prompt=prompt)
        sql_query = generate_query_chain.invoke({"question": pergunta})
        print("[LLM] ✅ SQL gerado!", flush=True)
        
        # Limpar markdown formatting (```sql ... ```)
        sql_query = sql_query.strip()
        if sql_query.startswith('```sql'):
            sql_query = sql_query[6:]
        if sql_query.startswith('```'):
            sql_query = sql_query[3:]
        if sql_query.endswith('```'):
            sql_query = sql_query[:-3]
        sql_query = sql_query.strip()
        
        print(f"[SQL] 📝 SQL: {sql_query[:200]}...", flush=True)
        
        # Executar SQL
        print("[DB] 🔍 Executando query no PostgreSQL...", flush=True)
        with db._engine.connect() as connection:
            df = pd.read_sql_query(sql_text(sql_query), connection)
        
        num_resultados = len(df)
        print(f"[DB] ✅ Query executada! {num_resultados} registros retornados", flush=True)
        
        # Gerar resposta em linguagem natural
        if num_resultados > 0:
            print("[LLM] 💬 Gemma está formulando resposta... (usando GPU)", flush=True)
            preview_data = df.head(5).to_string()
            
            answer_prompt = PromptTemplate.from_template(
                """Dada a seguinte pergunta, consulta SQL e resultado, responda em português de forma clara e concisa.

Pergunta: {question}
Consulta SQL: {query}
Amostra dos Resultados: {result}

Resposta em português:"""
            )
            
            rephrase_chain = answer_prompt | llm | StrOutputParser()
            
            resposta_texto = rephrase_chain.invoke({
                "question": pergunta,
                "query": sql_query,
                "result": preview_data
            })
            print("[LLM] ✅ Resposta gerada!", flush=True)
        else:
            resposta_texto = "A consulta não retornou resultados."
            print("[LLM] ⚠️ Nenhum resultado encontrado", flush=True)
        
        # Converter DataFrame para JSON
        dados_json = df.to_dict(orient='records')
        
        return jsonify({
            "sucesso": True,
            "pergunta": pergunta,
            "sql_gerado": sql_query,
            "resposta_texto": resposta_texto,
            "total_resultados": num_resultados,
            "dados": dados_json[:100],  # Limitar para não sobrecarregar
            "tem_mais_dados": num_resultados > 100
        })
        
    except Exception as e:
        print(f"[ERRO] {str(e)}")
        return jsonify({
            "sucesso": False,
            "erro": str(e)
        }), 500

@app.route('/export', methods=['POST'])
def export_data():
    """
    Exporta dados para CSV ou PDF
    """
    try:
        data = request.get_json()
        sql_query = data.get('sql')
        formato = data.get('format', 'csv')  # csv ou pdf
        
        if not sql_query:
            return jsonify({"erro": "SQL não fornecido"}), 400
        
        # Executar SQL
        llm, db = init_langchain()
        from sqlalchemy import text as sql_text
        
        with db._engine.connect() as connection:
            df = pd.read_sql_query(sql_text(sql_query), connection)
        
        if formato == 'csv':
            # Gerar CSV
            csv_buffer = BytesIO()
            df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
            csv_buffer.seek(0)
            csv_base64 = base64.b64encode(csv_buffer.read()).decode()
            
            return jsonify({
                "sucesso": True,
                "formato": "csv",
                "arquivo_base64": csv_base64,
                "total_registros": len(df)
            })
        
        elif formato == 'pdf':
            # Gerar PDF (simplificado)
            from reportlab.lib.pagesizes import landscape, letter
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
            from reportlab.lib import colors
            
            pdf_buffer = BytesIO()
            doc = SimpleDocTemplate(pdf_buffer, pagesize=landscape(letter))
            
            # Preparar dados
            dados_tabela = [df.columns.tolist()] + df.head(100).values.tolist()
            tabela = Table(dados_tabela)
            
            estilo = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ])
            tabela.setStyle(estilo)
            
            doc.build([tabela])
            pdf_buffer.seek(0)
            pdf_base64 = base64.b64encode(pdf_buffer.read()).decode()
            
            return jsonify({
                "sucesso": True,
                "formato": "pdf",
                "arquivo_base64": pdf_base64,
                "total_registros": len(df)
            })
        
        else:
            return jsonify({"erro": "Formato inválido"}), 400
            
    except Exception as e:
        print(f"[ERRO EXPORT] {str(e)}")
        return jsonify({"sucesso": False, "erro": str(e)}), 500

if __name__ == '__main__':
    import sys
    sys.stdout.flush()
    
    print("="*60, flush=True)
    print("🤖 LLM Service iniciando (LangChain + Gemma)...", flush=True)
    print(f"📊 Database: {DB_CONFIG['database']}", flush=True)
    print(f"🔗 Ollama: {OLLAMA_HOST}", flush=True)
    print(f"🎮 GPU: Detectando uso via Ollama...", flush=True)
    print("="*60, flush=True)
    
    app.run(host='0.0.0.0', port=8000, debug=False)

