import subprocess
import sys
import time
import os
import re

# --- CONFIGURAÇÕES GERAIS ---
# Nomes para os recursos locais que serão criados
LOCAL_CONTAINER_NAME = "cnpj_postgres_local"

# Conexão ao Servidor PostgreSQL Local (o destino final)
DB_HOST_LOCAL = "localhost"
DB_PORT_LOCAL = "5432"
DB_USER_LOCAL = "postgres"
DB_PASSWORD_LOCAL = "password" # Senha do seu PostgreSQL instalado no PC
DB_NAME_FINAL = "db_processo_migrado"

# --- FUNÇÕES AUXILIARES ---
def print_header(title):
    """Imprime um cabeçalho formatado."""
    print("\n" + "="*70)
    print(f" {title.upper()} ".center(70, "="))
    print("="*70)

def run_command(command, description, can_fail=False, capture_output=True, env_overrides=None):
    """Executa um comando no shell, com tratamento de erros e feedback."""
    print(f"-> {description}...")
    try:
        effective_env = os.environ.copy()
        if env_overrides:
            effective_env.update(env_overrides)
        
        effective_env["PGPASSWORD"] = DB_PASSWORD_LOCAL
            
        process = subprocess.run(
            command,
            capture_output=capture_output,
            text=True,
            encoding='utf-8',
            errors='replace',
            env=effective_env,
            shell=isinstance(command, str)
        )
        if process.returncode != 0 and not can_fail:
            print(f"\n[ERRO FATAL] O comando falhou.")
            print("--- MENSAGEM DE ERRO ---")
            print(process.stderr.strip() or process.stdout.strip())
            print("------------------------")
            return None, None
        return process.stdout.strip(), process.stderr.strip()
    except FileNotFoundError:
        cmd_name = command[0] if isinstance(command, list) else command.split()[0]
        print(f"[ERRO FATAL] O comando '{cmd_name}' não foi encontrado.")
        return None, None

def get_user_confirmation(prompt):
    """Pede confirmação (s/n) ao usuário."""
    while True:
        choice = input(f"{prompt} (s/n): ").lower().strip()
        if choice in ['s', 'n']:
            return choice == 's'
        print("Resposta inválida. Por favor, digite 's' para sim ou 'n' para não.")

def find_postgres_bin_dir():
    """Procura o diretório bin do PostgreSQL e retorna o caminho."""
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
    
    print("[ERRO FATAL] Não foi possível encontrar o diretório 'bin' do PostgreSQL automaticamente.")
    return None

