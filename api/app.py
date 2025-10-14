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
    """Retorna lista de municípios (códigos IBGE) - OTIMIZADO COM NOMES"""
    try:
        import time
        start = time.time()
        
        uf = request.args.get('uf', '')
        limit = min(int(request.args.get('limit', 50)), 200)  # Máximo 200, padrão 50
        
        if uf:
            # TENTATIVA 1: Com JOIN na tabela municipios (se existir)
            sql_com_join = f"""
                SELECT 
                    e.municipio as codigo,
                    COALESCE(m.descricao, e.municipio) as descricao,
                    COUNT(*) as total
                FROM estabelecimentos e
                LEFT JOIN municipios m ON e.municipio = m.codigo
                WHERE e.uf = '{uf}' 
                  AND e.municipio IS NOT NULL 
                  AND e.municipio != ''
                GROUP BY e.municipio, m.descricao
                ORDER BY total DESC
                LIMIT {limit}
            """
            
            # FALLBACK: Sem JOIN (caso tabela municipios não exista)
            sql_sem_join = f"""
                SELECT 
                    municipio as codigo,
                    municipio as descricao,
                    COUNT(*) as total
                FROM estabelecimentos 
                WHERE uf = '{uf}' 
                  AND municipio IS NOT NULL 
                  AND municipio != ''
                GROUP BY municipio
                ORDER BY total DESC
                LIMIT {limit}
            """
            
            try:
                result = executar_sql(sql_com_join)
                print(f"[INFO] Usando query COM JOIN (tabela municipios encontrada)")
            except Exception as join_error:
                print(f"[WARN] JOIN falhou: {join_error}")
                result = executar_sql(sql_sem_join)
                print(f"[WARN] Usando query SEM JOIN (fallback)")
        else:
            # Top municípios do Brasil
            sql = f"""
                SELECT 
                    municipio as codigo,
                    municipio as descricao,
                    COUNT(*) as total
                FROM estabelecimentos 
                WHERE municipio IS NOT NULL AND municipio != ''
                GROUP BY municipio
                ORDER BY total DESC
                LIMIT {limit}
            """
            result = executar_sql(sql)
        
        elapsed = time.time() - start
        
        print(f"[PERFORMANCE] /filtros/municipios (UF={uf}): {elapsed:.2f}s - {len(result)} resultados")
        
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
    """Retorna lista de bairros de um município - OTIMIZADO"""
    try:
        import time
        start = time.time()
        
        uf = request.args.get('uf', '')
        municipio = request.args.get('municipio', '')
        limit = min(int(request.args.get('limit', 100)), 500)
        
        if not municipio:
            return jsonify({"erro": "Parâmetro 'municipio' é obrigatório"}), 400
        
        conditions = [f"municipio = '{municipio}'"]
        if uf:
            conditions.append(f"uf = '{uf}'")
        
        where_clause = " AND ".join(conditions)
        
        # OTIMIZADO: Usa índice e filtra bairros inválidos
        sql = f"""
            SELECT 
                bairro,
                COUNT(*) as total
            FROM estabelecimentos 
            WHERE {where_clause}
              AND bairro IS NOT NULL 
              AND bairro != ''
              AND bairro NOT IN ('NAO INFORMADO', 'NAO DISPONIVEL', '-')
            GROUP BY bairro
            ORDER BY total DESC
            LIMIT {limit}
        """
        
        result = executar_sql(sql)
        elapsed = time.time() - start
        
        print(f"[PERFORMANCE] /filtros/bairros (UF={uf}, MUN={municipio}): {elapsed:.2f}s - {len(result)} resultados")
        
        return jsonify({
            "bairros": result,
            "total": len(result),
            "tempo_ms": int(elapsed * 1000)
        })
    except Exception as e:
        print(f"[ERRO] /filtros/bairros: {str(e)}")
        return jsonify({"erro": str(e)}), 500

