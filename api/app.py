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
bairros_cache = {}
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
        
        # Cache de UFs (não mudam) - formato correto
        if 'ufs_cache' not in globals():
            sql = """
                SELECT uf as codigo, uf as descricao, COUNT(*) as total
                FROM estabelecimentos 
                WHERE uf IS NOT NULL AND uf != ''
                GROUP BY uf
                ORDER BY uf
            """
            result = executar_sql(sql)
            # Formatar corretamente para o frontend
            ufs_formatadas = []
            for row in result:
                ufs_formatadas.append({
                    'codigo': row['codigo'],
                    'descricao': f"{row['descricao']} ({row['total']:,} empresas)",
                    'total': row['total']
                })
            globals()['ufs_cache'] = ufs_formatadas
        
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
    """Retorna lista de municípios - BUSCA POR LIKE (DIGITAÇÃO)"""
    try:
        start = time.time()
        
        uf = request.args.get('uf', '')
        busca = request.args.get('busca', '').strip().upper()  # Termo de busca
        limit = min(int(request.args.get('limit', 50)), 100)   # Limite menor para LIKE
        
        if uf:
            # Cache com chave incluindo busca
            cache_key = f"municipios_{uf}_{busca}"
            if cache_key in municipios_cache and busca:  # Só usar cache se tiver busca
                cached_data = municipios_cache[cache_key]
                if (time.time() - cache_timestamp.get(cache_key, 0)) < 1800:  # Cache válido por 30 min
                    print(f"[CACHE] Municípios {uf}/{busca} carregados do cache")
                    return jsonify({
                        "municipios": cached_data,
                        "total": len(cached_data),
                        "tempo_ms": int((time.time() - start) * 1000)
                    })
            
            if busca and len(busca) >= 2:  # Busca por LIKE se tiver 2+ caracteres
                # Query com LIKE para busca rápida
                sql = """
                    SELECT DISTINCT e.municipio as codigo, m.descricao
                    FROM estabelecimentos e
                    LEFT JOIN municipios m ON e.municipio = m.codigo
                    WHERE e.uf = %s 
                      AND e.municipio IS NOT NULL 
                      AND e.municipio != ''
                      AND UPPER(COALESCE(m.descricao, e.municipio)) LIKE %s
                    ORDER BY m.descricao
                    LIMIT %s
                """
                
                busca_like = f"%{busca}%"
                result = executar_sql(sql, (uf, busca_like, limit))
                
                municipios_traduzidos = []
                for row in result:
                    codigo = row['codigo']
                    descricao = row['descricao'] or codigo  # Fallback para código se não tiver descrição
                    
                    municipios_traduzidos.append({
                        'codigo': codigo,
                        'descricao': descricao,
                        'total': 0
                    })
                
                print(f"[PERFORMANCE] Municípios {uf} LIKE '{busca}': {len(municipios_traduzidos)} em {time.time() - start:.3f}s")
                
            else:  # Sem busca ou busca muito curta - retornar lista vazia
                municipios_traduzidos = []
                print(f"[PERFORMANCE] Municípios {uf}: Sem busca ou busca < 2 caracteres")
            
            # Salvar no cache se tiver busca
            if busca:
                municipios_cache[cache_key] = municipios_traduzidos
                cache_timestamp[cache_key] = time.time()
            
            result = municipios_traduzidos
            
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
    """Retorna lista de bairros - BUSCA POR LIKE (DIGITAÇÃO)"""
    try:
        start = time.time()
        
        uf = request.args.get('uf', '')
        municipio = request.args.get('municipio', '')
        busca = request.args.get('busca', '').strip().upper()  # Termo de busca
        limit = min(int(request.args.get('limit', 50)), 100)   # Limite menor para LIKE
        
        if uf and municipio:
            # Cache com chave incluindo busca
            cache_key = f"bairros_{uf}_{municipio}_{busca}"
            if cache_key in bairros_cache and busca:  # Só usar cache se tiver busca
                cached_data = bairros_cache[cache_key]
                if (time.time() - cache_timestamp.get(cache_key, 0)) < 1800:  # Cache válido por 30 min
                    print(f"[CACHE] Bairros {uf}/{municipio}/{busca} carregados do cache")
                    return jsonify({
                        "bairros": cached_data,
                        "total": len(cached_data),
                        "tempo_ms": int((time.time() - start) * 1000)
                    })
            
            if busca and len(busca) >= 2:  # Busca por LIKE se tiver 2+ caracteres
                # Query com LIKE para busca rápida
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
                      AND UPPER(bairro) LIKE %s
                    GROUP BY bairro
                    ORDER BY total DESC
                    LIMIT %s
                """
                
                busca_like = f"%{busca}%"
                result = executar_sql(sql, (uf, municipio, busca_like, limit))
                
                # Formatar bairros com nome + quantidade
                bairros_formatados = []
                for row in result:
                    bairros_formatados.append({
                        'codigo': row['codigo'],
                        'descricao': f"{row['descricao']} ({row['total']:,} empresas)",
                        'total': row['total']
                    })
                
                print(f"[PERFORMANCE] Bairros {uf}/{municipio} LIKE '{busca}': {len(bairros_formatados)} em {time.time() - start:.3f}s")
                
            else:  # Sem busca ou busca muito curta - retornar lista vazia
                bairros_formatados = []
                print(f"[PERFORMANCE] Bairros {uf}/{municipio}: Sem busca ou busca < 2 caracteres")
            
            # Salvar no cache se tiver busca
            if busca:
                bairros_cache[cache_key] = bairros_formatados
                cache_timestamp[cache_key] = time.time()
            
            result = bairros_formatados
        
        elapsed = time.time() - start
        
        return jsonify({
            "bairros": result,
            "total": len(result),
            "tempo_ms": int(elapsed * 1000)
        })
    except Exception as e:
        print(f"[ERRO] /filtros/bairros: {str(e)}")
        return jsonify({"erro": str(e)}), 500

@app.route('/filtros/cep', methods=['GET'])
def get_cep_info():
    """CEP como entrada primária - BUSCA RÁPIDA"""
    try:
        start = time.time()
        
        cep = request.args.get('cep', '').replace('-', '').replace('.', '').strip()
        
        if not cep or len(cep) != 8:
            return jsonify({
                "erro": "CEP deve ter 8 dígitos",
                "exemplo": "01310100"
            }), 400
        
        # Buscar informações do CEP
        sql = """
            SELECT 
                cep,
                uf,
                municipio,
                bairro,
                logradouro,
                COUNT(*) as total_empresas
            FROM estabelecimentos 
            WHERE cep = %s
            GROUP BY cep, uf, municipio, bairro, logradouro
            ORDER BY total_empresas DESC
            LIMIT 50
        """
        
        result = executar_sql(sql, (cep,))
        
        if not result:
            return jsonify({
                "erro": "CEP não encontrado",
                "cep": cep
            }), 404
        
        # Traduzir município
        if result:
            municipio_codigo = result[0]['municipio']
            municipio_nome = traduzir_municipio(municipio_codigo)
            
            # Adicionar nome traduzido ao resultado
            for row in result:
                row['municipio_nome'] = municipio_nome
        
        elapsed = time.time() - start
        
        return jsonify({
            "cep": cep,
            "resultados": result,
            "total": len(result),
            "tempo_ms": int(elapsed * 1000)
        })
        
    except Exception as e:
        print(f"[ERRO] /filtros/cep: {str(e)}")
        return jsonify({"erro": str(e)}), 500

@app.route('/filtros/cep/autocomplete', methods=['GET'])
def get_cep_autocomplete():
    """Autocomplete de CEP - BUSCA RÁPIDA"""
    try:
        start = time.time()
        
        cep_partial = request.args.get('cep', '').replace('-', '').replace('.', '').strip()
        
        if len(cep_partial) < 5:
            return jsonify({
                "ceps": [],
                "total": 0,
                "tempo_ms": 0
            })
        
        # Buscar CEPs similares
        sql = """
            SELECT DISTINCT
                cep,
                uf,
                municipio,
                bairro,
                COUNT(*) as total_empresas
            FROM estabelecimentos 
            WHERE cep LIKE %s
              AND cep IS NOT NULL
              AND cep != ''
            GROUP BY cep, uf, municipio, bairro
            ORDER BY total_empresas DESC
            LIMIT 20
        """
        
        result = executar_sql(sql, (f"{cep_partial}%",))
        
        # Traduzir municípios
        for row in result:
            municipio_codigo = row['municipio']
            row['municipio_nome'] = traduzir_municipio(municipio_codigo)
        
        elapsed = time.time() - start
        
        return jsonify({
            "ceps": result,
            "total": len(result),
            "tempo_ms": int(elapsed * 1000)
        })
        
    except Exception as e:
        print(f"[ERRO] /filtros/cep/autocomplete: {str(e)}")
        return jsonify({"erro": str(e)}), 500

@app.route('/query/avancada', methods=['GET'])
def query_avancada():
    """Busca avançada de empresas - ENDPOINT PRINCIPAL"""
    try:
        start = time.time()
        
        # Receber parâmetros
        uf = request.args.get('uf', '').strip()
        municipio = request.args.get('municipio', '').strip()
        bairro = request.args.get('bairro', '').strip()
        cep = request.args.get('cep', '').strip()
        razao_social = request.args.get('razaoSocial', '').strip()
        nome_fantasia = request.args.get('nomeFantasia', '').strip()
        cnpj = request.args.get('cnpj', '').strip()
        situacao = request.args.get('situacao', '').strip()
        matriz_filial = request.args.get('matrizFilial', '').strip()
        cnae = request.args.get('cnae', '').strip()
        natureza_juridica = request.args.get('naturezaJuridica', '').strip()
        porte_empresa = request.args.get('porteEmpresa', '').strip()
        capital_social_min = request.args.get('capitalSocialMin', '').strip()
        capital_social_max = request.args.get('capitalSocialMax', '').strip()
        data_abertura_inicio = request.args.get('dataAberturaInicio', '').strip()
        data_abertura_fim = request.args.get('dataAberturaFim', '').strip()
        mei = request.args.get('mei', '').strip()
        ddd = request.args.get('ddd', '').strip()
        opcao_simples = request.args.get('opcaoSimples', '').strip()
        limit = min(int(request.args.get('limit', 100)), 500)
        offset = int(request.args.get('offset', 0))
        
        print(f"[BUSCA] Filtros recebidos: UF={uf}, Municipio={municipio}, Bairro={bairro}")
        
        # Construir query dinamicamente
        where_clauses = []
        params = []
        
        # Localização
        if uf:
            where_clauses.append("e.uf = %s")
            params.append(uf)
        
        if municipio:
            # Se for um nome, buscar o código primeiro
            if not municipio.isdigit():
                try:
                    sql_municipio = "SELECT codigo FROM municipios WHERE UPPER(descricao) LIKE %s LIMIT 1"
                    result_mun = executar_sql(sql_municipio, (f"%{municipio.upper()}%",))
                    if result_mun:
                        municipio_codigo = result_mun[0]['codigo']
                        where_clauses.append("e.municipio = %s")
                        params.append(municipio_codigo)
                        print(f"[BUSCA] Município '{municipio}' traduzido para código {municipio_codigo}")
                except:
                    pass
            else:
                where_clauses.append("e.municipio = %s")
                params.append(municipio)
        
        if bairro:
            # Se for nome completo com contagem, extrair só o nome
            if '(' in bairro:
                bairro = bairro.split('(')[0].strip()
            where_clauses.append("UPPER(e.bairro) = %s")
            params.append(bairro.upper())
        
        if cep:
            where_clauses.append("e.cep = %s")
            params.append(cep)
        
        # Identificação
        if razao_social:
            where_clauses.append("UPPER(emp.razao_social) LIKE %s")
            params.append(f"%{razao_social.upper()}%")
        
        if nome_fantasia:
            where_clauses.append("UPPER(e.nome_fantasia) LIKE %s")
            params.append(f"%{nome_fantasia.upper()}%")
        
        if cnpj:
            cnpj_limpo = cnpj.replace('.', '').replace('/', '').replace('-', '')
            where_clauses.append("(e.cnpj_basico || e.cnpj_ordem || e.cnpj_dv) LIKE %s")
            params.append(f"%{cnpj_limpo}%")
        
        if situacao:
            where_clauses.append("e.situacao_cadastral = %s")
            params.append(situacao)
        
        if matriz_filial:
            where_clauses.append("e.identificador_matriz_filial = %s")
            params.append(matriz_filial)
        
        # Dados econômicos
        if cnae:
            where_clauses.append("e.cnae_fiscal_principal = %s")
            params.append(cnae)
        
        if natureza_juridica:
            where_clauses.append("emp.natureza_juridica = %s")
            params.append(natureza_juridica)
        
        if porte_empresa:
            where_clauses.append("emp.porte_empresa = %s")
            params.append(porte_empresa)
        
        if capital_social_min:
            where_clauses.append("CAST(emp.capital_social AS NUMERIC) >= %s")
            params.append(float(capital_social_min))
        
        if capital_social_max:
            where_clauses.append("CAST(emp.capital_social AS NUMERIC) <= %s")
            params.append(float(capital_social_max))
        
        # Período
        if data_abertura_inicio:
            where_clauses.append("e.data_inicio_atividade >= %s")
            params.append(data_abertura_inicio)
        
        if data_abertura_fim:
            where_clauses.append("e.data_inicio_atividade <= %s")
            params.append(data_abertura_fim)
        
        # Outros
        if mei:
            where_clauses.append("emp.mei = %s")
            params.append(mei)
        
        if ddd:
            where_clauses.append("e.ddd_1 = %s")
            params.append(ddd)
        
        if opcao_simples:
            where_clauses.append("emp.opcao_simples = %s")
            params.append(opcao_simples)
        
        # Montar query final
        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        sql = f"""
            SELECT 
                (e.cnpj_basico || e.cnpj_ordem || e.cnpj_dv) as cnpj,
                emp.razao_social,
                e.nome_fantasia,
                e.situacao_cadastral,
                e.data_situacao_cadastral,
                e.uf,
                e.municipio,
                e.bairro,
                e.cep,
                e.cnae_fiscal_principal as cnae_fiscal,
                e.data_inicio_atividade,
                emp.porte_empresa,
                emp.capital_social,
                e.identificador_matriz_filial as matriz_filial,
                e.ddd_1 as ddd,
                e.telefone_1 as telefone
            FROM estabelecimentos e
            LEFT JOIN empresas emp ON e.cnpj_basico = emp.cnpj_basico
            WHERE {where_sql}
            ORDER BY emp.razao_social
            LIMIT %s OFFSET %s
        """
        
        params.extend([limit, offset])
        
        print(f"[BUSCA] Executando query com {len(where_clauses)} filtros")
        result = executar_sql(sql, tuple(params))
        
        # Traduzir municípios nos resultados
        for row in result:
            if row.get('municipio'):
                row['municipio_nome'] = traduzir_municipio(row['municipio'])
        
        # Contar total
        count_sql = f"""
            SELECT COUNT(*) as total
            FROM estabelecimentos e
            LEFT JOIN empresas emp ON e.cnpj_basico = emp.cnpj_basico
            WHERE {where_sql}
        """
        
        count_result = executar_sql(count_sql, tuple(params[:-2]))  # Remover LIMIT e OFFSET
        total = count_result[0]['total'] if count_result else 0
        
        elapsed = time.time() - start
        
        print(f"[BUSCA] Encontrados {len(result)} registros de {total} total em {elapsed:.3f}s")
        
        return jsonify({
            "dados": result,
            "total": total,
            "limit": limit,
            "offset": offset,
            "tempo_ms": int(elapsed * 1000)
        })
        
    except Exception as e:
        print(f"[ERRO] /query/avancada: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"erro": str(e), "dados": [], "total": 0}), 500

if __name__ == '__main__':
    print("="*60)
    print("API Flask Otimizada iniciando...")
    print(f"Host: {os.getenv('DB_HOST', 'crm-postgres')}:{os.getenv('DB_PORT', '5432')}")
    print(f"Database: {os.getenv('DB_NAME', 'cnpj_processado')}")
    print("="*60)
    
    app.run(host='0.0.0.0', port=5000, debug=False)
