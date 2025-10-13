import os
import zipfile
import sqlite3
import time
import multiprocessing as mp
import csv
import shutil

# --- CONFIGURAÇÕES GLOBAIS ---
PASTA_RAIZ_DADOS = 'Dados Abertos CNPJ'
PASTA_PROCESSADOS = os.path.join(PASTA_RAIZ_DADOS, 'Processados')
NOME_BD = 'CNPJ_Processado.db'
LOCAL_APP_WEB = os.path.join('C:', os.sep, 'xampp', 'htdocs', 'crm_docs')
TAMANHO_LOTE = 50000

# --- LAYOUT COMPLETO DO BANCO DE DADOS ---
LAYOUTS = {
    'empresas': {'prefixo_arquivo': 'Empresas', 'colunas': ['cnpj_basico', 'razao_social', 'natureza_juridica', 'qualificacao_responsavel', 'capital_social', 'porte_empresa', 'ente_federativo_responsavel']},
    'estabelecimentos': {'prefixo_arquivo': 'Estabelecimentos', 'colunas': ['cnpj_basico', 'cnpj_ordem', 'cnpj_dv', 'identificador_matriz_filial', 'nome_fantasia', 'situacao_cadastral', 'data_situacao_cadastral', 'motivo_situacao_cadastral', 'nome_cidade_exterior', 'pais', 'data_inicio_atividade', 'cnae_fiscal_principal', 'cnae_fiscal_secundaria', 'tipo_logradouro', 'logradouro', 'numero', 'complemento', 'bairro', 'cep', 'uf', 'municipio', 'ddd_1', 'telefone_1', 'ddd_2', 'telefone_2', 'ddd_fax', 'fax', 'correio_eletronico', 'situacao_especial', 'data_situacao_especial']},
    'socios': {'prefixo_arquivo': 'Socios', 'colunas': ['cnpj_basico', 'identificador_socio', 'nome_socio', 'cpf_cnpj_socio', 'qualificacao_socio', 'data_entrada_sociedade', 'pais', 'representante_legal', 'nome_representante', 'qualificacao_representante_legal', 'faixa_etaria']},
    'simples': {'prefixo_arquivo': 'Simples', 'colunas': ['cnpj_basico', 'opcao_pelo_simples', 'data_opcao_simples', 'data_exclusao_simples', 'opcao_pelo_mei', 'data_opcao_mei', 'data_exclusao_mei']},
    'cnaes': {'prefixo_arquivo': 'Cnaes', 'colunas': ['codigo', 'descricao']},
    'municipios': {'prefixo_arquivo': 'Municipios', 'colunas': ['codigo', 'descricao']},
    'naturezas': {'prefixo_arquivo': 'Naturezas', 'colunas': ['codigo', 'descricao']},
    'qualificacoes': {'prefixo_arquivo': 'Qualificacoes', 'colunas': ['codigo', 'descricao']},
    'paises': {'prefixo_arquivo': 'Paises', 'colunas': ['codigo', 'descricao']},
    'motivos': {'prefixo_arquivo': 'Motivos', 'colunas': ['codigo', 'descricao']}
}

def criar_tabelas(conexao):
    cursor = conexao.cursor()
    for nome_tabela, definicao in LAYOUTS.items():
        colunas_sql = ', '.join([f'"{nome}" TEXT' for nome in definicao['colunas']])
        cursor.execute(f'CREATE TABLE IF NOT EXISTS {nome_tabela} ({colunas_sql})')
    conexao.commit()

def worker(arquivos_para_processar, fila_de_dados):
    
    def generate_cleaned_lines(f_bytes):
        for line_bytes in f_bytes:
            try:
                yield line_bytes.replace(b'\x00', b'').decode('latin1')
            except UnicodeDecodeError:
                continue

    for caminho_zip in arquivos_para_processar:
        nome_base_arquivo = os.path.basename(caminho_zip)
        tipo_tabela = None
        for nome, definicao in LAYOUTS.items():
            if nome_base_arquivo.lower().startswith(definicao['prefixo_arquivo'].lower()):
                tipo_tabela = nome
                break
        if not tipo_tabela: continue
        
        try:
            with zipfile.ZipFile(caminho_zip, 'r') as zf:
                nome_arquivo_interno = zf.namelist()[0]
                with zf.open(nome_arquivo_interno, 'r') as f_bytes:
                    
                    cleaned_lines_generator = generate_cleaned_lines(f_bytes)
                    reader = csv.reader(cleaned_lines_generator, delimiter=';')
                    
                    lote_linhas = []
                    for linha in reader:
                        lote_linhas.append(tuple(linha))
                        if len(lote_linhas) >= TAMANHO_LOTE:
                            fila_de_dados.put((tipo_tabela, lote_linhas))
                            lote_linhas = []
                    
                    if lote_linhas:
                        fila_de_dados.put((tipo_tabela, lote_linhas))
            
            fila_de_dados.put(("FILE_DONE", caminho_zip))
            print(f"Arquivo {nome_base_arquivo} processado com sucesso.")
        except Exception as e:
            print(f"Erro crítico ao processar {nome_base_arquivo}: {e}")
            fila_de_dados.put(("FILE_ERROR", caminho_zip))

