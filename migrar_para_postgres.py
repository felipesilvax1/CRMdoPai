# -*- coding: utf-8 -*-
"""
Script para migrar dados do SQLite para PostgreSQL/Supabase
"""
import sqlite3
import psycopg2
from psycopg2 import sql
import sys

# Configurações
SQLITE_DB = "C:/Users/PwC/Documents/CRM/CNPJ_Processado.db"
PG_CONFIG = {
    'host': 'localhost',
    'port': '54322',
    'database': 'postgres',
    'user': 'postgres',
    'password': 'postgres'
}

BATCH_SIZE = 10000  # Registros por lote

def conectar_sqlite():
    """Conecta ao banco SQLite"""
    return sqlite3.connect(SQLITE_DB)

def conectar_postgres():
    """Conecta ao PostgreSQL"""
    return psycopg2.connect(**PG_CONFIG)

def criar_tabelas_postgres(pg_conn):
    """Cria estrutura das tabelas no PostgreSQL"""
    print("\n[1/5] Criando estrutura das tabelas...")
    
    with pg_conn.cursor() as cursor:
        # Tabela empresas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS empresas (
                "cnpj basico" VARCHAR(8) PRIMARY KEY,
                "razao social" TEXT,
                "natureza juridica" VARCHAR(4),
                "qualificacao responsavel" VARCHAR(2),
                "capital social" NUMERIC,
                "porte empresa" VARCHAR(2),
                "ente federativo responsavel" TEXT
            );
        """)
        
        # Tabela estabelecimentos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS estabelecimentos (
                "cnpj basico" VARCHAR(8),
                cnpj_ordem VARCHAR(4),
                cnpj_dv VARCHAR(2),
                "identificador matriz filial" VARCHAR(1),
                "nome fantasia" TEXT,
                "situacao cadastral" VARCHAR(2),
                "data situacao cadastral" VARCHAR(8),
                municipio VARCHAR(100),
                bairro TEXT,
                logradouro TEXT,
                numero VARCHAR(20),
                complemento TEXT,
                cep VARCHAR(8),
                uf VARCHAR(2),
                cnae_fiscal_principal VARCHAR(7),
                cnae_fiscal_secundaria TEXT,
                PRIMARY KEY ("cnpj basico", cnpj_ordem, cnpj_dv)
            );
        """)
        
        # Tabela socios
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS socios (
                "cnpj basico" VARCHAR(8),
                "identificador de socio" VARCHAR(1),
                "nome socio razao social" TEXT,
                "cnpj cpf do socio" VARCHAR(14),
                "qualificacao socio" VARCHAR(2),
                "data entrada sociedade" VARCHAR(8),
                PRIMARY KEY ("cnpj basico", "identificador de socio", "cnpj cpf do socio")
            );
        """)
        
        # Tabela cnaes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cnaes (
                codigo VARCHAR(7) PRIMARY KEY,
                descricao TEXT
            );
        """)
        
        pg_conn.commit()
        print("    [OK] Tabelas criadas!")

def migrar_tabela(sqlite_conn, pg_conn, tabela, colunas):
    """Migra uma tabela específica"""
    print(f"\n[Migrando] {tabela}...")
    
    # Contar registros
    sqlite_cursor = sqlite_conn.cursor()
    sqlite_cursor.execute(f'SELECT COUNT(*) FROM "{tabela}"')
    total = sqlite_cursor.fetchone()[0]
    print(f"    Total de registros: {total:,}")
    
    if total == 0:
        print(f"    [AVISO] Tabela {tabela} vazia, pulando...")
        return
    
    # Preparar INSERT
    placeholders = ','.join(['%s'] * len(colunas))
    colunas_quoted = ','.join([f'"{col}"' for col in colunas])
    insert_sql = f'INSERT INTO "{tabela}" ({colunas_quoted}) VALUES ({placeholders}) ON CONFLICT DO NOTHING'
    
    # Migrar em lotes
    offset = 0
    pg_cursor = pg_conn.cursor()
    
    while offset < total:
        # Ler lote do SQLite
        sqlite_cursor.execute(
            f'SELECT {colunas_quoted} FROM "{tabela}" LIMIT {BATCH_SIZE} OFFSET {offset}'
        )
        rows = sqlite_cursor.fetchall()
        
        if not rows:
            break
        
        # Inserir no PostgreSQL
        try:
            psycopg2.extras.execute_batch(pg_cursor, insert_sql, rows, page_size=1000)
            pg_conn.commit()
            offset += len(rows)
            progresso = (offset / total) * 100
            print(f"    Progresso: {offset:,}/{total:,} ({progresso:.1f}%)", end='\r')
        except Exception as e:
            print(f"\n    [ERRO] ao inserir lote: {e}")
            pg_conn.rollback()
            break
    
    print(f"\n    [OK] {tabela} migrada com sucesso!")

