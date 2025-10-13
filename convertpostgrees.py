import subprocess
import sys
import time
import os
import re

# --- CONFIGURAÇÕES GERAIS ---
# Nomes dos recursos a serem limpos
CONTAINERS_TO_CLEAN = ["cnpj_postgres_local", "cnpj_postgres_notebook"]
VOLUMES_TO_CLEAN = ["cnpj_postgres_data", "cnpj_postgres_data_local", "2025-08_postgres-data", "consulta-cnpj-local_postgres_data"]

# Conexão ao Servidor PostgreSQL Local
DB_HOST_LOCAL = "localhost"
DB_PORT_LOCAL = "5432"
DB_USER_LOCAL = "postgres"
DB_PASSWORD_LOCAL = "password" 
DB_NAME_TO_CLEAN = "db_processo_migrado"
DB_NAME_FINAL = "cnpj_dados_finais" # Novo nome para o banco de dados final

# --- FUNÇÕES AUXILIARES ---
def print_header(title):
    print("\n" + "="*70)
    print(f" {title.upper()} ".center(70, "="))
    print("="*70)

def run_command(command, description, can_fail=False, capture_output=True, env_overrides=None):
    print(f"-> {description}...")
    try:
        effective_env = os.environ.copy()
        if env_overrides:
            effective_env.update(env_overrides)
        
        # PGPASSWORD precisa ser setado para comandos psql/dropdb
        if DB_PASSWORD_LOCAL:
            effective_env["PGPASSWORD"] = DB_PASSWORD_LOCAL
            
        process = subprocess.run(
            command, capture_output=capture_output, text=True, encoding='utf-8',
            errors='replace', env=effective_env, shell=isinstance(command, str)
        )
        if process.returncode != 0 and not can_fail:
            print(f"\n[AVISO] O comando falhou (isso pode ser normal durante a limpeza).")
            print("--- MENSAGEM DE ERRO ---\n" + (process.stderr.strip() or process.stdout.strip()))
            print("------------------------")
            return None, None
        return process.stdout.strip(), process.stderr.strip()
    except FileNotFoundError:
        cmd_name = command[0] if isinstance(command, list) else command.split()[0]
        print(f"[ERRO FATAL] O comando '{cmd_name}' não foi encontrado.")
        return None, None

def get_user_confirmation(prompt):
    while True:
        choice = input(f"{prompt} (s/n): ").lower().strip()
        if choice in ['s', 'n']: return choice == 's'
        print("Resposta inválida.")

def find_postgres_bin_dir():
    print("-> Procurando pela instalação local do PostgreSQL...")
    base_path = os.environ.get("ProgramFiles", "C:\\Program Files")
    pg_dir = os.path.join(base_path, "PostgreSQL")
    
    if os.path.isdir(pg_dir):
        versions = sorted([d for d in os.listdir(pg_dir) if os.path.isdir(os.path.join(pg_dir, d)) and d.replace('.','').isdigit()], reverse=True)
        if versions:
            for version in versions:
                bin_path = os.path.join(pg_dir, version, "bin")
                if os.path.isdir(bin_path):
                    print(f"-> PostgreSQL encontrado em: {bin_path}")
                    return bin_path
    print("[AVISO] Não foi possível encontrar o diretório 'bin' do PostgreSQL automaticamente.")
    return None

