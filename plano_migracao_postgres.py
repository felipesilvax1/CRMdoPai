"""
PLANO DE MIGRAÇÃO SQLite → PostgreSQL
=====================================

ANÁLISE DO BANCO ATUAL:
- Tamanho: 31.09 GB
- Total de registros: 227.057.546
- Tabelas: 10
- Principais tabelas:
  * estabelecimentos: 79.225.899 registros (30 colunas)
  * empresas: 77.041.156 registros (7 colunas)
  * socios: 26.197.302 registros (11 colunas)
  * simples: 44.584.423 registros (7 colunas)

HARDWARE IDENTIFICADO:
- RAM: 32 GB
- Espaço livre: 299 GB
- Processador: 1 (precisa verificar núcleos)

ESTIMATIVA DE TEMPO DE MIGRAÇÃO:
================================

Baseado no volume de dados e hardware:

1. PREPARAÇÃO E SETUP (30-60 minutos):
   - Criação do container PostgreSQL
   - Configuração do banco
   - Criação das tabelas e índices

2. MIGRAÇÃO DOS DADOS (4-8 horas):
   - Tabelas pequenas (< 100K registros): 5-10 minutos
   - Tabelas médias (1M-10M registros): 30-60 minutos
   - Tabelas grandes (> 10M registros): 2-4 horas cada
   
   Estimativa total: 4-8 horas (dependendo da velocidade do disco)

3. OTIMIZAÇÃO PÓS-MIGRAÇÃO (30-60 minutos):
   - Criação de índices adicionais
   - Análise de estatísticas
   - Vacuum e reindex

TEMPO TOTAL ESTIMADO: 5-10 HORAS

FATORES QUE PODEM AFETAR O TEMPO:
- Velocidade do disco (SSD vs HDD)
- Configurações do PostgreSQL
- Processamento paralelo
- Rede (se container remoto)

RECOMENDAÇÕES:
- Executar durante horário de baixo uso
- Fazer backup completo antes
- Monitorar uso de recursos
- Considerar migração em lotes se necessário
"""

