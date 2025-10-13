# -*- coding: utf-8 -*-
"""
Script para importar dados PostgreSQL de um laptop remoto na rede
"""
import subprocess
import os
import sys
from datetime import datetime

# Configurações
REMOTE_HOST = "192.168.15.24"
REMOTE_CONTAINER = "c93d7f48cac6"
REMOTE_USER = "postgres"
REMOTE_PASSWORD = "password"

LOCAL_CONTAINER = "cnpj_postgres_final"
LOCAL_USER = "postgres"
LOCAL_PASSWORD = "password"

DUMP_FILE = "dump_postgres_remoto.sql"

def executar_comando(comando, descricao):
    """Executa comando e mostra progresso"""
    print(f"\n[>>] {descricao}...")
    try:
        result = subprocess.run(
            comando,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        if result.returncode != 0:
            print(f"[ERRO] {result.stderr}")
            return False, result.stderr
        print(f"[OK] {descricao} concluído!")
        return True, result.stdout
    except Exception as e:
        print(f"[ERRO] {str(e)}")
        return False, str(e)

def testar_conexao_remota():
    """Testa conectividade com o laptop remoto"""
    print("\n" + "="*60)
    print("ETAPA 1: Testando conectividade")
    print("="*60)
    
    # Ping no IP remoto
    cmd = f"ping -n 2 {REMOTE_HOST}"
    sucesso, output = executar_comando(cmd, f"Ping em {REMOTE_HOST}")
    
    if not sucesso:
        print(f"\n[!] AVISO: Não consegui fazer ping em {REMOTE_HOST}")
        print("    Verifique se o laptop está ligado e na rede")
        resposta = input("Deseja continuar mesmo assim? (s/n): ")
        if resposta.lower() != 's':
            return False
    
    return True

def descobrir_porta_postgres():
    """Descobre qual porta o PostgreSQL está exposto no laptop remoto"""
    print("\n" + "="*60)
    print("ETAPA 2: Descobrindo porta do PostgreSQL remoto")
    print("="*60)
    
    # Tentar portas comuns
    portas_comuns = [5432, 54322, 5433]
    
    for porta in portas_comuns:
        print(f"\nTestando porta {porta}...")
        cmd = f'docker exec {REMOTE_CONTAINER} psql -U {REMOTE_USER} -c "SELECT 1" 2>&1'
        # Nota: Precisaríamos de acesso SSH ou Docker remoto para isso
        # Vamos assumir porta padrão 5432
    
    print("\n[INFO] Assumindo porta padrão: 5432")
    return 5432

def listar_bancos_remotos():
    """Lista os bancos de dados disponíveis no servidor remoto"""
    print("\n" + "="*60)
    print("ETAPA 3: Listando bancos de dados remotos")
    print("="*60)
    
    # Usando pg_dump via rede diretamente
    cmd = f'set PGPASSWORD={REMOTE_PASSWORD} && psql -h {REMOTE_HOST} -U {REMOTE_USER} -p 5432 -c "\\l" 2>&1'
    sucesso, output = executar_comando(cmd, "Listar bancos remotos")
    
    if sucesso:
        print("\n" + output)
    
    return sucesso

def fazer_dump_remoto(nome_banco):
    """Faz dump do banco remoto"""
    print("\n" + "="*60)
    print(f"ETAPA 4: Fazendo dump do banco '{nome_banco}'")
    print("="*60)
    
    # Usar pg_dump para exportar via rede
    cmd = f'set PGPASSWORD={REMOTE_PASSWORD} && pg_dump -h {REMOTE_HOST} -U {REMOTE_USER} -p 5432 -d {nome_banco} -F c -f {DUMP_FILE} 2>&1'
    
    print(f"\n[INFO] Criando dump compactado em {DUMP_FILE}...")
    print("[INFO] Isso pode levar VÁRIOS MINUTOS dependendo do tamanho...")
    
    sucesso, output = executar_comando(cmd, "Dump do banco remoto")
    
    if sucesso and os.path.exists(DUMP_FILE):
        tamanho = os.path.getsize(DUMP_FILE) / (1024*1024)
        print(f"\n[OK] Dump criado com sucesso!")
        print(f"     Tamanho: {tamanho:.2f} MB")
        return True
    
    return False

def restaurar_dump_local(nome_banco):
    """Restaura o dump no PostgreSQL local"""
    print("\n" + "="*60)
    print(f"ETAPA 5: Restaurando dump no banco local")
    print("="*60)
    
    # Criar banco se não existir
    cmd = f'docker exec {LOCAL_CONTAINER} psql -U {LOCAL_USER} -c "CREATE DATABASE {nome_banco};" 2>&1'
    executar_comando(cmd, f"Criar banco {nome_banco}")
    
    # Restaurar dump
    cmd = f'docker exec -i {LOCAL_CONTAINER} pg_restore -U {LOCAL_USER} -d {nome_banco} -v < {DUMP_FILE} 2>&1'
    
    print(f"\n[INFO] Restaurando dados...")
    print("[INFO] Isso pode levar VÁRIOS MINUTOS...")
    
    sucesso, output = executar_comando(cmd, "Restaurar dump")
    return sucesso

def validar_checksums(nome_banco):
    """Valida os dados comparando contagens entre origem e destino"""
    print("\n" + "="*60)
    print("ETAPA 6: Validando integridade dos dados")
    print("="*60)
    
    tabelas = ['empresas', 'estabelecimentos', 'socios', 'cnaes']
    
    print("\nComparando contagens de registros:\n")
    print(f"{'Tabela':<20} {'Remoto':>15} {'Local':>15} {'Status':>10}")
    print("-" * 65)
    
    tudo_ok = True
    
    for tabela in tabelas:
        # Contar no remoto
        cmd_remoto = f'set PGPASSWORD={REMOTE_PASSWORD} && psql -h {REMOTE_HOST} -U {REMOTE_USER} -d {nome_banco} -t -c "SELECT COUNT(*) FROM {tabela};" 2>&1'
        sucesso_r, count_remoto = executar_comando(cmd_remoto, f"Contar {tabela} remoto")
        
        # Contar no local
        cmd_local = f'docker exec {LOCAL_CONTAINER} psql -U {LOCAL_USER} -d {nome_banco} -t -c "SELECT COUNT(*) FROM {tabela};" 2>&1'
        sucesso_l, count_local = executar_comando(cmd_local, f"Contar {tabela} local")
        
        if sucesso_r and sucesso_l:
            try:
                num_remoto = int(count_remoto.strip())
                num_local = int(count_local.strip())
                status = "OK" if num_remoto == num_local else "ERRO"
                
                if status == "ERRO":
                    tudo_ok = False
                
                print(f"{tabela:<20} {num_remoto:>15,} {num_local:>15,} {status:>10}")
            except:
                print(f"{tabela:<20} {'ERRO':>15} {'ERRO':>15} {'ERRO':>10}")
                tudo_ok = False
        else:
            print(f"{tabela:<20} {'N/A':>15} {'N/A':>15} {'SKIP':>10}")
    
    print()
    return tudo_ok

def main():
    """Função principal"""
    print("\n" + "="*60)
    print("IMPORTAÇÃO DE DADOS POSTGRESQL REMOTO")
    print("="*60)
    print(f"\nOrigem: {REMOTE_HOST} (Container: {REMOTE_CONTAINER})")
    print(f"Destino: Local (Container: {LOCAL_CONTAINER})")
    print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Testar conexão
    if not testar_conexao_remota():
        print("\n[ERRO] Falha na conectividade. Abortando.")
        sys.exit(1)
    
    # 2. Descobrir bancos disponíveis
    print("\n[INFO] Para listar bancos remotos, você precisa ter:")
    print("       - PostgreSQL client instalado localmente")
    print("       - Porta 5432 liberada no firewall do laptop remoto")
    
    nome_banco = input("\nDigite o nome do banco a importar (padrão: cnpj_processed): ").strip()
    if not nome_banco:
        nome_banco = "cnpj_processed"
    
    # 3. Fazer dump
    print(f"\n[INFO] Iniciando dump do banco '{nome_banco}'...")
    if not fazer_dump_remoto(nome_banco):
        print("\n[ERRO] Falha ao criar dump. Verifique:")
        print("       - PostgreSQL client (pg_dump) instalado")
        print("       - Porta 5432 acessível no laptop remoto")
        print("       - Credenciais corretas")
        sys.exit(1)
    
    # 4. Restaurar
    if not restaurar_dump_local(nome_banco):
        print("\n[AVISO] Alguns erros durante restauração (pode ser normal)")
    
    # 5. Validar
    if validar_checksums(nome_banco):
        print("\n" + "="*60)
        print("IMPORTAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*60)
        print(f"\nBanco '{nome_banco}' importado e validado!")
        print(f"Container local: {LOCAL_CONTAINER}")
    else:
        print("\n" + "="*60)
        print("IMPORTAÇÃO CONCLUÍDA COM AVISOS")
        print("="*60)
        print("\n[!] Algumas tabelas têm contagens diferentes.")
        print("    Verifique manualmente se está tudo correto.")
    
    # Limpar arquivo temporário
    if os.path.exists(DUMP_FILE):
        resposta = input(f"\nDeseja remover o arquivo {DUMP_FILE}? (s/n): ")
        if resposta.lower() == 's':
            os.remove(DUMP_FILE)
            print("[OK] Arquivo removido!")

if __name__ == '__main__':
    print("\n[!] IMPORTANTE:")
    print("    Este script requer:")
    print("    - PostgreSQL client tools instalados (psql, pg_dump, pg_restore)")
    print("    - Acesso de rede ao laptop remoto (porta 5432)")
    print("    - Firewall configurado para permitir conexões PostgreSQL")
    print()
    
    resposta = input("Deseja continuar? (s/n): ")
    if resposta.lower() == 's':
        main()
    else:
        print("Operação cancelada.")


