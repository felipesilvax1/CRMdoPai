#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Criação de Índices de Performance
ETA: 20-40 min
"""

import psycopg2
import time
from datetime import datetime

# Configuração
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': 'postgres',
    'database': 'cnpj_processado'
}

# Índices críticos
INDICES = [
    {
        'nome': 'idx_estabelecimentos_uf_municipio',
        'tabela': 'estabelecimentos',
        'colunas': '(uf, municipio)',
        'descricao': 'Filtro UF + Município (cascata)'
    },
    {
        'nome': 'idx_estabelecimentos_uf',
        'tabela': 'estabelecimentos',
        'colunas': '(uf)',
        'descricao': 'Filtro UF'
    },
    {
        'nome': 'idx_estabelecimentos_municipio',
        'tabela': 'estabelecimentos',
        'colunas': '(municipio)',
        'descricao': 'Filtro Município'
    },
    {
        'nome': 'idx_estabelecimentos_bairro',
        'tabela': 'estabelecimentos',
        'colunas': '(bairro)',
        'descricao': 'Filtro Bairro'
    },
    {
        'nome': 'idx_estabelecimentos_cnae',
        'tabela': 'estabelecimentos',
        'colunas': '(cnae_fiscal)',
        'descricao': 'Filtro CNAE'
    },
    {
        'nome': 'idx_estabelecimentos_situacao',
        'tabela': 'estabelecimentos',
        'colunas': '(situacao_cadastral)',
        'descricao': 'Filtro Situação'
    },
    {
        'nome': 'idx_estabelecimentos_cep',
        'tabela': 'estabelecimentos',
        'colunas': '(cep)',
        'descricao': 'Filtro CEP'
    },
    {
        'nome': 'idx_estabelecimentos_ddd',
        'tabela': 'estabelecimentos',
        'colunas': '(ddd1)',
        'descricao': 'Filtro DDD'
    },
]

def print_utf8(msg):
    """Print com encoding UTF-8 seguro"""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore'))

def criar_indices():
    """Criar todos os índices"""
    print_utf8("\n" + "="*60)
    print_utf8("CRIAÇÃO DE ÍNDICES DE PERFORMANCE")
    print_utf8("="*60)
    
    start_total = time.time()
    
    try:
        # Conectar
        print_utf8("\n📡 Conectando ao PostgreSQL...")
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        cur = conn.cursor()
        
        print_utf8("✅ Conectado com sucesso!")
        
        # Verificar total de registros
        cur.execute("SELECT COUNT(*) FROM estabelecimentos")
        total_registros = cur.fetchone()[0]
        print_utf8(f"\n📊 Total de registros: {total_registros:,}")
        
        # Criar cada índice
        indices_criados = 0
        for idx, indice in enumerate(INDICES, 1):
            print_utf8(f"\n[{idx}/{len(INDICES)}] {indice['descricao']}")
            print_utf8(f"    Índice: {indice['nome']}")
            
            # Verificar se já existe
            cur.execute("""
                SELECT 1 FROM pg_indexes 
                WHERE indexname = %s
            """, (indice['nome'],))
            
            if cur.fetchone():
                print_utf8("    ⏭️  Já existe, pulando...")
                continue
            
            # Criar índice
            start = time.time()
            sql = f"""
                CREATE INDEX CONCURRENTLY IF NOT EXISTS {indice['nome']}
                ON {indice['tabela']} {indice['colunas']}
            """
            
            print_utf8("    ⏳ Criando...")
            try:
                cur.execute(sql)
                duration = time.time() - start
                print_utf8(f"    ✅ Criado em {duration:.1f}s")
                indices_criados += 1
            except Exception as e:
                print_utf8(f"    ⚠️  Erro: {e}")
                continue
        
        # Resumo
        duration_total = time.time() - start_total
        print_utf8("\n" + "="*60)
        print_utf8("✅ PROCESSO CONCLUÍDO!")
        print_utf8("="*60)
        print_utf8(f"\n📊 Estatísticas:")
        print_utf8(f"   • Índices criados: {indices_criados}/{len(INDICES)}")
        print_utf8(f"   • Tempo total: {duration_total/60:.1f} min")
        print_utf8(f"   • Registros indexados: {total_registros:,}")
        
        print_utf8("\n🚀 Próximo passo: Testar performance!")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print_utf8(f"\n❌ ERRO: {e}")
        return False
    
    return True

if __name__ == "__main__":
    criar_indices()

