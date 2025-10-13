import os
import zipfile
import sqlite3
import time
import multiprocessing as mp
import csv

# --- CONFIGURAÇÕES E LAYOUTS (sem alteração) ---
PASTA_RAIZ_DADOS = 'Dados Abertos CNPJ'
PASTA_PROCESSADOS = os.path.join(PASTA_RAIZ_DADOS, 'Processados')
NOME_BD = 'CNPJ_Processado.db'
TAMANHO_LOTE = 50000

COLUNAS_EMPRESAS = ['cnpj_basico', 'razao_social', 'natureza_juridica', 'qualificacao_responsavel', 'capital_social', 'porte_empresa', 'ente_federativo_responsavel']
COLUNAS_ESTABELECIMENTOS = ['cnpj_basico', 'cnpj_ordem', 'cnpj_dv', 'identificador_matriz_filial', 'nome_fantasia', 'situacao_cadastral', 'data_situacao_cadastral', 'motivo_situacao_cadastral', 'nome_cidade_exterior', 'pais', 'data_inicio_atividade', 'cnae_fiscal_principal', 'cnae_fiscal_secundaria', 'tipo_logradouro', 'logradouro', 'numero', 'complemento', 'bairro', 'cep', 'uf', 'municipio', 'ddd_1', 'telefone_1', 'ddd_2', 'telefone_2', 'ddd_fax', 'fax', 'correio_eletronico', 'situacao_especial', 'data_situacao_especial']
COLUNAS_SOCIOS = ['cnpj_basico', 'identificador_socio', 'nome_socio', 'cpf_cnpj_socio', 'qualificacao_socio', 'data_entrada_sociedade', 'pais', 'representante_legal', 'nome_representante', 'qualificacao_representante_legal', 'faixa_etaria']

LAYOUTS = {
    'empresas': {'prefixo_arquivo': 'Empresas', 'colunas': COLUNAS_EMPRESAS},
    'estabelecimentos': {'prefixo_arquivo': 'Estabelecimentos', 'colunas': COLUNAS_ESTABELECIMENTOS},
    'socios': {'prefixo_arquivo': 'Socios', 'colunas': COLUNAS_SOCIOS}
}

def criar_tabelas(conexao):
    cursor = conexao.cursor()
    for nome_tabela, definicao in LAYOUTS.items():
        colunas_sql = ', '.join([f'"{nome}" TEXT' for nome in definicao['colunas']])
        cursor.execute(f'CREATE TABLE IF NOT EXISTS {nome_tabela} ({colunas_sql})')
    conexao.commit()

def worker(arquivos_para_processar, fila_de_dados):
    for caminho_zip in arquivos_para_processar:
        nome_base_arquivo = os.path.basename(caminho_zip)
        tipo_tabela = None
        for nome, definicao in LAYOUTS.items():
            if nome_base_arquivo.startswith(definicao['prefixo_arquivo']):
                tipo_tabela = nome
                break
        if not tipo_tabela: continue
        
        try:
            with zipfile.ZipFile(caminho_zip, 'r') as zf:
                nome_arquivo_interno = zf.namelist()[0]
                with zf.open(nome_arquivo_interno, 'r') as f_bytes:
                    import io
                    f_text = io.TextIOWrapper(f_bytes, encoding='latin1')
                    reader = csv.reader(f_text, delimiter=';')
                    
                    lote_linhas = []
                    for linha in reader:
                        lote_linhas.append(tuple(linha))
                        if len(lote_linhas) >= TAMANHO_LOTE:
                            fila_de_dados.put((tipo_tabela, lote_linhas))
                            lote_linhas = []
                    if lote_linhas:
                        fila_de_dados.put((tipo_tabela, lote_linhas))
            
            fila_de_dados.put(("FILE_DONE", caminho_zip))
            print(f"Arquivo {nome_base_arquivo} lido com sucesso.")
        except Exception as e:
            print(f"Erro crítico ao processar {nome_base_arquivo}: {e}")
            fila_de_dados.put(("FILE_ERROR", caminho_zip))

