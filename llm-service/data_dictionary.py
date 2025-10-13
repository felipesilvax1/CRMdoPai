# -*- coding: utf-8 -*-
"""
Dicionário de Dados - Schema completo do banco CNPJ
"""

DATA_DICTIONARY = """
═══════════════════════════════════════════════════════════════
DICIONÁRIO DE DADOS - BANCO CNPJ BRASIL
═══════════════════════════════════════════════════════════════

IMPORTANTE: Este é o schema REAL do banco com 79 milhões de registros!

═══════════════════════════════════════════════════════════════
TABELA: estabelecimentos (79.225.899 registros)
═══════════════════════════════════════════════════════════════

COLUNAS PRINCIPAIS:
  • cnpj_basico (text) - 8 primeiros dígitos do CNPJ
  • cnpj_ordem (text) - 4 dígitos de ordem
  • cnpj_dv (text) - 2 dígitos verificadores
  • nome_fantasia (text) - Nome fantasia da empresa
  • situacao_cadastral (text) - Código da situação:
      '01' = Nula
      '02' = Ativa ← USAR ESTE PARA "ATIVOS/ATIVAS"
      '03' = Suspensa
      '04' = Inapta
      '08' = Baixada
  
LOCALIZAÇÃO:
  • uf (text) - Sigla do estado (SP, RJ, MG, RS, PR, SC, BA, etc)
      ⚠️ NUNCA use 'BR' - Brasil não é UF válida!
  • municipio (text) - CÓDIGO IBGE do município (ex: '6291' = Barueri)
      ⚠️ NÃO é nome da cidade, é CÓDIGO!
      Para buscar por nome de cidade, use JOIN com tabela municipios
  • bairro (text) - Nome do bairro
  • logradouro (text) - Nome da rua/avenida
  • cep (text) - CEP

ATIVIDADE:
  • cnae_fiscal_principal (text) - Código CNAE principal
  • cnae_fiscal_secundaria (text) - CNAEs secundários (separados por vírgula)
  • data_inicio_atividade (text) - Data de início

OUTROS:
  • identificador_matriz_filial (text) - '1'=Matriz, '2'=Filial
  • correio_eletronico (text) - Email
  • ddd_1, telefone_1 (text) - Telefone

═══════════════════════════════════════════════════════════════
TABELA: municipios (5.570 registros)
═══════════════════════════════════════════════════════════════

COLUNAS:
  • codigo (text) - Código IBGE do município
  • descricao (text) - Nome da cidade (ex: 'BARUERI', 'SÃO PAULO')

⚠️ IMPORTANTE: Para buscar por NOME DE CIDADE, use JOIN:

EXEMPLO CORRETO:
  SELECT COUNT(*) 
  FROM estabelecimentos e
  JOIN municipios m ON e.municipio = m.codigo
  WHERE m.descricao ILIKE '%BARUERI%' AND e.uf = 'SP';

═══════════════════════════════════════════════════════════════
TABELA: cnaes (2.718 registros)
═══════════════════════════════════════════════════════════════

Descrições dos CNAEs (códigos de atividade econômica)

═══════════════════════════════════════════════════════════════
TABELA: empresas (vazia - em migração)
TABELA: socios (vazia - em migração)
═══════════════════════════════════════════════════════════════

⚠️ Estas tabelas ainda não têm dados!

═══════════════════════════════════════════════════════════════
EXEMPLOS DE QUERIES CORRETAS
═══════════════════════════════════════════════════════════════

1. Contar estabelecimentos ativos no Brasil:
   SELECT COUNT(*) FROM estabelecimentos WHERE situacao_cadastral = '02';

2. Contar por estado:
   SELECT COUNT(*) FROM estabelecimentos WHERE uf = 'SP';

3. Buscar por CÓDIGO de município:
   SELECT * FROM estabelecimentos WHERE municipio = '6291' LIMIT 10;

4. Buscar por NOME de município (JOIN):
   SELECT e.*, m.descricao as nome_municipio
   FROM estabelecimentos e
   JOIN municipios m ON e.municipio = m.codigo
   WHERE m.descricao ILIKE '%BARUERI%'
   LIMIT 10;

5. CNAEs mais comuns:
   SELECT cnae_fiscal_principal, COUNT(*) as total
   FROM estabelecimentos
   GROUP BY cnae_fiscal_principal
   ORDER BY total DESC
   LIMIT 10;

═══════════════════════════════════════════════════════════════
CÓDIGOS IMPORTANTES PARA LEMBRAR
═══════════════════════════════════════════════════════════════

UFs (Estados):
  AC, AL, AP, AM, BA, CE, DF, ES, GO, MA, MT, MS, MG, PA, PB, PR, 
  PE, PI, RJ, RN, RS, RO, RR, SC, SP, SE, TO

Situação Cadastral:
  '02' = Ativa (usar para "ativos", "ativas", "em atividade")
  '01' = Nula
  '03' = Suspensa
  '04' = Inapta
  '08' = Baixada

Matriz/Filial:
  '1' = Matriz
  '2' = Filial

═══════════════════════════════════════════════════════════════
"""

def get_data_dictionary():
    """Retorna o dicionário de dados completo"""
    return DATA_DICTIONARY

def get_table_relationships():
    """Retorna informações sobre relacionamentos entre tabelas"""
    return {
        "estabelecimentos_municipios": {
            "join": "estabelecimentos.municipio = municipios.codigo",
            "description": "Para buscar por nome de cidade, use JOIN com municipios. A coluna é 'descricao' (não 'nome')!"
        },
        "estabelecimentos_cnaes": {
            "join": "estabelecimentos.cnae_fiscal_principal = cnaes.codigo",
            "description": "Para descrição do CNAE, use JOIN com cnaes"
        }
    }