# --- LÓGICA PRINCIPAL ---
def main():
    print_header("Script de Recomeço Total: Limpeza e Conversão")
    print("Este script irá APAGAR PERMANENTEMENTE todos os contêineres e volumes Docker")
    print("relacionados a esta migração, e também o banco de dados no seu PostgreSQL local.")

    if not get_user_confirmation("\nVocê tem certeza que deseja continuar com a limpeza total?"):
        print("Operação cancelada."); sys.exit(0)

    # --- FASE 1: LIMPEZA TOTAL ---
    print_header("Fase 1: Limpeza Total do Ambiente")
    
    # Limpar Contêineres
    for container in CONTAINERS_TO_CLEAN:
        run_command(["docker", "stop", container], f"Parando contêiner '{container}'", can_fail=True)
        run_command(["docker", "rm", container], f"Removendo contêiner '{container}'", can_fail=True)
    
    # Limpar Volumes
    for volume in VOLUMES_TO_CLEAN:
        run_command(["docker", "volume", "rm", volume], f"Removendo volume '{volume}'", can_fail=True)

    # Limpar Banco de Dados
    pg_bin_dir = find_postgres_bin_dir()
    if pg_bin_dir:
        dropdb_exe = os.path.join(pg_bin_dir, "dropdb.exe")
        run_command([dropdb_exe, "-h", DB_HOST_LOCAL, "-p", DB_PORT_LOCAL, "-U", DB_USER_LOCAL, "--if-exists", DB_NAME_TO_CLEAN], f"Apagando banco de dados '{DB_NAME_TO_CLEAN}'", can_fail=True)
        run_command([dropdb_exe, "-h", DB_HOST_LOCAL, "-p", DB_PORT_LOCAL, "-U", DB_USER_LOCAL, "--if-exists", DB_NAME_FINAL], f"Apagando banco de dados '{DB_NAME_FINAL}'", can_fail=True)

    print("\n-> Limpeza concluída.")

    # --- FASE 2: CONVERSÃO DIRETA DO SQLITE ---
    print_header("Fase 2: Conversão Direta de SQLite para PostgreSQL")
    
    sqlite_path = ""
    while not sqlite_path or not os.path.isfile(sqlite_path):
        sqlite_path = input("\nPor favor, arraste o seu arquivo de banco de dados SQLite para esta janela e pressione Enter,\nou digite o caminho completo para ele: ").strip().replace("'", "").replace("\"", "")
        if not os.path.isfile(sqlite_path):
            print("[ERRO] Arquivo não encontrado. Por favor, verifique o caminho e tente novamente.")

    print(f"-> Arquivo de origem: {sqlite_path}")

    # Monta o comando do pgloader via Docker
    # Mapeamos o diretório do arquivo SQLite para /data/ no contêiner
    sqlite_dir = os.path.dirname(sqlite_path)
    sqlite_filename = os.path.basename(sqlite_path)
    
    # URL de conexão para o PostgreSQL. `host.docker.internal` permite que o contêiner acesse o localhost do PC.
    postgres_url = f"postgresql://{DB_USER_LOCAL}:{DB_PASSWORD_LOCAL}@{DB_HOST_LOCAL}:{DB_PORT_LOCAL}/{DB_NAME_FINAL}"
    
    # Comando pgloader
    pgloader_command = [
        "docker", "run", "--rm", "-v", f"{sqlite_dir}:/data:ro", # :ro para apenas leitura
        "dimitri/pgloader:latest",
        "pgloader",
        f"sqlite:///data/{sqlite_filename}",
        postgres_url
    ]

    print("\n-> O pgloader irá primeiro criar o banco de dados de destino se ele não existir.")
    if pg_bin_dir:
         createdb_exe = os.path.join(pg_bin_dir, "createdb.exe")
         run_command([createdb_exe, "-h", DB_HOST_LOCAL, "-p", DB_PORT_LOCAL, "-U", DB_USER_LOCAL, DB_NAME_FINAL], f"Garantindo que o banco de dados '{DB_NAME_FINAL}' exista", can_fail=True)


    print_header("Estimativa de Tempo: 1 a 3 horas")
    print("A conversão de um banco de dados grande é um processo intensivo.")
    print("O terminal abaixo mostrará o progresso do pgloader.")
    print("Por favor, seja paciente e não interrompa o processo.")
    print("-" * 70)

    # Executa a conversão
    # Usamos Popen para ver a saída em tempo real
    process = subprocess.Popen(pgloader_command, text=True, encoding='utf-8', errors='replace')
    process.wait()

    print("-" * 70)
    if process.returncode != 0:
        print("[ERRO FATAL] A migração com o pgloader falhou. Verifique os logs acima.")
        sys.exit(1)
    
    print_header("Conversão Concluída com Sucesso!")
    print(f"Os dados do arquivo SQLite foram migrados com sucesso para o banco de dados '{DB_NAME_FINAL}' no seu PostgreSQL local.")
    print("Finalmente, missão cumprida!")

if __name__ == "__main__":
    main()