import sqlite3
import psycopg2
from psycopg2.extras import execute_values
import time
import logging
from typing import List, Dict, Any
import os

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MigradorSQLiteParaPostgres:
    def __init__(self, sqlite_db_path: str, postgres_config: Dict[str, str]):
        self.sqlite_db_path = sqlite_db_path
        self.postgres_config = postgres_config
        self.sqlite_conn = None
        self.postgres_conn = None
        
    def conectar_banco(self):
        """Conecta aos bancos SQLite e PostgreSQL"""
        try:
            # Conectar SQLite
            self.sqlite_conn = sqlite3.connect(self.sqlite_db_path)
            logger.info("Conectado ao SQLite com sucesso")
            
            # Conectar PostgreSQL
            self.postgres_conn = psycopg2.connect(**self.postgres_config)
            logger.info("Conectado ao PostgreSQL com sucesso")
            
        except Exception as e:
            logger.error(f"Erro ao conectar aos bancos: {e}")
            raise
    
    def obter_estrutura_tabelas(self) -> List[Dict[str, Any]]:
        """Obtém a estrutura de todas as tabelas do SQLite"""
        cursor = self.sqlite_conn.cursor()
        
        # Obter lista de tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tabelas = [row[0] for row in cursor.fetchall()]
        
        estruturas = []
        for tabela in tabelas:
            # Obter estrutura da tabela
            cursor.execute(f"PRAGMA table_info(`{tabela}`);")
            colunas = cursor.fetchall()
            
            # Contar registros
            cursor.execute(f"SELECT COUNT(*) FROM `{tabela}`;")
            total_registros = cursor.fetchone()[0]
            
            estruturas.append({
                'nome': tabela,
                'colunas': colunas,
                'total_registros': total_registros
            })
        
        return estruturas
    
    def criar_tabela_postgres(self, estrutura: Dict[str, Any]):
        """Cria tabela no PostgreSQL baseada na estrutura do SQLite"""
        cursor = self.postgres_conn.cursor()
        
        nome_tabela = estrutura['nome']
        colunas = estrutura['colunas']
        
        # Mapear tipos SQLite para PostgreSQL
        def mapear_tipo(tipo_sqlite: str) -> str:
            tipo_sqlite = tipo_sqlite.upper()
            if 'TEXT' in tipo_sqlite or 'VARCHAR' in tipo_sqlite:
                return 'TEXT'
            elif 'INTEGER' in tipo_sqlite or 'INT' in tipo_sqlite:
                return 'BIGINT'
            elif 'REAL' in tipo_sqlite or 'FLOAT' in tipo_sqlite:
                return 'DECIMAL'
            elif 'BLOB' in tipo_sqlite:
                return 'BYTEA'
            else:
                return 'TEXT'  # Default para TEXT
        
        # Criar comando CREATE TABLE
        colunas_sql = []
        for coluna in colunas:
            nome_coluna = coluna[1]
            tipo_coluna = mapear_tipo(coluna[2])
            nullable = "NULL" if coluna[3] == 0 else "NOT NULL"
            colunas_sql.append(f'"{nome_coluna}" {tipo_coluna} {nullable}')
        
        create_sql = f"""
        CREATE TABLE IF NOT EXISTS "{nome_tabela}" (
            {', '.join(colunas_sql)}
        );
        """
        
        cursor.execute(create_sql)
        self.postgres_conn.commit()
        logger.info(f"Tabela '{nome_tabela}' criada no PostgreSQL")
    
    def migrar_dados_tabela(self, nome_tabela: str, total_registros: int, batch_size: int = 10000):
        """Migra dados de uma tabela específica em lotes"""
        sqlite_cursor = self.sqlite_conn.cursor()
        postgres_cursor = self.postgres_conn.cursor()
        
        # Obter colunas da tabela
        sqlite_cursor.execute(f"PRAGMA table_info(`{nome_tabela}`);")
        colunas = [col[1] for col in sqlite_cursor.fetchall()]
        
        # Preparar query de inserção
        placeholders = ', '.join(['%s'] * len(colunas))
        colunas_str = ', '.join([f'"{col}"' for col in colunas])
        insert_sql = f'INSERT INTO "{nome_tabela}" ({colunas_str}) VALUES ({placeholders})'
        
        # Migrar em lotes
        offset = 0
        registros_migrados = 0
        
        logger.info(f"Iniciando migração da tabela '{nome_tabela}' ({total_registros:,} registros)")
        
        while offset < total_registros:
            # Buscar lote do SQLite
            sqlite_cursor.execute(f"SELECT * FROM `{nome_tabela}` LIMIT {batch_size} OFFSET {offset};")
            dados_lote = sqlite_cursor.fetchall()
            
            if not dados_lote:
                break
            
            # Inserir lote no PostgreSQL
            try:
                execute_values(
                    postgres_cursor,
                    insert_sql,
                    dados_lote,
                    template=None,
                    page_size=batch_size
                )
                self.postgres_conn.commit()
                
                registros_migrados += len(dados_lote)
                offset += batch_size
                
                progresso = (registros_migrados / total_registros) * 100
                logger.info(f"Tabela '{nome_tabela}': {registros_migrados:,}/{total_registros:,} ({progresso:.1f}%)")
                
            except Exception as e:
                logger.error(f"Erro ao migrar lote da tabela '{nome_tabela}': {e}")
                self.postgres_conn.rollback()
                raise
        
        logger.info(f"Migração da tabela '{nome_tabela}' concluída!")
    
    def criar_indices_postgres(self, estruturas: List[Dict[str, Any]]):
        """Cria índices no PostgreSQL baseado no SQLite"""
        cursor = self.postgres_conn.cursor()
        
        # Índices principais para CNPJ
        indices_principais = [
            'CREATE INDEX IF NOT EXISTS idx_estabelecimentos_cnpj_basico ON estabelecimentos (cnpj_basico);',
            'CREATE INDEX IF NOT EXISTS idx_empresas_cnpj_basico ON empresas (cnpj_basico);',
            'CREATE INDEX IF NOT EXISTS idx_socios_cnpj_basico ON socios (cnpj_basico);',
            'CREATE INDEX IF NOT EXISTS idx_simples_cnpj_basico ON simples (cnpj_basico);',
            'CREATE INDEX IF NOT EXISTS idx_estabelecimentos_cep ON estabelecimentos (cep);',
            'CREATE INDEX IF NOT EXISTS idx_estabelecimentos_uf ON estabelecimentos (uf);'
        ]
        
        for indice_sql in indices_principais:
            try:
                cursor.execute(indice_sql)
                self.postgres_conn.commit()
                logger.info(f"Índice criado: {indice_sql.split()[-1]}")
            except Exception as e:
                logger.warning(f"Erro ao criar índice: {e}")
    
    def executar_migracao_completa(self):
        """Executa a migração completa do SQLite para PostgreSQL"""
        inicio_total = time.time()
        
        try:
            # Conectar aos bancos
            self.conectar_banco()
            
            # Obter estrutura das tabelas
            logger.info("Obtendo estrutura das tabelas...")
            estruturas = self.obter_estrutura_tabelas()
            
            # Ordenar por tamanho (menores primeiro)
            estruturas.sort(key=lambda x: x['total_registros'])
            
            # Criar tabelas no PostgreSQL
            logger.info("Criando tabelas no PostgreSQL...")
            for estrutura in estruturas:
                self.criar_tabela_postgres(estrutura)
            
            # Migrar dados
            logger.info("Iniciando migração de dados...")
            for estrutura in estruturas:
                inicio_tabela = time.time()
                self.migrar_dados_tabela(
                    estrutura['nome'], 
                    estrutura['total_registros']
                )
                tempo_tabela = time.time() - inicio_tabela
                logger.info(f"Tabela '{estrutura['nome']}' migrada em {tempo_tabela:.2f} segundos")
            
            # Criar índices
            logger.info("Criando índices no PostgreSQL...")
            self.criar_indices_postgres(estruturas)
            
            # Vacuum e analyze
            logger.info("Executando VACUUM ANALYZE...")
            cursor = self.postgres_conn.cursor()
            cursor.execute("VACUUM ANALYZE;")
            self.postgres_conn.commit()
            
            tempo_total = time.time() - inicio_total
            logger.info(f"MIGRAÇÃO CONCLUÍDA! Tempo total: {tempo_total:.2f} segundos ({tempo_total/3600:.2f} horas)")
            
        except Exception as e:
            logger.error(f"Erro durante a migração: {e}")
            raise
        finally:
            if self.sqlite_conn:
                self.sqlite_conn.close()
            if self.postgres_conn:
                self.postgres_conn.close()

def main():
    """Função principal para executar a migração"""
    
    # Configuração do PostgreSQL (ajustar conforme necessário)
    postgres_config = {
        'host': 'localhost',
        'port': '5432',
        'database': 'cnpj_processado',
        'user': 'postgres',
        'password': 'sua_senha_aqui'
    }
    
    # Verificar se Docker está rodando
    try:
        import subprocess
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        if result.returncode != 0:
            logger.error("Docker não está rodando. Inicie o Docker primeiro.")
            return
    except FileNotFoundError:
        logger.error("Docker não está instalado.")
        return
    
    # Criar migrador
    migrador = MigradorSQLiteParaPostgres('CNPJ_Processado.db', postgres_config)
    
    # Executar migração
    migrador.executar_migracao_completa()

if __name__ == "__main__":
    main()

