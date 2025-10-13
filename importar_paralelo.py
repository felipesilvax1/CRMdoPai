# -*- coding: utf-8 -*-
"""
Importação PARALELA e OTIMIZADA do PostgreSQL remoto
Usa múltiplos cores do Xeon para acelerar
"""
import subprocess
import os
import sqlite3
import psycopg2
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Configurações
REMOTE_HOST = "192.168.15.24"
REMOTE_DB = "cnpj_processed"
LOCAL_CONTAINER = "cnpj_postgres_final"
LOCAL_DB = "cnpj_processed"
USER = "postgres"
PASSWORD = "password"
SQLITE_PATH = "C:/Users/PwC/Documents/CRM/CNPJ_Processado.db"

# Número de workers paralelos (use metade dos cores)
import multiprocessing
NUM_WORKERS = max(4, multiprocessing.cpu_count() // 2)

print(f"\n{'='*70}")
print(f"IMPORTAÇÃO PARALELA - Usando {NUM_WORKERS} threads")
print(f"{'='*70}\n")

def copiar_tabela_direta(tabela):
    """Copia uma tabela diretamente via SQL COPY (muito mais rápido)"""
    inicio = time.time()
    print(f"[{tabela}] Iniciando cópia...")
    
    try:
        # 1. Exportar da origem via COPY TO
        dump_file = f"dump_{tabela}.csv"
        cmd_export = f'''docker run --rm -e PGPASSWORD={PASSWORD} postgres:15 psql -h {REMOTE_HOST} -U {USER} -d {REMOTE_DB} -c "\\COPY {tabela} TO STDOUT WITH (FORMAT CSV, HEADER)" > {dump_file}'''
        
        result = subprocess.run(cmd_export, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[{tabela}] ERRO ao exportar: {result.stderr}")
            return False, 0
        
        tamanho_mb = os.path.getsize(dump_file) / (1024*1024)
        print(f"[{tabela}] Exportado: {tamanho_mb:.1f} MB")
        
        # 2. Importar no destino via COPY FROM
        cmd_import = f'''docker exec -i {LOCAL_CONTAINER} psql -U {USER} -d {LOCAL_DB} -c "\\COPY {tabela} FROM STDIN WITH (FORMAT CSV, HEADER)" < {dump_file}'''
        
        result = subprocess.run(cmd_import, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[{tabela}] ERRO ao importar: {result.stderr}")
            return False, 0
        
        # 3. Contar registros
        cmd_count = f'docker exec {LOCAL_CONTAINER} psql -U {USER} -d {LOCAL_DB} -t -c "SELECT COUNT(*) FROM {tabela};"'
        result = subprocess.run(cmd_count, shell=True, capture_output=True, text=True)
        count = int(result.stdout.strip())
        
        tempo = time.time() - inicio
        print(f"[{tabela}] CONCLUÍDO: {count:,} registros em {tempo:.1f}s")
        
        # Limpar arquivo temporário
        os.remove(dump_file)
        
        return True, count
        
    except Exception as e:
        print(f"[{tabela}] EXCEÇÃO: {str(e)}")
        return False, 0

def preparar_banco_local():
    """Prepara o banco de dados local"""
    print("\n[PREPARAÇÃO] Criando estrutura no banco local...")
    
    # Criar banco
    cmd = f'docker exec {LOCAL_CONTAINER} psql -U {USER} -c "DROP DATABASE IF EXISTS {LOCAL_DB};"'
    subprocess.run(cmd, shell=True, capture_output=True)
    
    cmd = f'docker exec {LOCAL_CONTAINER} psql -U {USER} -c "CREATE DATABASE {LOCAL_DB};"'
    subprocess.run(cmd, shell=True, capture_output=True)
    
    # Copiar apenas o schema (DDL) do banco remoto
    print("[PREPARAÇÃO] Copiando estrutura das tabelas...")
    cmd = f'docker run --rm -e PGPASSWORD={PASSWORD} postgres:15 pg_dump -h {REMOTE_HOST} -U {USER} -d {REMOTE_DB} --schema-only | docker exec -i {LOCAL_CONTAINER} psql -U {USER} -d {LOCAL_DB}'
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERRO ao copiar schema: {result.stderr}")
        return False
    
    print("[PREPARAÇÃO] Estrutura criada com sucesso!")
    return True

def validar_com_sqlite():
    """Valida dados comparando PostgreSQL com SQLite original"""
    print(f"\n{'='*70}")
    print("VALIDAÇÃO: Comparando PostgreSQL vs SQLite")
    print(f"{'='*70}\n")
    
    tabelas = ['empresas', 'estabelecimentos', 'socios', 'cnaes']
    
    # Conectar ao SQLite
    sqlite_conn = sqlite3.connect(SQLITE_PATH)
    sqlite_cursor = sqlite_conn.cursor()
    
    # Conectar ao PostgreSQL local
    pg_conn = psycopg2.connect(
        host='localhost',
        port=5432,
        database=LOCAL_DB,
        user=USER,
        password=PASSWORD
    )
    pg_cursor = pg_conn.cursor()
    
    print(f"{'Tabela':<20} {'SQLite':>15} {'PostgreSQL':>15} {'Status':>10}")
    print("-" * 65)
    
    tudo_ok = True
    
    for tabela in tabelas:
        try:
            # Contar no SQLite
            sqlite_cursor.execute(f'SELECT COUNT(*) FROM "{tabela}"')
            count_sqlite = sqlite_cursor.fetchone()[0]
            
            # Contar no PostgreSQL
            pg_cursor.execute(f'SELECT COUNT(*) FROM {tabela}')
            count_pg = pg_cursor.fetchone()[0]
            
            diferenca = abs(count_sqlite - count_pg)
            status = "✓ OK" if diferenca == 0 else f"✗ DIFF {diferenca:,}"
            
            if diferenca > 0:
                tudo_ok = False
            
            print(f"{tabela:<20} {count_sqlite:>15,} {count_pg:>15,} {status:>10}")
            
        except Exception as e:
            print(f"{tabela:<20} {'ERRO':>15} {'ERRO':>15} {'✗ ERRO':>10}")
            print(f"   Detalhes: {str(e)}")
            tudo_ok = False
    
    sqlite_conn.close()
    pg_conn.close()
    
    return tudo_ok

def main():
    """Execução principal"""
    inicio_total = time.time()
    
    # 1. Preparar banco local
    if not preparar_banco_local():
        print("\n[ERRO] Falha ao preparar banco local!")
        return
    
    # 2. Lista de tabelas para copiar (ordenadas por tamanho - maiores primeiro)
    tabelas = [
        'estabelecimentos',  # 79M registros
        'empresas',          # 77M registros  
        'socios',            # 26M registros
        'simples',
        'municipios',
        'naturezas',
        'paises',
        'motivos',
        'qualificacoes',
        'cnaes'              # 2.7K registros
    ]
    
    print(f"\n{'='*70}")
    print(f"COPIANDO {len(tabelas)} TABELAS EM PARALELO")
    print(f"{'='*70}\n")
    
    # 3. Copiar tabelas em paralelo
    resultados = {}
    
    with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        futures = {executor.submit(copiar_tabela_direta, tabela): tabela for tabela in tabelas}
        
        for future in as_completed(futures):
            tabela = futures[future]
            try:
                sucesso, count = future.result()
                resultados[tabela] = (sucesso, count)
            except Exception as e:
                print(f"[{tabela}] EXCEÇÃO: {str(e)}")
                resultados[tabela] = (False, 0)
    
    # 4. Resumo
    tempo_total = time.time() - inicio_total
    
    print(f"\n{'='*70}")
    print("RESUMO DA IMPORTAÇÃO")
    print(f"{'='*70}\n")
    print(f"Tempo total: {tempo_total/60:.1f} minutos")
    print(f"Tabelas processadas: {len(resultados)}")
    print(f"Sucesso: {sum(1 for s, _ in resultados.values() if s)}")
    print(f"Falhas: {sum(1 for s, _ in resultados.values() if not s)}")
    
    # 5. Validar com SQLite
    if validar_com_sqlite():
        print(f"\n{'='*70}")
        print("✓ VALIDAÇÃO CONCLUÍDA: DADOS ÍNTEGROS!")
        print(f"{'='*70}\n")
    else:
        print(f"\n{'='*70}")
        print("✗ VALIDAÇÃO: ENCONTRADAS DIFERENÇAS!")
        print(f"{'='*70}\n")

if __name__ == '__main__':
    print("\n[INFO] Este método usa COPY direto - muito mais rápido!")
    print("[INFO] Vai usar todos os cores disponíveis do seu Xeon")
    print()
    
    main()