def main():
    start_time_total = time.time()
    os.makedirs(PASTA_PROCESSADOS, exist_ok=True)
    
    print(f"--- [ETAPA 1/4] Iniciando/Continuando a criação do banco de dados '{NOME_BD}' ---")
    
    conn = sqlite3.connect(NOME_BD)
    criar_tabelas(conn)
    conn.execute('PRAGMA journal_mode = WAL;')
    conn.execute('PRAGMA synchronous = NORMAL;')
    cursor = conn.cursor()

    zips_a_processar = [os.path.join(PASTA_RAIZ_DADOS, f) for f in os.listdir(PASTA_RAIZ_DADOS) if f.lower().endswith('.zip')]
    if not zips_a_processar:
        print("Nenhum arquivo novo para processar. Pulando para as etapas de otimização.")
    else:
        num_processos = max(1, mp.cpu_count() - 1)
        print(f"Encontrados {len(zips_a_processar)} arquivos. Processando com {num_processos} núcleos...")
        
        # --- A CORREÇÃO ESTÁ AQUI: Limitando o tamanho da fila ---
        # A fila agora só pode conter 100 "pedaços" no máximo.
        fila_de_dados = mp.Queue(maxsize=100)
        # --- FIM DA CORREÇÃO ---

        arquivos_por_processo = [zips_a_processar[i::num_processos] for i in range(num_processos)]
        processos = [mp.Process(target=worker, args=(arquivos, fila_de_dados)) for arquivos in arquivos_por_processo]
        for p in processos: p.start()

        arquivos_em_progresso = len(zips_a_processar)
        while arquivos_em_progresso > 0:
            try:
                tipo, dados = fila_de_dados.get(timeout=120)
                if tipo == "FILE_DONE":
                    os.rename(dados, os.path.join(PASTA_PROCESSADOS, os.path.basename(dados)))
                    arquivos_em_progresso -= 1
                elif tipo == "FILE_ERROR":
                     arquivos_em_progresso -= 1
                else:
                    tipo_tabela, lote_linhas = tipo, dados
                    num_colunas_esperado = len(LAYOUTS[tipo_tabela]['colunas'])
                    lote_filtrado = [tuple(linha[:num_colunas_esperado]) for linha in lote_linhas if len(linha) >= num_colunas_esperado]
                    if lote_filtrado:
                        placeholders = ', '.join(['?'] * num_colunas_esperado)
                        sql_insert = f'INSERT INTO {tipo_tabela} VALUES ({placeholders})'
                        cursor.executemany(sql_insert, lote_filtrado)
                        conn.commit()
            except mp.queues.Empty:
                print("Fila vazia por muito tempo, processo de importação terminou ou travou.")
                break

        for p in processos: p.join()
    print("--- [ETAPA 1/4] Criação do banco de dados concluída. ---\n")

    print(f"--- [ETAPA 2/4] Limpando dados (TRIM) ---")
    cursor.execute('UPDATE empresas SET razao_social = TRIM(razao_social);')
    cursor.execute('UPDATE estabelecimentos SET nome_fantasia = TRIM(nome_fantasia);')
    conn.commit()
    print("--- [ETAPA 2/4] Limpeza de dados concluída. ---\n")

    print(f"--- [ETAPA 3/4] Criando índices de performance ---")
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_empresas_cnpj_basico ON empresas(cnpj_basico);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_empresas_razao_social ON empresas(razao_social COLLATE NOCASE);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_estabelecimentos_cnpj_basico ON estabelecimentos(cnpj_basico);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_estabelecimentos_nome_fantasia ON estabelecimentos(nome_fantasia COLLATE NOCASE);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_socios_cnpj_basico ON socios(cnpj_basico);')
    conn.commit()
    print("--- [ETAPA 3/4] Criação de índices concluída. ---\n")

    conn.close()

    print(f"--- [ETAPA 4/4] Copiando banco de dados final para a aplicação web ---")
    try:
        shutil.copy(NOME_BD, LOCAL_APP_WEB)
        print(f"  - SUCESSO! Banco de dados '{os.path.join(LOCAL_APP_WEB, NOME_BD)}' foi atualizado.")
    except Exception as e:
        print(f"  - ERRO: Não foi possível copiar o arquivo. Por favor, copie manualmente. Erro: {e}")

    end_time_total = time.time()
    print(f"\n--- ATUALIZAÇÃO COMPLETA CONCLUÍDA ---")
    print(f"Tempo total do processo: {(end_time_total - start_time_total) / 60:.2f} minutos.")

if __name__ == '__main__':
    mp.freeze_support()
    main()

