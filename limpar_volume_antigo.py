import subprocess
import sys
import re

# --- CONFIGURAÇÃO ---
# Nome do volume antigo que queremos remover (o original do SSD)
VOLUME_PARA_REMOVER = "2025-08_postgres-data"

def run_command(command, description, can_fail=False):
    """Executa um comando no shell, lida com erros e retorna a saída."""
    print(f"-> {description}...")
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='replace')
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            if can_fail:
                return None, stderr.strip()  # Retorna o erro para tratamento
            else:
                print(f"[ERRO FATAL] O comando falhou com o código {process.returncode}.")
                print("--- MENSAGEM DE ERRO ---")
                print(stderr)
                print("------------------------")
                sys.exit(1)
        
        print("   ... Sucesso!")
        return stdout.strip(), None

    except FileNotFoundError:
        print(f"[ERRO FATAL] O comando '{command[0]}' não foi encontrado. O Docker está em execução?")
        sys.exit(1)

def main():
    """Função principal para remover o volume Docker antigo."""
    print("--- INICIANDO SCRIPT DE LIMPEZA DE VOLUME DOCKER ---")
    
    confirm = input(f"Tem certeza que deseja remover PERMANENTEMENTE o volume '{VOLUME_PARA_REMOVER}'? (s/n): ").lower()
    
    if confirm == 's':
        # Tenta remover o volume, permitindo que o comando falhe para que possamos tratar o erro
        _, error_message = run_command(["docker", "volume", "rm", VOLUME_PARA_REMOVER], f"Tentando remover o volume '{VOLUME_PARA_REMOVER}'", can_fail=True)
        
        # Se a remoção falhou porque o volume está em uso
        if error_message and "volume is in use" in error_message:
            print(f"   -> AVISO: O volume está em uso.")
            
            # Tenta extrair o ID do contêiner da mensagem de erro
            container_id_match = re.search(r'\[([a-f0-9]+)\]', error_message)
            
            if container_id_match:
                container_id = container_id_match.group(1)
                print(f"   Ele está sendo usado pelo contêiner com ID: {container_id[:12]}")
                
                choice = input("   Deseja parar e remover este contêiner para liberar o volume? (s/n): ").lower()
                if choice == 's':
                    run_command(["docker", "stop", container_id], f"Parando o contêiner {container_id[:12]}")
                    run_command(["docker", "rm", container_id], f"Removendo o contêiner {container_id[:12]}")
                    
                    # Tenta remover o volume novamente após liberar
                    run_command(["docker", "volume", "rm", VOLUME_PARA_REMOVER], f"Removendo o volume '{VOLUME_PARA_REMOVER}' novamente")
                    print(f"\n[SUCESSO] O volume foi removido e o espaço em disco foi liberado.")
                else:
                    print("Operação cancelada. O volume não foi removido.")
            else:
                print("[ERRO] Não foi possível identificar o contêiner que está usando o volume. Remova-o manualmente pelo Docker Desktop.")
        
        elif error_message:
            # Se ocorreu outro tipo de erro não esperado
            print(f"[ERRO FATAL] Falha ao remover o volume com uma mensagem inesperada:")
            print(error_message)
        
        else:
            # Se a remoção foi bem-sucedida na primeira tentativa
            print(f"\n[SUCESSO] O volume foi removido e o espaço em disco foi liberado.")

    else:
        print("Operação cancelada pelo usuário.")

if __name__ == "__main__":
    main()

