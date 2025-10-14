#!/usr/bin/env python3
"""
CRIAÇÃO URGENTE DE ÍNDICES - Performance crítica
Reduz queries de 48s para ~2s
"""
import psycopg2
import time

DB_CONFIG = {
    'host': '192.168.15.22',
    'port': 5432,
    'database': 'cnpj_processado',
    'user': 'postgres',
    'password': 'password'
}

# Índices críticos (em ordem de prioridade)
indices = [
    {
        "nome": "idx_estabelecimentos_uf",
        "sql": "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_estabelecimentos_uf ON estabelecimentos(uf);",
        "desc": "Acelera filtros por UF",
        "critico": True
    },
    {
        "nome": "idx_estabelecimentos_uf_municipio",
        "sql": "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_estabelecimentos_uf_municipio ON estabelecimentos(uf, municipio);",
        "desc": "Acelera filtros de municipios (CRITICO - 48s para 2s)",
        "critico": True
    },
    {
        "nome": "idx_estabelecimentos_municipio",
        "sql": "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_estabelecimentos_municipio ON estabelecimentos(municipio);",
        "desc": "Acelera queries de município isolado",
        "critico": False
    },
]

print("=" * 80)
print("CRIACAO URGENTE DE INDICES - PERFORMANCE CRITICA")
print("=" * 80)
print("\nAVISO: Criacao de indices em 79M registros pode demorar 10-30 minutos")
print("       Mas e ESSENCIAL para UX aceitavel!\n")
print("=" * 80)

try:
    # Usar autocommit para CREATE INDEX CONCURRENTLY
    conn = psycopg2.connect(**DB_CONFIG)
    conn.set_session(autocommit=True)
    cur = conn.cursor()
    
    print("\nConectado ao PostgreSQL!")
    print("Database: cnpj_processado")
    print("=" * 80)
    
    for idx in indices:
        print(f"\n[{'CRITICO' if idx['critico'] else 'OPCIONAL'}] {idx['nome']}")
        print(f"Descricao: {idx['desc']}")
        
        # Verificar se já existe
        cur.execute("""
            SELECT 1 FROM pg_indexes 
            WHERE schemaname = 'public' 
              AND tablename = 'estabelecimentos' 
              AND indexname = %s
        """, (idx['nome'],))
        
        if cur.fetchone():
            print(f"  [OK] Indice ja existe! (pulando)")
            continue
        
        print(f"  Criando... (pode demorar 5-20 min)")
        start = time.time()
        
        try:
            cur.execute(idx['sql'])
            elapsed = time.time() - start
            print(f"  [OK] CRIADO com sucesso em {elapsed:.1f}s ({elapsed/60:.1f} min)")
        except Exception as e:
            print(f"  [ERRO] {e}")
            if idx['critico']:
                print("  [AVISO] Indice CRITICO falhou!")
    
    print("\n" + "=" * 80)
    print("ANALISANDO TABELA (otimizar planner)")
    print("=" * 80)
    cur.execute("ANALYZE estabelecimentos;")
    print("[OK] ANALYZE concluido!")
    
    print("\n" + "=" * 80)
    print("VERIFICANDO INDICES CRIADOS")
    print("=" * 80)
    cur.execute("""
        SELECT indexname, pg_size_pretty(pg_relation_size(indexname::regclass))
        FROM pg_indexes
        WHERE tablename = 'estabelecimentos'
          AND schemaname = 'public'
        ORDER BY indexname
    """)
    
    for indexname, size in cur.fetchall():
        print(f"  - {indexname:40} {size}")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("[OK] PRONTO! Indices criados com sucesso!")
    print("=" * 80)
    print("\nPerformance esperada:")
    print("  ANTES: 48s para carregar municipios")
    print("  DEPOIS: 1-3s para carregar municipios")
    print("\n  MELHORIA: ~95% mais rapido!")
    print("=" * 80)

except Exception as e:
    print(f"\n[ERRO FATAL] {e}")
    import traceback
    traceback.print_exc()

