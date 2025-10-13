import sqlite3
import os
import time

NOME_BD = 'CNPJ_Processado.db'

def limpar_dados():
    if not os.path.exists(NOME_BD):
        print(f"Erro: O banco de dados '{NOME_BD}' não foi encontrado.")
        return

    print(f"Abrindo '{NOME_BD}' para limpeza de dados (TRIM)...")
    conn = sqlite3.connect(NOME_BD)
    cursor = conn.cursor()
    
    start_time_total = time.time()

    try:
        print("\n--- Limpando a tabela 'empresas' ---")
        print("Removendo espaços extras da coluna 'razao_social'. Isso pode levar vários minutos...")
        start_time = time.time()
        cursor.execute('UPDATE empresas SET razao_social = TRIM(razao_social);')
        conn.commit()
        end_time = time.time()
        print(f"  - Limpeza da tabela 'empresas' concluída em {end_time - start_time:.2f} segundos.")
        
        print("\n--- Limpando a tabela 'estabelecimentos' ---")
        print("Removendo espaços extras da coluna 'nome_fantasia'. Isso também pode demorar...")
        start_time = time.time()
        cursor.execute('UPDATE estabelecimentos SET nome_fantasia = TRIM(nome_fantasia);')
        conn.commit()
        end_time = time.time()
        print(f"  - Limpeza da tabela 'estabelecimentos' concluída em {end_time - start_time:.2f} segundos.")
        
        end_time_total = time.time()
        print("\n--- SUCESSO! ---")
        print(f"A limpeza dos dados foi concluída com sucesso.")
        print(f"Tempo total de execução: {end_time_total - start_time_total:.2f} segundos.")
        print("\nAs buscas exatas agora utilizarão 100% do potencial dos índices.")

    except sqlite3.Error as e:
        print(f"\nOcorreu um erro de SQL: {e}")
    finally:
        conn.close()


if __name__ == '__main__':
    limpar_dados()