# --- LÓGICA PRINCIPAL DO SCRIPT ---
def main():
    """Orquestra todo o processo de migração, do início ao fim."""
    
    print_header("Fase 1: Verificação do Ambiente Local")

    volumes_raw, _ = run_command(["docker", "volume", "ls", "--format", "{{.Name}}"], "Listando volumes")
    if volumes_raw is None: sys.exit(1)
    
    volume_options = []
    for vol_name in volumes_raw.splitlines():
        size_cmd = ["docker", "run", "--rm", "-v", f"{vol_name}:/data", "alpine", "du", "-sh", "/data"]
        size_raw, _ = run_command(size_cmd, f"Calculando tamanho de '{vol_name}'", can_fail=True)
        size = size_raw.split()[0] if size_raw else "0.0K"
        volume_options.append({"name": vol_name, "size": size})

    print("\nForam encontrados os seguintes volumes:")
    for i, vol in enumerate(volume_options):
        print(f"   [{i+1}] {vol['name']} ({vol['size']})")
    
    source_volume_name = ""
    while True:
        try:
            choice = int(input(f"\nPor favor, digite o NÚMERO do volume que contém os dados a serem migrados: "))
            if 1 <= choice <= len(volume_options):
                source_volume_name = volume_options[choice-1]['name']; break
            else: print("Número inválido.")
        except (ValueError, IndexError): print("Por favor, digite um número da lista.")
    print(f"-> Você selecionou: '{source_volume_name}'")

    print_header("Fase 2: Autodetecção, Reparo e Preparação do Contêiner")
    
    version_cmd = ["docker", "run", "--rm", "-v", f"{source_volume_name}:/data", "alpine", "cat", "/data/PG_VERSION"]
    version_str, _ = run_command(version_cmd, "Detectando a versão do PostgreSQL a partir dos dados")
    if not version_str or not version_str.strip().isdigit():
        print(f"[ERRO FATAL] Não foi possível determinar a versão do PostgreSQL a partir do volume '{source_volume_name}'."); sys.exit(1)
    
    pg_version = version_str.strip()
    source_container_image = f"postgres:{pg_version}"
    print(f"-> VERSÃO DETECTADA: {pg_version}. Usando a imagem Docker: '{source_container_image}'")

    run_command(["docker", "stop", LOCAL_CONTAINER_NAME], "Parando contêiner antigo (se existir)", can_fail=True)
    run_command(["docker", "rm", LOCAL_CONTAINER_NAME], "Removendo contêiner antigo (se existir)", can_fail=True)

    maint_container_name = f"{LOCAL_CONTAINER_NAME}-maint"
    run_command(["docker", "stop", maint_container_name], "Limpando contêiner de manutenção antigo", can_fail=True)
    run_command(["docker", "rm", maint_container_name], "Limpando contêiner de manutenção antigo", can_fail=True)

    maint_cmd = ["docker", "run", "-d", "--name", maint_container_name, "-v", f"{source_volume_name}:/var/lib/postgresql/data", source_container_image, "sleep", "infinity"]
    if run_command(maint_cmd, "Iniciando contêiner de manutenção")[0] is None: sys.exit(1)
    
    fix_perms_cmd = ["docker", "exec", maint_container_name, "chown", "-R", "postgres:postgres", "/var/lib/postgresql/data"]
    if run_command(fix_perms_cmd, "Corrigindo permissões dos arquivos")[0] is None: sys.exit(1)
    
    run_command(["docker", "stop", maint_container_name], "Parando contêiner de manutenção", can_fail=True)
    run_command(["docker", "rm", maint_container_name], "Removendo contêiner de manutenção", can_fail=True)

    final_container_cmd = ["docker", "run", "-d", "--name", LOCAL_CONTAINER_NAME, "-e", "POSTGRES_PASSWORD=password", "-e", "POSTGRES_USER=postgres", "-v", f"{source_volume_name}:/var/lib/postgresql/data", source_container_image]
    if run_command(final_container_cmd, f"Recriando contêiner final com a imagem '{source_container_image}'")[0] is None: sys.exit(1)

    print("-> Aguardando o PostgreSQL iniciar no contêiner...")
    time.sleep(25)

    status, _ = run_command(["docker", "ps", "-f", f"name={LOCAL_CONTAINER_NAME}", "-f", "status=running"], "Verificando saúde do contêiner", can_fail=True)
    if not status:
        print(f"[ERRO FATAL] O contêiner '{LOCAL_CONTAINER_NAME}' não conseguiu iniciar."); print(f"Verifique os logs manualmente com o comando: docker logs {LOCAL_CONTAINER_NAME}"); sys.exit(1)
    print("-> Contêiner está em execução e saudável!")

    print_header("Fase 3: Seleção do Banco de Dados de Origem")
    
    pg_bin_dir = find_postgres_bin_dir()
    if not pg_bin_dir: sys.exit(1)

    list_db_cmd = ["docker", "exec", LOCAL_CONTAINER_NAME, "psql", "-U", "postgres", "-lqtA"]
    db_list_raw, _ = run_command(list_db_cmd, "Listando bancos de dados no contêiner")
    if db_list_raw is None: sys.exit(1)
    
    all_dbs = [line.split('|')[0].strip() for line in db_list_raw.splitlines() if line.strip() and '|' in line]
    selectable_dbs = [db for db in all_dbs if db != 'template0']
    
    source_db_name = ""
    if not selectable_dbs: print("[ERRO FATAL] Nenhum banco de dados selecionável foi encontrado no contêiner."); sys.exit(1)
    elif len(selectable_dbs) == 1: source_db_name = selectable_dbs[0]; print(f"-> Banco de dados de origem único encontrado: '{source_db_name}'")
    else:
        print("\nForam encontrados os seguintes bancos de dados no contêiner:")
        for i, db_name in enumerate(selectable_dbs): print(f"   [{i+1}] {db_name}")
        while True:
            try:
                choice = int(input(f"\nPor favor, digite o NÚMERO do banco de dados que deseja migrar: "))
                if 1 <= choice <= len(selectable_dbs): source_db_name = selectable_dbs[choice-1]; break
                else: print("Número inválido.")
            except (ValueError, IndexError): print("Por favor, digite um número da lista.")
    print(f"-> Banco de dados de origem selecionado: '{source_db_name}'")

    print_header("Fase 4: Migração Final para o PostgreSQL Local (Otimizado)")

    # Limpeza segura do banco de dados de destino
    dropdb_exe = os.path.join(pg_bin_dir, "dropdb.exe")
    createdb_exe = os.path.join(pg_bin_dir, "createdb.exe")
    
    if get_user_confirmation(f"O script irá agora APAGAR (se existir) e recriar o banco de dados '{DB_NAME_FINAL}'. Deseja continuar?"):
        run_command([dropdb_exe, "-h", DB_HOST_LOCAL, "-p", DB_PORT_LOCAL, "-U", DB_USER_LOCAL, "--if-exists", DB_NAME_FINAL], f"Apagando banco de dados '{DB_NAME_FINAL}' antigo", can_fail=True)
        if run_command([createdb_exe, "-h", DB_HOST_LOCAL, "-p", DB_PORT_LOCAL, "-U", DB_USER_LOCAL, DB_NAME_FINAL], f"Criando banco de dados '{DB_NAME_FINAL}' limpo")[0] is None:
            sys.exit(1)
    else:
        print("Operação cancelada pelo usuário."); sys.exit(0)
    
    dump_file_path = os.path.join(os.path.expanduser("~"), "Documents", "migration_dump.fc")
    
    try:
        print_header("Fase 4.1: Criando Dump Local")
        dump_command = ["docker", "exec", LOCAL_CONTAINER_NAME, "pg_dump", "-U", "postgres", "-Fc", source_db_name]
        
        print(f"-> Criando arquivo de dump em '{dump_file_path}'. Isso pode levar vários minutos...")
        dump_env = os.environ.copy(); dump_env["PGPASSWORD"] = "password"

        with open(dump_file_path, "wb") as f:
            dump_process = subprocess.Popen(dump_command, stdout=f, stderr=subprocess.PIPE, env=dump_env)
            _, stderr_dump = dump_process.communicate()
            if dump_process.returncode != 0:
                print("[ERRO FATAL] Falha ao criar o arquivo de dump."); print(stderr_dump.decode('utf-8', errors='replace')); sys.exit(1)
        print("-> Arquivo de dump criado com sucesso!")

        num_jobs = max(1, os.cpu_count() // 2)
        print_header(f"Fase 4.2: Restaurando em Paralelo (usando {num_jobs} núcleos)")
        
        pg_restore_exe = os.path.join(pg_bin_dir, "pg_restore.exe")
        # CORREÇÃO: Removido o --clean, pois já limpamos o banco manualmente
        restore_command = [pg_restore_exe, "-h", DB_HOST_LOCAL, "-p", DB_PORT_LOCAL, "-U", DB_USER_LOCAL, "-d", DB_NAME_FINAL, "-v", "-j", str(num_jobs), dump_file_path]

        print("-> Acompanhe o progresso da restauração abaixo:"); print("-" * 70)
        
        restore_env = os.environ.copy(); restore_env["PGPASSWORD"] = DB_PASSWORD_LOCAL

        restore_process = subprocess.Popen(restore_command, env=restore_env, text=True, encoding='utf-8', errors='replace')
        restore_process.wait()
        
        print("-" * 70)
        if restore_process.returncode != 0:
            print("[ERRO FATAL] A migração falhou. Verifique os logs do pg_restore acima."); sys.exit(1)

    except Exception as e:
        print(f"[ERRO FATAL] Ocorreu um erro inesperado ao executar a migração: {e}"); sys.exit(1)
    finally:
        if os.path.exists(dump_file_path):
            print_header("Fase 4.3: Limpeza"); print(f"-> Removendo arquivo de dump temporário..."); os.remove(dump_file_path)

    print_header("Fase 5: Validação Final")
    
    psql_exe = os.path.join(pg_bin_dir, "psql.exe")
    count_source_cmd = ["docker", "exec", LOCAL_CONTAINER_NAME, "psql", "-U", "postgres", "-d", source_db_name, "-qtc", "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';"]
    source_count_raw, _ = run_command(count_source_cmd, "Contando tabelas na origem")
    
    count_dest_cmd = [psql_exe, "-h", DB_HOST_LOCAL, "-p", DB_PORT_LOCAL, "-U", DB_USER_LOCAL, "-d", DB_NAME_FINAL, "-qtc", "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';"]
    dest_count_raw, _ = run_command(count_dest_cmd, "Contando tabelas no destino")

    try:
        source_count = int(source_count_raw.strip())
        dest_count = int(dest_count_raw.strip())
        print(f"-> Tabelas na origem: {source_count}")
        print(f"-> Tabelas no destino: {dest_count}")
        if source_count == dest_count and source_count > 0:
            print_header("Migração Concluída e Validada com Sucesso!")
            print("O número de tabelas na origem e no destino correspondem.")
            print("Missão cumprida!")
        else:
            print_header("ALERTA DE VALIDAÇÃO!")
            print("O número de tabelas na origem e no destino NÃO correspondem. A migração pode ter sido parcial.")
    except (ValueError, TypeError):
        print("[ERRO DE VALIDAÇÃO] Não foi possível comparar a contagem de tabelas.")

if __name__ == "__main__":
    main()

