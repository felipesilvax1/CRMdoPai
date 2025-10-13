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

@app.route('/filtros/ufs', methods=['GET'])
def get_ufs():
    """Retorna lista de UFs disponíveis"""
    try:
        sql = "SELECT DISTINCT uf, COUNT(*) as total FROM estabelecimentos WHERE uf IS NOT NULL GROUP BY uf ORDER BY uf"
        result = executar_sql(sql)
        return jsonify({"ufs": result})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/filtros/municipios', methods=['GET'])
def get_municipios():
    """Retorna lista de municípios (códigos IBGE)"""
    try:
        uf = request.args.get('uf', '')
        
        if uf:
            # Municípios de uma UF específica (sem JOIN - tabela municipios vazia)
            sql = f"""
                SELECT DISTINCT 
                    municipio as codigo,
                    municipio as descricao,
                    COUNT(*) as total
                FROM estabelecimentos 
                WHERE uf = '{uf}' AND municipio IS NOT NULL AND municipio != ''
                GROUP BY municipio
                ORDER BY total DESC
                LIMIT 100
            """
        else:
            # Top municípios do Brasil (sem UF)
            sql = """
                SELECT DISTINCT 
                    municipio as codigo,
                    municipio as descricao,
                    COUNT(*) as total
                FROM estabelecimentos 
                WHERE municipio IS NOT NULL AND municipio != ''
                GROUP BY municipio
                ORDER BY total DESC
                LIMIT 100
            """
        
        result = executar_sql(sql)
        return jsonify({
            "municipios": result,
            "nota": "Códigos IBGE - Tabela de nomes em migração"
        })
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/filtros/cnaes', methods=['GET'])
def get_cnaes():
    """Retorna CNAEs mais comuns"""
    try:
        sql = """
            SELECT cnae_fiscal_principal as codigo, COUNT(*) as total 
            FROM estabelecimentos 
            WHERE cnae_fiscal_principal IS NOT NULL 
            GROUP BY cnae_fiscal_principal 
            ORDER BY total DESC 
            LIMIT 100
        """
        result = executar_sql(sql)
        return jsonify({"cnaes": result})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/query/filtrado', methods=['POST'])
def query_filtrado():
    """Executa query com filtros (sem LLM)"""
    try:
        data = request.get_json()
        
        # Filtros opcionais
        uf = data.get('uf')
        municipio_codigo = data.get('municipio')
        situacao = data.get('situacao', '02')  # Padrão: ativas
        cnae = data.get('cnae')
        limit = min(int(data.get('limit', 50)), 1000)  # Máx 1000
        
        # Construir WHERE
        conditions = []
        if uf:
            conditions.append(f"uf = '{uf}'")
        if municipio_codigo:
            conditions.append(f"municipio = '{municipio_codigo}'")
        if situacao:
            conditions.append(f"situacao_cadastral = '{situacao}'")
        if cnae:
            conditions.append(f"cnae_fiscal_principal = '{cnae}'")
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        # Query
        sql = f"""
            SELECT 
                cnpj_basico,
                cnpj_ordem,
                cnpj_dv,
                nome_fantasia,
                situacao_cadastral,
                uf,
                municipio,
                cnae_fiscal_principal,
                logradouro,
                bairro,
                correio_eletronico
            FROM estabelecimentos
            WHERE {where_clause}
            LIMIT {limit}
        """
        
        # Também pegar contagem total
        count_sql = f"SELECT COUNT(*) as total FROM estabelecimentos WHERE {where_clause}"
        
        resultados = executar_sql(sql)
        total = executar_sql(count_sql)[0]['total']
        
        return jsonify({
            "dados": resultados,
            "total_encontrado": total,
            "total_retornado": len(resultados),
            "sql_executado": sql,
            "filtros_aplicados": {
                "uf": uf,
                "municipio": municipio_codigo,
                "situacao": situacao,
                "cnae": cnae
            }
        })
        
    except Exception as e:
        print(f"[ERRO] {str(e)}")
        return jsonify({"erro": str(e)}), 500

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
