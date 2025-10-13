# -*- coding: utf-8 -*-
"""
API Flask simplificada para consultas ao banco PostgreSQL via Supabase
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import json

# Cria a aplicação Flask
app = Flask(__name__)
CORS(app)

# Configuração do Supabase local
SUPABASE_DB_URL = "postgresql://postgres:postgres@localhost:54322/postgres"

def executar_sql_via_psql(sql: str):
    """Executa SQL via psql e retorna os resultados em JSON"""
    try:
        # Comando psql com formato JSON
        cmd = [
            'docker', 'exec', '-i', 'supabase_db_PwC',
            'psql', '-U', 'postgres', '-d', 'postgres',
            '-c', sql,
            '-t',  # Apenas dados (sem headers)
            '--no-align',  # Sem alinhamento
            '--field-separator', '|'  # Separador de campos
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.returncode != 0:
            raise Exception(f"Erro ao executar SQL: {result.stderr}")
        
        # Parse dos resultados
        output = result.stdout.strip()
        if not output:
            return []
        
        lines = [line for line in output.split('\n') if line.strip()]
        if not lines:
            return []
        
        # Obter colunas
        cmd_columns = [
            'docker', 'exec', '-i', 'supabase_db_PwC',
            'psql', '-U', 'postgres', '-d', 'postgres',
            '-c', sql + ' LIMIT 0',  # Apenas headers
        ]
        
        result_cols = subprocess.run(cmd_columns, capture_output=True, text=True, encoding='utf-8')
        
        # Parse simples: primeira linha tem os nomes das colunas
        # Para simplificar, vamos retornar como string primeiro
        resultados = []
        for line in lines:
            if '|' in line:
                values = line.split('|')
                resultados.append({'resultado': line})
        
        return resultados
        
    except Exception as e:
        print(f"Erro ao executar SQL: {e}")
        raise

def gerar_sql_simples(pergunta: str) -> str:
    """Gera SQL simples baseado em palavras-chave"""
    pergunta_lower = pergunta.lower()
    
    # Busca por nome de empresa
    if 'empresa' in pergunta_lower or 'razao' in pergunta_lower or 'nome' in pergunta_lower:
        # Extrair o termo de busca
        palavras = pergunta.split()
        termo_busca = ' '.join([p for p in palavras if len(p) > 3])
        return f"""SELECT "cnpj basico", "razao social", "porte empresa" 
                   FROM empresas 
                   WHERE "razao social" ILIKE '%{termo_busca}%' 
                   LIMIT 10"""
    
    # Busca por município
    elif 'municipio' in pergunta_lower or 'cidade' in pergunta_lower:
        palavras = pergunta.split()
        municipio = next((p.upper() for p in palavras if len(p) > 3 and p.lower() not in ['qual', 'quais', 'empresa', 'empresas', 'municipio', 'cidade']), 'SAO PAULO')
        return f"""SELECT e."razao social", est.municipio, est.uf
                   FROM empresas e
                   JOIN estabelecimentos est ON e."cnpj basico" = est."cnpj basico"
                   WHERE est.municipio ILIKE '%{municipio}%'
                   LIMIT 20"""
    
    # Busca por CNAE/atividade
    elif 'cnae' in pergunta_lower or 'atividade' in pergunta_lower or 'logistica' in pergunta_lower:
        return """SELECT e."razao social", c.descricao as atividade, est.municipio
                  FROM empresas e
                  JOIN estabelecimentos est ON e."cnpj basico" = est."cnpj basico"
                  JOIN cnaes c ON est.cnae_fiscal_principal::text = c.codigo
                  WHERE c.descricao ILIKE '%logistica%' 
                     OR c.descricao ILIKE '%transporte%'
                  LIMIT 20"""
    
    # Query padrão
    else:
        return """SELECT "cnpj basico", "razao social", "porte empresa" 
                  FROM empresas 
                  LIMIT 10"""

@app.route('/query', methods=['POST'])
def handle_query():
    """Endpoint principal que recebe a pergunta e retorna os resultados"""
    try:
        data = request.get_json()
        pergunta = data.get('question')
        
        if not pergunta:
            return jsonify({"erro": "Nenhuma pergunta foi fornecida."}), 400
        
        print(f"\n📥 Pergunta recebida: '{pergunta}'")
        
        # Gerar SQL
        sql = gerar_sql_simples(pergunta)
        print(f"📝 SQL gerado: {sql}")
        
        # Executar query
        print("⚡ Executando query no PostgreSQL...")
        resultados = executar_sql_via_psql(sql)
        print(f"✅ {len(resultados)} resultados encontrados")
        
        # Gerar resposta
        resposta_texto = f"Encontrei {len(resultados)} resultado(s) para sua consulta."
        if len(resultados) > 0:
            resposta_texto += f" Aqui estão os primeiros resultados."
        
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
        # Teste simples de conexão
        result = subprocess.run(
            ['docker', 'exec', 'supabase_db_PwC', 'psql', '-U', 'postgres', '-c', 'SELECT 1'],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            return jsonify({
                "status": "ok",
                "database": "connected",
                "message": "API e banco de dados funcionando!"
            })
        else:
            raise Exception("Falha ao conectar ao banco")
    except Exception as e:
        return jsonify({
            "status": "error",
            "database": "disconnected",
            "error": str(e)
        }), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Servidor Flask API SIMPLIFICADA iniciando...")
    print("=" * 60)
    print(f"📍 URL: http://localhost:5000")
    print(f"🗄️  PostgreSQL via Supabase Docker")
    print("📝 Usando queries SQL diretas (sem IA)")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)