def main():
    os.makedirs(PASTA_PROCESSADOS, exist_ok=True)

    # --- CORREÇÃO FINAL ESTÁ AQUI ---
    # Sempre criamos a conexão e as tabelas ANTES de qualquer outra coisa.
    conn = sqlite3.connect(NOME_BD)
    print(f"Verificando/Criando tabelas no banco de dados '{NOME_BD}'...")
    criar_tabelas(conn) # Garante que as tabelas existam
    # --- FIM DA CORREÇÃO ---
    
    conn.execute('PRAGMA journal_mode = WAL;')
    conn.execute('PRAGMA synchronous = NORMAL;')
    cursor = conn.cursor()

    zips_a_processar = [os.path.join(PASTA_RAIZ_DADOS, f) for f in os.listdir(PASTA_RAIZ_DADOS) if f.lower().endswith('.zip')]
    if not zips_a_processar:
        print("Nenhum arquivo novo para processar.")
        conn.close()
        return
    
    print(f"Encontrados {len(zips_a_processar)} arquivos para processar.")
    num_processos = max(1, mp.cpu_count() - 1)
    print(f"Iniciando/Continuando processamento com {num_processos} trabalhadores...")
    start_time_total = time.time()
    
    fila_de_dados = mp.Queue()
    arquivos_por_processo = [zips_a_processar[i::num_processos] for i in range(num_processos)]
    processos = [mp.Process(target=worker, args=(arquivos, fila_de_dados)) for arquivos in arquivos_por_processo]
    for p in processos: p.start()

    arquivos_em_progresso = len(zips_a_processar)
    total_linhas_inseridas = 0
    while arquivos_em_progresso > 0:
        try:
            tipo, dados = fila_de_dados.get(timeout=60)
            if tipo == "FILE_DONE":
                caminho_arquivo, nome_arquivo = dados, os.path.basename(dados)
                destino = os.path.join(PASTA_PROCESSADOS, nome_arquivo)
                os.rename(caminho_arquivo, destino)
                print(f"Arquivo {nome_arquivo} movido para 'Processados'.")
                arquivos_em_progresso -= 1
            elif tipo == "FILE_ERROR":
                 arquivos_em_progresso -= 1
                 print(f"Arquivo {os.path.basename(dados)} falhou.")
            else:
                tipo_tabela, lote_linhas = tipo, dados
                num_colunas_esperado = len(LAYOUTS[tipo_tabela]['colunas'])
                lote_filtrado = [tuple(linha[:num_colunas_esperado]) for linha in lote_linhas if len(linha) >= num_colunas_esperado]
                if lote_filtrado:
                    placeholders = ', '.join(['?'] * num_colunas_esperado)
                    sql_insert = f'INSERT INTO {tipo_tabela} VALUES ({placeholders})'
                    cursor.executemany(sql_insert, lote_filtrado)
                    conn.commit()
                    total_linhas_inseridas += len(lote_filtrado)
                    print(f"  - Inserido lote de {len(lote_filtrado):,} na tabela `{tipo_tabela}`. Total inserido nesta rodada: {total_linhas_inseridas:,}")
        except mp.queues.Empty:
            print("Fila vazia, processo terminou.")
            break

    for p in processos: p.join()
    
    end_time_total = time.time()
    print("\n--- Processo de Importação Concluído! ---")
    conn.close()

    print("\n--- Iniciando Criação do Índice de Busca ---")
    conn_idx = sqlite3.connect(NOME_BD)
    cursor_idx = conn_idx.cursor()
    print("Criando índice na coluna 'razao_social'. Isso pode levar alguns minutos...")
    cursor_idx.execute('CREATE INDEX IF NOT EXISTS idx_empresas_razao_social ON empresas(razao_social);')
    conn_idx.commit()
    conn_idx.close()
    print("--- Índice Criado com Sucesso! ---")


if __name__ == '__main__':
    mp.freeze_support()
    main()