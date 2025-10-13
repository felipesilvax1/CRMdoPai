# -*- coding: utf-8 -*-
"""
API Flask para consultas ao banco SQLite de CNPJ
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

# Cria a aplicação Flask
app = Flask(__name__)
CORS(app)

# Caminho do banco SQLite
DB_PATH = "C:/Users/PwC/Documents/CRM/CNPJ_Processado.db"

def executar_sql(sql: str):
    """Executa SQL no SQLite e retorna os resultados"""
    try:
        if not os.path.exists(DB_PATH):
            raise Exception(f"Banco de dados não encontrado: {DB_PATH}")
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Para retornar dicionários
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        
        # Converter para lista de dicionários
        resultados = [dict(row) for row in rows]
        conn.close()
        
        return resultados
    except Exception as e:
        raise Exception(f"Erro ao executar SQL: {str(e)}")

def gerar_sql_simples(pergunta: str) -> str:
    """Gera SQL simples baseado em palavras-chave"""
    pergunta_lower = pergunta.lower()
    
    # Busca por nome de empresa
    if 'empresa' in pergunta_lower or 'razao' in pergunta_lower:
        return """SELECT "cnpj basico", "razao social", "porte empresa" 
                  FROM empresas 
                  WHERE "razao social" IS NOT NULL
                  LIMIT 20"""
    
    # Busca por município
    elif 'municipio' in pergunta_lower or 'cidade' in pergunta_lower or 'barueri' in pergunta_lower:
        palavras = pergunta.split()
        municipio = next((p.upper() for p in palavras if len(p) > 3 and p.lower() not in ['qual', 'quais', 'empresa', 'empresas', 'municipio', 'cidade', 'existem', 'onde']), 'BARUERI')
        return f"""SELECT e."razao social", est.municipio, est.uf, est.bairro
                   FROM empresas e
                   JOIN estabelecimentos est ON e."cnpj basico" = est."cnpj basico"
                   WHERE est.municipio = '{municipio}'
                   LIMIT 30"""
    
    # Busca por CNAE/atividade  
    elif 'cnae' in pergunta_lower or 'atividade' in pergunta_lower or 'logistica' in pergunta_lower or 'transporte' in pergunta_lower:
        return """SELECT e."razao social", c.descricao as atividade, est.municipio
                  FROM empresas e
                  JOIN estabelecimentos est ON e."cnpj basico" = est."cnpj basico"
                  JOIN cnaes c ON est.cnae_fiscal_principal = c.codigo
                  WHERE c.descricao LIKE '%logistica%' 
                     OR c.descricao LIKE '%transporte%'
                     OR c.descricao LIKE '%armazenagem%'
                  LIMIT 30"""
    
    # Busca por sócios
    elif 'socio' in pergunta_lower or 'sócio' in pergunta_lower or 'proprietario' in pergunta_lower:
        return """SELECT s."nome socio razao social" as socio, 
                         e."razao social" as empresa,
                         s."qualificacao socio"
                  FROM socios s
                  JOIN empresas e ON s."cnpj basico" = e."cnpj basico"
                  WHERE s."nome socio razao social" IS NOT NULL
                  LIMIT 25"""
    
    # Busca por porte
    elif 'porte' in pergunta_lower or 'grande' in pergunta_lower or 'pequena' in pergunta_lower:
        return """SELECT "cnpj basico", "razao social", "porte empresa", "capital social"
                  FROM empresas 
                  WHERE "porte empresa" IS NOT NULL
                  AND "razao social" IS NOT NULL
                  LIMIT 30"""
    
    # Query padrão - mostra estatísticas gerais
    else:
        return """SELECT 
                    (SELECT COUNT(*) FROM empresas) as total_empresas,
                    (SELECT COUNT(*) FROM estabelecimentos) as total_estabelecimentos,
                    (SELECT COUNT(*) FROM socios) as total_socios,
                    (SELECT COUNT(*) FROM cnaes) as total_cnaes"""

@app.route('/query', methods=['POST'])
def handle_query():
    """Endpoint principal que recebe a pergunta e retorna os resultados"""
    try:
        data = request.get_json()
        pergunta = data.get('question')
        
        if not pergunta:
            return jsonify({"erro": "Nenhuma pergunta foi fornecida."}), 400
        
        print(f"\n[>>] Pergunta recebida: '{pergunta}'")
        
        # Gerar SQL
        sql = gerar_sql_simples(pergunta)
        print(f"[SQL] {sql[:150]}...")
        
        # Executar query
        print("[DB] Executando query no SQLite...")
        resultados = executar_sql(sql)
        print(f"[OK] {len(resultados)} resultados encontrados")
        
        # Gerar resposta
        if len(resultados) == 0:
            resposta_texto = "Não encontrei resultados para sua consulta. Tente reformular sua pergunta."
        elif len(resultados) == 1 and 'total_empresas' in resultados[0]:
            # É uma query de estatísticas
            stats = resultados[0]
            resposta_texto = f"No banco de dados temos: {stats['total_empresas']:,} empresas, {stats['total_estabelecimentos']:,} estabelecimentos, {stats['total_socios']:,} sócios e {stats['total_cnaes']:,} códigos CNAE cadastrados."
        else:
            resposta_texto = f"Encontrei {len(resultados)} resultado(s) para sua consulta. Veja os dados completos abaixo."
        
        return jsonify({
            "resposta_texto": resposta_texto,
            "sql_gerado": sql,
            "total_resultados": len(resultados),
            "dados_completos": resultados
        })
        
    except Exception as e:
        print(f"[ERRO] {str(e)}")
        return jsonify({
            "erro": f"Erro ao processar consulta: {str(e)}"
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint para verificar se a API está funcionando"""
    try:
        if not os.path.exists(DB_PATH):
            raise Exception(f"Banco de dados não encontrado: {DB_PATH}")
        
        # Teste simples de conexão
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM empresas")
        count = cursor.fetchone()[0]
        conn.close()
        
        return jsonify({
            "status": "ok",
            "database": "connected",
            "database_type": "SQLite",
            "total_empresas": count,
            "message": f"API funcionando! {count:,} empresas no banco."
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "database": "disconnected",
            "error": str(e)
        }), 500

if __name__ == '__main__':
    print("=" * 70)
    print(">>> Servidor Flask API (SQLite) iniciando...")
    print("=" * 70)
    print(f"URL: http://localhost:5000")
    print(f"Banco: {DB_PATH}")
    print(f"Consultas SQL diretas baseadas em palavras-chave")
    print(f"Acesse http://localhost:3000 para usar a interface")
    print("=" * 70)
    
    # Verificar se o banco existe
    if not os.path.exists(DB_PATH):
        print(f"\n[!] AVISO: Banco de dados nao encontrado!")
        print(f"    Esperado em: {DB_PATH}")
    else:
        print(f"\n[OK] Banco de dados encontrado!")
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM empresas")
            count = cursor.fetchone()[0]
            conn.close()
            print(f"     Total de empresas: {count:,}")
        except:
            print(f"     (Nao foi possivel contar as empresas)")
    
    print("\n>>> Iniciando servidor...\n")
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

