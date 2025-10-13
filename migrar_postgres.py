import subprocess
import sys
import os
import json

# --- CONFIGURAÇÕES ---
# Conectando ao servidor PostgreSQL local
TARGET_HOST = "localhost"
TARGET_PORT = "5432"
TARGET_USER = "postgres"
TARGET_PASSWORD = "password" 
# Nome do banco de dados a ser criado no servidor local
DB_NAME_NO_SERVIDOR = "db_processo_migrado" 
# Nome do contêiner local que criamos, que contém os dados
CONTAINER_DE_ORIGEM = "cnpj_postgres_local" 

def run_docker_command(command, description, sensitive=False):
    """Executa um comando DENTRO do contêiner Docker e lida com a saída."""
    full_command = ["docker", "exec", "-i", CONTAINER_DE_ORIGEM] + command
    
    print(f"\n-> {description}...")
    if not sensitive:
        print(f"   Executando: {' '.join(full_command)}")
        
    try:
        process = subprocess.Popen(full_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='replace')
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            return stdout, stderr

        return stdout, None
    except FileNotFoundError:
        print("[ERRO FATAL] O comando 'docker' não foi encontrado. O Docker está em execução?")
        sys.exit(1)
    except Exception as e:
        print(f"[ERRO FATAL INESPERADO] {e}")
        sys.exit(1)

def check_container_running():
    """Verifica se o contêiner de origem está em execução."""
    print("--- PASSO PRELIMINAR: Verificando status do contêiner de origem ---")
    try:
        command = ["docker", "inspect", "--format", "{{.State.Running}}", CONTAINER_DE_ORIGEM]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        is_running = result.stdout.strip() == "true"
        
        if is_running:
            print(f"-> O contêiner '{CONTAINER_DE_ORIGEM}' está em execução. Tudo certo!")
            return True
        else:
            print(f"[ERRO FATAL] O contêiner '{CONTAINER_DE_ORIGEM}' não está em execução.")
            print("   Por favor, abra o Docker Desktop, vá para a aba 'Containers' e inicie-o antes de rodar este script.")
            return False
            
    except subprocess.CalledProcessError:
        print(f"[ERRO FATAL] O contêiner '{CONTAINER_DE_ORIGEM}' não foi encontrado.")
        print("   Verifique se ele foi criado corretamente.")
        return False
    except FileNotFoundError:
        print("[ERRO FATAL] O comando 'docker' não foi encontrado. O Docker está instalado e em execução?")
        return False

