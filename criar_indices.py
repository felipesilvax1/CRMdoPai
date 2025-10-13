import sqlite3
import os
import time

NOME_BD = 'CNPJ_Processado.db'

def otimizar_busca_texto():
    if not os.path.exists(NOME_BD):
        print(f"Erro: O banco de dados '{NOME_BD}' não foi encontrado.")
        return

    print(f"Abrindo '{NOME_BD}' para otimizar os índices de busca por texto...")
    conn = sqlite3.connect(NOME_BD)
    cursor = conn.cursor()
    
    start_time = time.time()

    try:
        print("\n--- Otimizando a tabela 'empresas' ---")
        print("  - Removendo índice antigo de 'razao_social' (se existir)...")
        cursor.execute('DROP INDEX IF EXISTS idx_empresas_razao_social;')
        print("  - Criando novo índice case-insensitive (NOCASE)...")
        # A mágica está no 'COLLATE NOCASE', que torna o índice inteligente
        cursor.execute('CREATE INDEX idx_empresas_razao_social ON empresas(razao_social COLLATE NOCASE);')
        
        print("\n--- Otimizando a tabela 'estabelecimentos' ---")
        print("  - Removendo índice antigo de 'nome_fantasia' (se existir)...")
        cursor.execute('DROP INDEX IF EXISTS idx_estabelecimentos_nome_fantasia;')
        print("  - Criando novo índice case-insensitive (NOCASE)...")
        cursor.execute('CREATE INDEX idx_estabelecimentos_nome_fantasia ON estabelecimentos(nome_fantasia COLLATE NOCASE);')
        
        conn.commit()
        
        end_time = time.time()
        print("\n--- SUCESSO! ---")
        print(f"Índices de busca por texto foram otimizados com sucesso.")
        print(f"Tempo de execução: {end_time - start_time:.2f} segundos.")
        print("\nA busca exata por nome agora será instantânea.")

    except sqlite3.Error as e:
        print(f"\nOcorreu um erro de SQL: {e}")
    finally:
        conn.close()


if __name__ == '__main__':
    otimizar_busca_texto()