def criar_indices(pg_conn):
    """Cria índices para performance"""
    print("\n[5/5] Criando índices...")
    
    with pg_conn.cursor() as cursor:
        indices = [
            'CREATE INDEX IF NOT EXISTS idx_empresas_razao ON empresas("razao social")',
            'CREATE INDEX IF NOT EXISTS idx_est_cnpj ON estabelecimentos("cnpj basico")',
            'CREATE INDEX IF NOT EXISTS idx_est_municipio ON estabelecimentos(municipio)',
            'CREATE INDEX IF NOT EXISTS idx_socios_cnpj ON socios("cnpj basico")',
            'CREATE INDEX IF NOT EXISTS idx_cnaes_desc ON cnaes(descricao)',
        ]
        
        for idx in indices:
            try:
                cursor.execute(idx)
                pg_conn.commit()
            except Exception as e:
                print(f"    [AVISO] Erro ao criar índice: {e}")
    
    print("    [OK] Índices criados!")

def main():
    print("=" * 60)
    print("MIGRAÇÃO SQLite -> PostgreSQL/Supabase")
    print("=" * 60)
    
    try:
        # Conectar aos bancos
        print("\nConectando aos bancos de dados...")
        sqlite_conn = conectar_sqlite()
        pg_conn = conectar_postgres()
        print("    [OK] Conectado!")
        
        # Criar tabelas
        criar_tabelas_postgres(pg_conn)
        
        # Migrar dados
        print("\n[2/5] Migrando CNAEs...")
        migrar_tabela(sqlite_conn, pg_conn, 'cnaes', ['codigo', 'descricao'])
        
        print("\n[3/5] Migrando Empresas...")
        migrar_tabela(sqlite_conn, pg_conn, 'empresas', 
                     ['cnpj basico', 'razao social', 'natureza juridica', 
                      'qualificacao responsavel', 'capital social', 
                      'porte empresa', 'ente federativo responsavel'])
        
        print("\n[4/5] Migrando Estabelecimentos...")
        migrar_tabela(sqlite_conn, pg_conn, 'estabelecimentos',
                     ['cnpj basico', 'cnpj_ordem', 'cnpj_dv', 
                      'identificador matriz filial', 'nome fantasia',
                      'situacao cadastral', 'data situacao cadastral',
                      'municipio', 'bairro', 'logradouro', 'numero',
                      'complemento', 'cep', 'uf', 'cnae_fiscal_principal',
                      'cnae_fiscal_secundaria'])
        
        # Criar índices
        criar_indices(pg_conn)
        
        print("\n" + "=" * 60)
        print("MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n[ERRO FATAL] {e}")
        sys.exit(1)
    finally:
        if 'sqlite_conn' in locals():
            sqlite_conn.close()
        if 'pg_conn' in locals():
            pg_conn.close()

if __name__ == '__main__':
    print("\n[!] AVISO: Este processo pode levar HORAS devido ao volume de dados.")
    print("[!] Recomenda-se executar em horário que não precise do computador.\n")
    
    resposta = input("Deseja continuar? (s/n): ")
    if resposta.lower() == 's':
        main()
    else:
        print("Migração cancelada.")