def discover_and_select_source_db():
    """Lista os bancos de dados dentro do contêiner e pede para o usuário escolher."""
    print("\n--- PASSO 1/5: Identificando o banco de dados de origem no contêiner ---")
    
    psql_command = ["psql", "-U", "postgres", "-l", "-t", "-A"]
    cut_command = ["cut", "-d", "|", "-f1"]

    try:
        psql_proc = subprocess.Popen(["docker", "exec", CONTAINER_DE_ORIGEM] + psql_command, stdout=subprocess.PIPE, text=True)
        cut_proc = subprocess.Popen(cut_command, stdin=psql_proc.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        psql_proc.stdout.close()
        stdout, stderr = cut_proc.communicate()

        if cut_proc.returncode != 0:
            print("[ERRO FATAL] Não foi possível listar os bancos de dados dentro do contêiner.")
            print(stderr)
            sys.exit(1)
            
    except FileNotFoundError:
        print("[ERRO FATAL] O comando 'docker' ou 'cut' (parte do Git Bash/WSL) não foi encontrado.")
        sys.exit(1)

    db_list = [db for db in stdout.strip().split('\n') if db and db not in ('template0', 'template1', 'postgres')]

    if not db_list:
        print("[AVISO] Nenhum banco de dados de usuário encontrado. Usando o banco 'postgres' por padrão (pode estar vazio).")
        return "postgres"

    print("Foram encontrados os seguintes bancos de dados no contêiner:")
    for i, db_name in enumerate(db_list):
        print(f"   [{i + 1}] {db_name}")

    while True:
        try:
            choice = int(input("\nPor favor, digite o NÚMERO do banco que deseja migrar: "))
            if 1 <= choice <= len(db_list):
                selected_db = db_list[choice - 1]
                print(f"   -> Você selecionou: '{selected_db}'")
                return selected_db
            else:
                print("   Opção inválida.")
        except ValueError:
            print("   Entrada inválida. Digite apenas o número.")


def main():
    """Função principal que orquestra a migração."""
    print("\n--- INICIANDO SCRIPT DE MIGRAÇÃO POSTGRESQL (Local) ---")
    
    if not check_container_running():
        sys.exit(1)
        
    os.environ['PGPASSWORD'] = TARGET_PASSWORD
    
    db_name_in_container = discover_and_select_source_db()

    print(f"\n--- PASSO 2/5: Verificando a conexão com o servidor PostgreSQL local ---")
    _, error = run_docker_command(["psql", "-h", TARGET_HOST, "-U", TARGET_USER, "-d", "postgres", "-c", "SELECT 1;"], "Testando conexão", sensitive=True)
    if error:
        print("[ERRO FATAL] Falha ao conectar no servidor de banco de dados local.")
        print(f"   Mensagem: {error}")
        sys.exit(1)
    print("-> Conexão bem-sucedida!")

    print(f"\n--- PASSO 3/5: Criando o banco de dados '{DB_NAME_NO_SERVIDOR}' no servidor local ---")
    _, error = run_docker_command(["createdb", "-h", TARGET_HOST, "-U", TARGET_USER, DB_NAME_NO_SERVIDOR], f"Criando banco '{DB_NAME_NO_SERVIDOR}'", sensitive=True)
    if error:
        if "já existe" in error or "already exists" in error:
            choice = input(f"-> AVISO: O banco de dados '{DB_NAME_NO_SERVIDOR}' já existe. Deseja continuar e restaurar os dados nele mesmo? (s/n): ").lower()
            if choice != 's':
                print("Operação cancelada.")
                sys.exit(0)
        else:
            print(f"[ERRO FATAL] Falha ao criar o banco de dados: {error}")
            sys.exit(1)
    else:
        print(f"-> Banco de dados '{DB_NAME_NO_SERVIDOR}' criado com sucesso!")

    print("\n--- PASSO 4/5: Iniciando a transferência de dados ---")
    print("Isso pode levar um tempo considerável!")

    dump_command = f"pg_dump -U postgres -d {db_name_in_container} -Fc"
    restore_command = f"pg_restore -h {TARGET_HOST} -U {TARGET_USER} -d {DB_NAME_NO_SERVIDOR} -v"
    full_command_str = f"docker exec -i {CONTAINER_DE_ORIGEM} bash -c '{dump_command}' | docker exec -i {CONTAINER_DE_ORIGEM} bash -c '{restore_command}'"
    
    print(f"   Executando o pipeline de migração...")
    
    try:
        process = subprocess.Popen(full_command_str, shell=True, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='replace')
        for line in iter(process.stderr.readline, ''):
            print(line, end='')
        process.wait()
        
        if process.returncode != 0:
            print(f"\n[ERRO] A restauração falhou com o código de saída: {process.returncode}")
            sys.exit(1)

    except Exception as e:
        print(f"\n[ERRO FATAL] Ocorreu um erro inesperado durante a migração: {e}")
        sys.exit(1)
        
    print("\n--- PASSO 5/5: Limpeza Final ---")
    
    del os.environ['PGPASSWORD']

    print("\n--------------------------------------------------")
    print("[SUCESSO] Migração concluída!")
    print(f"O banco de dados '{db_name_in_container}' foi restaurado como '{DB_NAME_NO_SERVIDOR}' no seu servidor local.")

if __name__ == "__main__":
    main()

