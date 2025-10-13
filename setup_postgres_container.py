"""
Script para configurar container PostgreSQL para migração
"""

import subprocess
import time
import os
import sys

def verificar_docker():
    """Verifica se Docker está instalado e rodando"""
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Docker encontrado: {result.stdout.strip()}")
            return True
        else:
            print("✗ Docker não encontrado")
            return False
    except FileNotFoundError:
        print("✗ Docker não está instalado")
        return False

def verificar_docker_rodando():
    """Verifica se Docker está rodando"""
    try:
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Docker está rodando")
            return True
        else:
            print("✗ Docker não está rodando. Inicie o Docker Desktop.")
            return False
    except Exception as e:
        print(f"✗ Erro ao verificar Docker: {e}")
        return False

def criar_docker_compose():
    """Cria arquivo docker-compose.yml para PostgreSQL"""
    docker_compose_content = """version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: cnpj_postgres
    environment:
      POSTGRES_DB: cnpj_processado
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: cnpj123456
      POSTGRES_INITDB_ARGS: "--encoding=UTF8 --locale=pt_BR.UTF-8"
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init_scripts:/docker-entrypoint-initdb.d
    command: >
      postgres
      -c shared_preload_libraries=pg_stat_statements
      -c max_connections=200
      -c shared_buffers=8GB
      -c effective_cache_size=24GB
      -c maintenance_work_mem=2GB
      -c checkpoint_completion_target=0.9
      -c wal_buffers=16MB
      -c default_statistics_target=100
      -c random_page_cost=1.1
      -c effective_io_concurrency=200
      -c work_mem=256MB
      -c min_wal_size=1GB
      -c max_wal_size=4GB

volumes:
  postgres_data:
    driver: local
"""
    
    with open('docker-compose.yml', 'w', encoding='utf-8') as f:
        f.write(docker_compose_content)
    
    print("✓ Arquivo docker-compose.yml criado")

def criar_scripts_inicializacao():
    """Cria scripts de inicialização do PostgreSQL"""
    
    # Criar diretório para scripts
    os.makedirs('init_scripts', exist_ok=True)
    
    # Script de otimização
    init_script = """-- Script de inicialização do PostgreSQL para CNPJ
-- Otimizações para migração de dados grandes

-- Configurações de performance
ALTER SYSTEM SET shared_buffers = '8GB';
ALTER SYSTEM SET effective_cache_size = '24GB';
ALTER SYSTEM SET maintenance_work_mem = '2GB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_io_concurrency = 200;
ALTER SYSTEM SET work_mem = '256MB';
ALTER SYSTEM SET min_wal_size = '1GB';
ALTER SYSTEM SET max_wal_size = '4GB';

-- Recarregar configurações
SELECT pg_reload_conf();

-- Criar extensões úteis
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Configurar encoding
SET client_encoding = 'UTF8';
"""
    
    with open('init_scripts/01_init.sql', 'w', encoding='utf-8') as f:
        f.write(init_script)
    
    print("✓ Script de inicialização criado")

def criar_requirements():
    """Cria arquivo requirements.txt com dependências"""
    requirements = """psycopg2-binary==2.9.9
sqlite3
"""
    
    with open('requirements.txt', 'w', encoding='utf-8') as f:
        f.write(requirements)
    
    print("✓ Arquivo requirements.txt criado")

def iniciar_container():
    """Inicia o container PostgreSQL"""
    print("\n🚀 Iniciando container PostgreSQL...")
    
    try:
        # Parar container existente se houver
        subprocess.run(['docker-compose', 'down'], capture_output=True)
        
        # Iniciar container
        result = subprocess.run(['docker-compose', 'up', '-d'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ Container PostgreSQL iniciado com sucesso!")
            print("📊 Aguardando PostgreSQL inicializar...")
            
            # Aguardar PostgreSQL ficar pronto
            for i in range(30):
                time.sleep(2)
                try:
                    result = subprocess.run([
                        'docker', 'exec', 'cnpj_postgres', 
                        'pg_isready', '-U', 'postgres'
                    ], capture_output=True)
                    
                    if result.returncode == 0:
                        print("✓ PostgreSQL está pronto para conexões!")
                        return True
                except:
                    pass
                
                print(f"⏳ Aguardando... ({i+1}/30)")
            
            print("⚠️  PostgreSQL pode não estar totalmente pronto ainda")
            return True
            
        else:
            print(f"✗ Erro ao iniciar container: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"✗ Erro ao iniciar container: {e}")
        return False

def mostrar_informacoes_conexao():
    """Mostra informações de conexão"""
    print("\n" + "="*60)
    print("📋 INFORMAÇÕES DE CONEXÃO POSTGRESQL")
    print("="*60)
    print("Host: localhost")
    print("Porta: 5432")
    print("Database: cnpj_processado")
    print("Usuário: postgres")
    print("Senha: cnpj123456")
    print("="*60)
    print("\n💡 Para conectar via psql:")
    print("docker exec -it cnpj_postgres psql -U postgres -d cnpj_processado")
    print("\n💡 Para ver logs do container:")
    print("docker logs cnpj_postgres")
    print("\n💡 Para parar o container:")
    print("docker-compose down")

def main():
    """Função principal"""
    print("🔧 CONFIGURAÇÃO DO CONTAINER POSTGRESQL")
    print("="*50)
    
    # Verificações iniciais
    if not verificar_docker():
        print("\n❌ Docker não está disponível. Instale o Docker Desktop.")
        return False
    
    if not verificar_docker_rodando():
        print("\n❌ Docker não está rodando. Inicie o Docker Desktop.")
        return False
    
    print("\n📁 Criando arquivos de configuração...")
    criar_docker_compose()
    criar_scripts_inicializacao()
    criar_requirements()
    
    print("\n📦 Instalando dependências Python...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True)
        print("✓ Dependências instaladas")
    except subprocess.CalledProcessError:
        print("⚠️  Erro ao instalar dependências. Instale manualmente: pip install psycopg2-binary")
    
    # Iniciar container
    if iniciar_container():
        mostrar_informacoes_conexao()
        print("\n✅ SETUP CONCLUÍDO!")
        print("\n🎯 Próximos passos:")
        print("1. Ajuste a senha no arquivo plano_migracao_postgres.py")
        print("2. Execute: python plano_migracao_postgres.py")
        return True
    else:
        print("\n❌ Falha na configuração do container")
        return False

if __name__ == "__main__":
    main()