@app.route('/filtros/cnaes', methods=['GET'])
def get_cnaes():
    """Retorna CNAEs mais comuns"""
    try:
        limit = request.args.get('limit', 100)
        sql = f"""
            SELECT cnae_fiscal_principal as codigo, COUNT(*) as total 
            FROM estabelecimentos 
            WHERE cnae_fiscal_principal IS NOT NULL 
            GROUP BY cnae_fiscal_principal 
            ORDER BY total DESC 
            LIMIT {limit}
        """
        result = executar_sql(sql)
        return jsonify({"cnaes": result})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route('/filtros/naturezas', methods=['GET'])
def get_naturezas():
    """Retorna naturezas jurídicas mais comuns"""
    try:
        sql = """
            SELECT natureza_juridica as codigo, COUNT(*) as total 
            FROM empresas 
            WHERE natureza_juridica IS NOT NULL 
            GROUP BY natureza_juridica 
            ORDER BY total DESC 
            LIMIT 50
        """
        result = executar_sql(sql)
        return jsonify({"naturezas": result})
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

@app.route('/query/avancada', methods=['GET'])
def query_avancada():
    """Executa query com FILTROS ABRANGENTES - Todos os parâmetros via query string"""
    try:
        # ========== LOCALIZAÇÃO ==========
        uf = request.args.get('uf')
        municipio = request.args.get('municipio')
        bairro = request.args.get('bairro')
        cep = request.args.get('cep')
        
        # ========== IDENTIFICAÇÃO ==========
        razao_social = request.args.get('razaoSocial')
        nome_fantasia = request.args.get('nomeFantasia')
        cnpj = request.args.get('cnpj')
        situacao = request.args.get('situacao')
        matriz_filial = request.args.get('matrizFilial')
        mei = request.args.get('mei')
        
        # ========== ECONÔMICO ==========
        cnae = request.args.get('cnae')
        natureza_juridica = request.args.get('naturezaJuridica')
        porte_empresa = request.args.get('porteEmpresa')
        capital_social_min = request.args.get('capitalSocialMin')
        capital_social_max = request.args.get('capitalSocialMax')
        opcao_simples = request.args.get('opcaoSimples')
        
        # ========== TEMPORAL ==========
        data_abertura_inicio = request.args.get('dataAberturaInicio')
        data_abertura_fim = request.args.get('dataAberturaFim')
        
        # ========== OUTROS ==========
        ddd = request.args.get('ddd')
        
        # ========== PAGINAÇÃO ==========
        limit = min(int(request.args.get('limit', 100)), 5000)
        offset = int(request.args.get('offset', 0))
        
        # ========== CONSTRUIR WHERE ==========
        conditions_estabelecimentos = []
        conditions_empresas = []
        
        # Filtros de estabelecimentos
        if uf:
            conditions_estabelecimentos.append(f"e.uf = '{uf}'")
        if municipio:
            conditions_estabelecimentos.append(f"e.municipio = '{municipio}'")
        if bairro:
            conditions_estabelecimentos.append(f"e.bairro ILIKE '%{bairro}%'")
        if cep:
            conditions_estabelecimentos.append(f"e.cep = '{cep}'")
        if nome_fantasia:
            conditions_estabelecimentos.append(f"e.nome_fantasia ILIKE '%{nome_fantasia}%'")
        if cnpj:
            conditions_estabelecimentos.append(f"CONCAT(e.cnpj_basico, e.cnpj_ordem, e.cnpj_dv) = '{cnpj}'")
        if situacao:
            conditions_estabelecimentos.append(f"e.situacao_cadastral = '{situacao}'")
        if matriz_filial:
            conditions_estabelecimentos.append(f"e.identificador_matriz_filial = '{matriz_filial}'")
        if cnae:
            conditions_estabelecimentos.append(f"e.cnae_fiscal_principal LIKE '{cnae}%'")
        if mei:
            conditions_estabelecimentos.append(f"e.opcao_pelo_mei = '{mei}'")
        if ddd:
            conditions_estabelecimentos.append(f"e.ddd_1 = '{ddd}'")
        if data_abertura_inicio:
            conditions_estabelecimentos.append(f"e.data_inicio_atividade >= '{data_abertura_inicio}'")
        if data_abertura_fim:
            conditions_estabelecimentos.append(f"e.data_inicio_atividade <= '{data_abertura_fim}'")
        if opcao_simples:
            conditions_estabelecimentos.append(f"e.opcao_pelo_simples = '{opcao_simples}'")
        
        # Filtros de empresas
        if razao_social:
            conditions_empresas.append(f"emp.razao_social ILIKE '%{razao_social}%'")
        if natureza_juridica:
            conditions_empresas.append(f"emp.natureza_juridica = '{natureza_juridica}'")
        if porte_empresa:
            conditions_empresas.append(f"emp.porte_empresa = '{porte_empresa}'")
        if capital_social_min:
            conditions_empresas.append(f"emp.capital_social >= {capital_social_min}")
        if capital_social_max:
            conditions_empresas.append(f"emp.capital_social <= {capital_social_max}")
        
        # WHERE final
        where_estabelecimentos = " AND ".join(conditions_estabelecimentos) if conditions_estabelecimentos else "1=1"
        where_empresas = " AND ".join(conditions_empresas) if conditions_empresas else "1=1"
        
        # ========== QUERY PRINCIPAL ==========
        sql = f"""
            SELECT 
                e.cnpj_basico,
                e.cnpj_ordem,
                e.cnpj_dv,
                CONCAT(e.cnpj_basico, e.cnpj_ordem, e.cnpj_dv) as cnpj_completo,
                e.nome_fantasia,
                emp.razao_social,
                e.situacao_cadastral,
                e.identificador_matriz_filial,
                e.uf,
                e.municipio,
                e.bairro,
                e.logradouro,
                e.numero,
                e.cep,
                e.cnae_fiscal_principal,
                e.ddd_1,
                e.telefone_1,
                e.correio_eletronico,
                e.data_inicio_atividade,
                emp.natureza_juridica,
                emp.porte_empresa,
                emp.capital_social,
                e.opcao_pelo_simples,
                e.opcao_pelo_mei
            FROM estabelecimentos e
            LEFT JOIN empresas emp ON e.cnpj_basico = emp.cnpj_basico
            WHERE {where_estabelecimentos}
            {"AND " + where_empresas if conditions_empresas else ""}
            ORDER BY e.cnpj_basico, e.cnpj_ordem
            LIMIT {limit}
            OFFSET {offset}
        """
        
        # ========== COUNT TOTAL ==========
        count_sql = f"""
            SELECT COUNT(*) as total 
            FROM estabelecimentos e
            LEFT JOIN empresas emp ON e.cnpj_basico = emp.cnpj_basico
            WHERE {where_estabelecimentos}
            {"AND " + where_empresas if conditions_empresas else ""}
        """
        
        print(f"[BUSCA AVANÇADA] Executando query com {len(conditions_estabelecimentos) + len(conditions_empresas)} filtros")
        
        resultados = executar_sql(sql)
        total = executar_sql(count_sql)[0]['total']
        
        return jsonify({
            "dados": resultados,
            "total": total,
            "retornados": len(resultados),
            "filtros_ativos": len(conditions_estabelecimentos) + len(conditions_empresas),
            "sql": sql[:500]  # Preview do SQL
        })
        
    except Exception as e:
        print(f"[ERRO BUSCA AVANÇADA] {str(e)}")
        import traceback
        traceback.print_exc()
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

@app.route('/debug/tabelas', methods=['GET'])
def debug_tabelas():
    """Debug: Verificar estrutura das tabelas"""
    try:
        # Ver tabelas disponíveis
        tabelas = executar_sql("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        # Verificar tabela municipios
        municipios_info = {
            "tabela_existe": False,
            "total_registros": 0,
            "exemplo": []
        }
        
        try:
            count = executar_sql("SELECT COUNT(*) as total FROM municipios")
            municipios_info["tabela_existe"] = True
            municipios_info["total_registros"] = count[0]['total'] if count else 0
            
            if municipios_info["total_registros"] > 0:
                exemplos = executar_sql("SELECT * FROM municipios LIMIT 3")
                municipios_info["exemplo"] = exemplos
        except:
            pass
        
        return jsonify({
            "tabelas": tabelas,
            "municipios": municipios_info
        })
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

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
