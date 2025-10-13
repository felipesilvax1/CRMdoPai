# -*- coding: utf-8 -*-
"""
API Flask conectando DIRETAMENTE ao PostgreSQL remoto
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

USE_POSTGRES = os.getenv('USE_POSTGRES', 'false').lower() == 'true'

if USE_POSTGRES:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    
    DB_CONFIG = {
        'host': os.getenv('DB_HOST', '192.168.15.24'),
        'port': int(os.getenv('DB_PORT', '5432')),
        'database': os.getenv('DB_NAME', 'cnpj_processed'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', 'password')
    }
    
    def executar_sql(sql: str):
        conn = psycopg2.connect(**DB_CONFIG)
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(sql)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        finally:
            conn.close()
else:
    import sqlite3
    DB_PATH = os.getenv('SQLITE_DB_PATH', '/data/CNPJ_Processado.db')
    
    def executar_sql(sql: str):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

def gerar_sql_simples(pergunta: str) -> str:
    pergunta_lower = pergunta.lower()
    
    if any(p in pergunta_lower for p in ['estatistica', 'geral', 'quantas', 'total']):
        return """
        SELECT 
            (SELECT COUNT(*) FROM empresas) as total_empresas,
            (SELECT COUNT(*) FROM estabelecimentos) as total_estabelecimentos,
            (SELECT COUNT(*) FROM socios) as total_socios,
            (SELECT COUNT(*) FROM cnaes) as total_cnaes
        """
    
    if 'empresa' in pergunta_lower or 'razao' in pergunta_lower or 'estabelecimento' in pergunta_lower:
        return """
        SELECT 
            cnpj_basico,
            cnpj_ordem,
            cnpj_dv,
            nome_fantasia,
            situacao_cadastral,
            cnae_fiscal_principal,
            municipio,
            uf
        FROM estabelecimentos 
        WHERE nome_fantasia IS NOT NULL 
        AND nome_fantasia != ''
        LIMIT 50
        """
    
    return "SELECT 'Teste' as resultado"

@app.route('/health', methods=['GET'])
def health_check():
    try:
        result = executar_sql("SELECT 1 as test")
        return jsonify({
            "status": "ok",
            "database": "PostgreSQL" if USE_POSTGRES else "SQLite",
            "host": DB_CONFIG.get('host') if USE_POSTGRES else "local",
            "message": "API funcionando!"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route('/query', methods=['POST'])
def handle_query():
    try:
        data = request.get_json()
        pergunta = data.get('question')
        
        if not pergunta:
            return jsonify({"erro": "Nenhuma pergunta fornecida"}), 400
        
        print(f"[>>] Pergunta: {pergunta}")
        
        sql = gerar_sql_simples(pergunta)
        print(f"[SQL] {sql[:100]}...")
        
        resultados = executar_sql(sql)
        print(f"[OK] {len(resultados)} resultados")
        
        if len(resultados) == 1 and 'total_empresas' in resultados[0]:
            stats = resultados[0]
            resposta = f"Base de dados: {stats['total_empresas']:,} empresas, {stats['total_estabelecimentos']:,} estabelecimentos."
        else:
            resposta = f"Encontrei {len(resultados)} resultado(s)."
        
        return jsonify({
            "resposta_texto": resposta,
            "sql_gerado": sql,
            "total_resultados": len(resultados),
            "dados_completos": resultados
        })
        
    except Exception as e:
        print(f"[ERRO] {str(e)}")
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    db_type = "PostgreSQL" if USE_POSTGRES else "SQLite"
    print("="*60)
    print(f"API Flask iniciando com {db_type}...")
    if USE_POSTGRES:
        print(f"Host: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
        print(f"Database: {DB_CONFIG['database']}")
    print("="*60)
    
    app.run(host='0.0.0.0', port=5000, debug=False)
