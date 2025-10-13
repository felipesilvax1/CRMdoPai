import pandas as pd
from sqlalchemy import create_engine
import sqlite3
import time

# --- CONFIGURAÇÕES ---
# O caminho para o seu banco de dados SQLite
CAMINHO_SQLITE = r'C:\Users\PwC\Documents\CRM\CNPJ_Processado.db'

# A senha que você definiu para o superusuário 'postgres'
SENHA_POSTGRES = 'password' 

# TAMANHO DO PEDAÇO (CHUNK)
# Quantas linhas ler do SQLite e escrever no PostgreSQL por vez.
# 50.000 é um bom número para equilibrar performance e uso de memória.
TAMANHO_CHUNK = 50000

# --- FIM DAS CONFIGURAÇÕES ---

def migrar_dados_com_chunks():
    """
    Script para migrar todas as tabelas de SQLite para PostgreSQL
    usando chunks para manter o uso de memória baixo e estável.
    """
    print("--- Iniciando Migração Robusta com Chunks ---")
    
    # 1. Configurar as conexões
    try:
        conn_sqlite = sqlite3.connect(CAMINHO_SQLITE)
        engine_postgres = create_engine(f'postgresql://postgres:{SENHA_POSTGRES}@localhost:5432/prospeccao_br')
        print("Conexões com os bancos de dados estabelecidas.")
    except Exception as e:
        print(f"Erro ao conectar aos bancos de dados: {e}")
        return

    # 2. Pegar o nome de todas as tabelas do SQLite
    try:
        cursor = conn_sqlite.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tabelas = [row[0] for row in cursor.fetchall()]
        cursor.close()
        print(f"Tabelas encontradas no SQLite: {tabelas}")
    except Exception as e:
        print(f"Erro ao listar as tabelas do SQLite: {e}")
        conn_sqlite.close()
        return

    # 3. Loop para migrar cada tabela
    tempo_total_inicio = time.time()
    for tabela_nome in tabelas:
        tempo_tabela_inicio = time.time()
        print(f"\nIniciando migração da tabela: '{tabela_nome}'...")
        
        try:
            # Cria um 'iterador' que vai ler o SQLite em pedaços (chunks)
            chunk_iterator = pd.read_sql_query(f'SELECT * FROM "{tabela_nome}"', conn_sqlite, chunksize=TAMANHO_CHUNK)
            
            is_first_chunk = True
            chunk_num = 1
            total_linhas = 0

            # Loop através dos pedaços
            for chunk_df in chunk_iterator:
                total_linhas += len(chunk_df)
                print(f"  - Processando chunk {chunk_num} ({len(chunk_df)} linhas)...")
                
                # Para o primeiro chunk, ele CRIA a tabela no Postgres.
                # Para os chunks seguintes, ele APENAS ADICIONA os dados (append).
                if is_first_chunk:
                    chunk_df.to_sql(tabela_nome, engine_postgres, if_exists='replace', index=False, method='multi')
                    is_first_chunk = False
                else:
                    chunk_df.to_sql(tabela_nome, engine_postgres, if_exists='append', index=False, method='multi')
                
                chunk_num += 1

            tempo_tabela_fim = time.time()
            print(f"  [SUCESSO] Tabela '{tabela_nome}' ({total_linhas} linhas) migrada com sucesso em {tempo_tabela_fim - tempo_tabela_inicio:.2f} segundos.")

        except Exception as e:
            print(f"  [ERRO] Falha ao migrar a tabela '{tabela_nome}': {e}")

    conn_sqlite.close()
    tempo_total_fim = time.time()
    print(f"\n--- Migração de todas as tabelas concluída em {tempo_total_fim - tempo_total_inicio:.2f} segundos! ---")

if __name__ == '__main__':
    migrar_dados_com_chunks()