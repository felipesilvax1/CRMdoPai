#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Flask Otimizada para CRM
- Performance otimizada para S&O
- Cache inteligente
- Tradução de municípios
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import psycopg2.extras
import time
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Cache em memória para traduções
municipios_cache = {}
cache_timestamp = {}

def executar_sql(sql, params=None):
    """Executa SQL com conexão otimizada"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'crm-postgres'),
            port=os.getenv('DB_PORT', '5432'),
            database=os.getenv('DB_NAME', 'cnpj_processado'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'postgres')
        )
        
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(sql, params)
        
        if cursor.description:
            result = cursor.fetchall()
            return [dict(row) for row in result]
        else:
            return []
            
    except Exception as e:
        print(f"[ERRO SQL] {str(e)}")
        raise e
    finally:
        if 'conn' in locals():
            conn.close()

def traduzir_municipio(codigo):
    """Traduz código IBGE para nome (com cache)"""
    # Verificar cache (válido por 1 hora)
    now = time.time()
    if codigo in municipios_cache and (now - cache_timestamp.get(codigo, 0)) < 3600:
        return municipios_cache[codigo]
    
    try:
        sql = "SELECT descricao FROM municipios WHERE codigo = %s LIMIT 1"
        result = executar_sql(sql, (codigo,))
        descricao = result[0]['descricao'] if result else codigo
        
        # Salvar no cache
        municipios_cache[codigo] = descricao
        cache_timestamp[codigo] = now
        
        return descricao
    except:
        return codigo

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})

@app.route('/filtros/ufs', methods=['GET'])
def get_ufs():
    """Retorna lista de UFs - SUPER OTIMIZADO"""
    try:
        start = time.time()
        
        # Cache de UFs (não mudam)
        if 'ufs_cache' not in globals():
            sql = """
                SELECT uf as codigo, uf as descricao, COUNT(*) as total
                FROM estabelecimentos 
                WHERE uf IS NOT NULL AND uf != ''
                GROUP BY uf
                ORDER BY uf
            """
            result = executar_sql(sql)
            globals()['ufs_cache'] = result
        
        elapsed = time.time() - start
        
        return jsonify({
            "ufs": globals()['ufs_cache'],
            "total": len(globals()['ufs_cache']),
            "tempo_ms": int(elapsed * 1000)
        })
    except Exception as e:
        print(f"[ERRO] /filtros/ufs: {str(e)}")
        return jsonify({"erro": str(e)}), 500

@app.route('/filtros/municipios', methods=['GET'])
def get_municipios():
    """Retorna lista de municípios - PERFORMANCE + TRADUÇÃO"""
    try:
        start = time.time()
        
        uf = request.args.get('uf', '')
        limit = min(int(request.args.get('limit', 50)), 200)
        
        if uf:
            # Query principal (rápida)
            sql = """
                SELECT 
                    municipio as codigo,
                    COUNT(*) as total
                FROM estabelecimentos 
                WHERE uf = %s 
                  AND municipio IS NOT NULL 
                  AND municipio != ''
                GROUP BY municipio
                ORDER BY total DESC
                LIMIT %s
            """
            
            result = executar_sql(sql, (uf, limit))
            
            # Traduzir em paralelo (otimizado)
            municipios_traduzidos = []
            for row in result:
                codigo = row['codigo']
                total = row['total']
                descricao = traduzir_municipio(codigo)
                
                municipios_traduzidos.append({
                    'codigo': codigo,
                    'descricao': descricao,
                    'total': total
                })
            
            result = municipios_traduzidos
            print(f"[PERFORMANCE] Municípios {uf}: {len(result)} traduzidos em {time.time() - start:.3f}s")
            
        else:
            # Top municípios do Brasil
            sql = """
                SELECT 
                    municipio as codigo,
                    municipio as descricao,
                    COUNT(*) as total
                FROM estabelecimentos 
                WHERE municipio IS NOT NULL AND municipio != ''
                GROUP BY municipio
                ORDER BY total DESC
                LIMIT %s
            """
            result = executar_sql(sql, (limit,))
        
        elapsed = time.time() - start
        
        return jsonify({
            "municipios": result,
            "total": len(result),
            "tempo_ms": int(elapsed * 1000)
        })
    except Exception as e:
        print(f"[ERRO] /filtros/municipios: {str(e)}")
        return jsonify({"erro": str(e)}), 500

@app.route('/filtros/bairros', methods=['GET'])
def get_bairros():
    """Retorna lista de bairros - OTIMIZADO"""
    try:
        start = time.time()
        
        uf = request.args.get('uf', '')
        municipio = request.args.get('municipio', '')
        limit = min(int(request.args.get('limit', 100)), 500)
        
        if uf and municipio:
            sql = """
                SELECT 
                    bairro as codigo,
                    bairro as descricao,
                    COUNT(*) as total
                FROM estabelecimentos 
                WHERE uf = %s 
                  AND municipio = %s
                  AND bairro IS NOT NULL 
                  AND bairro != ''
                  AND bairro != 'NAO INFORMADO'
                  AND bairro != 'N/A'
                GROUP BY bairro
                ORDER BY total DESC
                LIMIT %s
            """
            
            result = executar_sql(sql, (uf, municipio, limit))
        
        elapsed = time.time() - start
        
        return jsonify({
            "bairros": result,
            "total": len(result),
            "tempo_ms": int(elapsed * 1000)
        })
    except Exception as e:
        print(f"[ERRO] /filtros/bairros: {str(e)}")
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    print("="*60)
    print("API Flask Otimizada iniciando...")
    print(f"Host: {os.getenv('DB_HOST', 'crm-postgres')}:{os.getenv('DB_PORT', '5432')}")
    print(f"Database: {os.getenv('DB_NAME', 'cnpj_processado')}")
    print("="*60)
    
    app.run(host='0.0.0.0', port=5000, debug=False)
