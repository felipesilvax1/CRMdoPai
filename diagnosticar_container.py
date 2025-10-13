import subprocess
import time
import sys

# --- CONFIGURAÇÕES ---
CONTAINER_NAME = "cnpj_postgres_local"
VOLUME_NAME = "cnpj_postgres_data_local"
IMAGE_NAME = "postgres:11" # A imagem que o contêiner usa

def run_command(command, description, can_fail=False):
    """Executa um comando no shell e lida com a saída."""
    print(f"-> {description}...")
    try:
        process = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', errors='replace')
        
        if process.returncode != 0 and not can_fail:
            print(f"[ERRO] O comando falhou.")
            print("--- MENSAGEM DE ERRO ---")
            print(process.stderr.strip())
            print("------------------------")
            return False
            
        return True
    except FileNotFoundError:
        print(f"[ERRO FATAL] O comando '{command[0]}' não foi encontrado. O Docker está instalado e em execução?")
        return False

def main():
    """Inicia o contêiner em modo de manutenção, corrige as permissões e recria o contêiner final."""
    print(f"--- INICIANDO REPARO DE PERMISSÕES DO CONTÊINER '{CONTAINER_NAME}' ---")

    # --- PASSO 1: Parar e remover o contêiner quebrado existente ---
    print("\n--- PASSO 1/5: Limpando ambiente ---")
    run_command(["docker", "stop", CONTAINER_NAME], f"Parando o contêiner '{CONTAINER_NAME}' (se estiver executando)", can_fail=True)
    run_command(["docker", "rm", CONTAINER_NAME], f"Removendo o contêiner '{CONTAINER_NAME}' antigo", can_fail=True)
    
    # --- PASSO 2: Iniciar contêiner em modo de manutenção ---
    print(f"\n--- PASSO 2/5: Iniciando contêiner em modo de manutenção ---")
    maintenance_container_name = f"{CONTAINER_NAME}-maintenance"
    run_command(["docker", "stop", maintenance_container_name], "Limpando contêiner de manutenção antigo (se existir)", can_fail=True)
    run_command(["docker", "rm", maintenance_container_name], "Limpando contêiner de manutenção antigo (se existir)", can_fail=True)

    maintenance_command = [
        "docker", "run", "-d", "--name", maintenance_container_name,
        "-v", f"{VOLUME_NAME}:/var/lib/postgresql/data",
        IMAGE_NAME,
        "sleep", "infinity"
    ]
    if not run_command(maintenance_command, "Iniciando contêiner de manutenção"):
        sys.exit(1)
    
    print("-> Contêiner de manutenção iniciado com sucesso.")
    time.sleep(2)

    # --- PASSO 3: Corrigir as permissões ---
    print("\n--- PASSO 3/5: Corrigindo as permissões dos arquivos ---")
    fix_perms_command = [
        "docker", "exec", maintenance_container_name,
        "chown", "-R", "postgres:postgres", "/var/lib/postgresql/data"
    ]
    if not run_command(fix_perms_command, "Executando 'chown' para corrigir permissões"):
        run_command(["docker", "stop", maintenance_container_name], "Parando contêiner de manutenção", can_fail=True)
        run_command(["docker", "rm", maintenance_container_name], "Removendo contêiner de manutenção", can_fail=True)
        sys.exit(1)
    
    print("-> Permissões corrigidas com sucesso!")

    # --- PASSO 4: Limpar o contêiner de manutenção ---
    print("\n--- PASSO 4/5: Finalizando o modo de manutenção ---")
    run_command(["docker", "stop", maintenance_container_name], "Parando contêiner de manutenção", can_fail=True)
    run_command(["docker", "rm", maintenance_container_name], "Removendo contêiner de manutenção", can_fail=True)

    # --- PASSO 5: Recriar o contêiner PostgreSQL final ---
    print(f"\n--- PASSO 5/5: Recriando o contêiner '{CONTAINER_NAME}' final ---")
    final_container_command = [
        "docker", "run", "-d", "--name", CONTAINER_NAME,
        "-e", "POSTGRES_PASSWORD=password",
        "-e", "POSTGRES_USER=postgres",
        "-v", f"{VOLUME_NAME}:/var/lib/postgresql/data",
        IMAGE_NAME
    ]
    if not run_command(final_container_command, "Recriando o contêiner final do PostgreSQL"):
        print("[ERRO] Não foi possível recriar o contêiner final. Verifique os logs do Docker.")
        sys.exit(1)

    print("-> Contêiner final recriado com sucesso! Aguardando inicialização...")
    time.sleep(10) # Pausa para dar tempo ao PostgreSQL de iniciar completamente

    print("\n--------------------------------------------------")
    print("[SUCESSO] O reparo foi concluído e o contêiner está pronto!")
    print(f"O contêiner '{CONTAINER_NAME}' está agora em execução com os dados reparados.")
    print("Agora, prossiga executando o script 'migrar_postgres.py' para finalizar a migração.")
    print("--------------------------------------------------")

if __name__ == "__main__":
    main()

