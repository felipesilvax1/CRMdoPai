import sqlite3
import os

NOME_BD = 'CNPJ_Processado.db'

def diagnostico_completo():
    if not os.path.exists(NOME_BD):
        print(f"Erro: O banco de dados '{NOME_BD}' não foi encontrado.")
        return

    print(f"--- Iniciando Diagnóstico Completo do BD: '{NOME_BD}' ---")
    conn = sqlite3.connect(NOME_BD)
    cursor = conn.cursor()

    try:
        # --- Verificando a Tabela 'estabelecimentos' ---
        print("\n[TESTE 1] Verificando a tabela 'estabelecimentos' (endereço, telefone, status)...")
        cursor.execute("SELECT * FROM estabelecimentos LIMIT 1;")
        colunas_est = [description[0] for description in cursor.description]
        primeiro_estabelecimento = cursor.fetchone()

        if primeiro_estabelecimento:
            print("  - SUCESSO: Tabela 'estabelecimentos' encontrada.")
            print(f"  - Colunas encontradas: {', '.join(colunas_est)}")
            print("\n  - Exemplo de dados de um estabelecimento:")
            for col, val in zip(colunas_est, primeiro_estabelecimento):
                if val: # Mostra apenas campos preenchidos
                    print(f"    - {col}: {val}")
        else:
            print("  - FALHA: Tabela 'estabelecimentos' está vazia ou não existe.")

        # --- Verificando a Tabela 'socios' ---
        print("\n[TESTE 2] Verificando a tabela 'socios'...")
        cursor.execute("SELECT * FROM socios LIMIT 1;")
        colunas_soc = [description[0] for description in cursor.description]
        primeiro_socio = cursor.fetchone()

        if primeiro_socio:
            print("  - SUCESSO: Tabela 'socios' encontrada.")
            print(f"  - Colunas encontradas: {', '.join(colunas_soc)}")
            print("\n  - Exemplo de dados de um sócio:")
            for col, val in zip(colunas_soc, primeiro_socio):
                 if val: # Mostra apenas campos preenchidos
                    print(f"    - {col}: {val}")
        else:
            print("  - FALHA: Tabela 'socios' está vazia ou não existe.")

        # --- Diagnóstico de Performance ---
        print("\n[TESTE 3] Analisando o plano de execução da sua busca atual...")
        termo_lento = '%MIDOTTI%'
        query_lenta = f"EXPLAIN QUERY PLAN SELECT razao_social FROM empresas WHERE razao_social LIKE '{termo_lento}'"
        plano_lento = cursor.execute(query_lenta).fetchone()
        
        print(f"  - Plano para a busca `LIKE '{termo_lento}'`: {plano_lento[3]}")
        if "SCAN" in plano_lento[3]:
            print("  - DIAGNÓSTICO: A busca está lenta porque o banco precisa ler a tabela inteira (TABLE SCAN). O índice não é usado quando a busca começa com '%'.")

    except sqlite3.Error as e:
        print(f"\nOcorreu um erro de SQL: {e}")
    finally:
        conn.close()
        print("\n--- Diagnóstico Concluído ---")

if __name__ == '__main__':
    diagnostico_completo()
