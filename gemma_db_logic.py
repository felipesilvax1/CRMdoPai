# -*- coding: utf-8 -*-
# ==============================================================================
# BLOCO 1: IMPORTAÇÕES E CONFIGURAÇÃO INICIAL
# ==============================================================================
import os
import sys
import pandas as pd
from operator import itemgetter
from sqlalchemy import create_engine, text as sql_text

# Importações do LangChain
import langchain
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain.prompts import PromptTemplate
from langchain_ollama.llms import OllamaLLM
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Ativa o modo verboso para máxima transparência durante a depuração
langchain.verbose = True

# ==============================================================================
# BLOCO 2: INICIALIZAÇÃO SINGLETON (GESTÃO DE CONEXÕES)
# ==============================================================================
# Usamos variáveis globais para evitar recarregar o modelo e reconectar ao DB a cada chamada
llm = None
db = None
engine = None 
current_db_path = None

def inicializar_modelo_e_db(caminho_do_banco):
    """Inicializa a conexão com o LLM e o banco de dados se ainda não tiver sido feito."""
    global llm, db, current_db_path, engine
    if llm is None:
        print("Conectando ao modelo Llama 3 (Ollama)...")
        llm = OllamaLLM(model="llama3:8b", temperature=0)
    
    if db is None or current_db_path != caminho_do_banco:
        print(f"Conectando ao banco de dados em: {caminho_do_banco}")
        engine = create_engine(f"sqlite:///{caminho_do_banco}")
        db = SQLDatabase(engine=engine)
        current_db_path = caminho_do_banco

# ==============================================================================
# BLOCO 3: FUNÇÃO PRINCIPAL DE PROCESSAMENTO
# ==============================================================================
def processar_pergunta(pergunta: str, caminho_do_banco: str) -> dict:
    """
    Função principal que recebe uma pergunta, processa-a através do agente de IA
    e retorna um dicionário com o resultado completo.
    """
    try:
        inicializar_modelo_e_db(caminho_do_banco)
        prompt_usado = "" 

        # --- BLOCO 3.1: DEFINIÇÃO DOS PROMPTS (O "CÉREBRO" DO AGENTE) ---
        PROMPT_GERACAO = PromptTemplate(
            input_variables=["input", "table_info", "top_k"],
            template="""Você é um assistente especialista em SQL, com foco exclusivo num banco de dados da Receita Federal brasileira. A sua missão é traduzir perguntas em português para consultas SELECT precisas para o dialeto SQLite.

**PRINCÍPIOS FUNDAMENTAIS (REGRAS INVIOLÁVEIS):**
1.  **Aderência Estrita ao Esquema:** Opere exclusivamente com as tabelas e colunas fornecidas. Nunca invente campos.
2.  **Tratamento de Nomes com Espaços:** Nomes de colunas com espaços (ex: "razao social", "cnpj basico") DEVEM obrigatoriamente ser envolvidos em aspas duplas ("). Ex: `SELECT T1."razao social" FROM empresas AS T1`.
3.  **A Chave de Ligação é "cnpj basico":** Use sempre a coluna "cnpj basico" para fazer JOIN entre as tabelas `empresas`, `estabelecimentos`, `socios` e `simples`.
4.  **Montagem do CNPJ Completo:** Para obter o CNPJ completo, você DEVE concatenar as colunas da tabela `estabelecimentos`: `cnpj_basico`, `cnpj_ordem`, `cnpj_dv`. O alias DEVE ser `cnpj_completo`.
5.  **Buscas de Texto Flexíveis:** Para buscas por nomes (`razao social`, `nome fantasia`), utilize sempre `LIKE '%TERMO%'` e `COLLATE NOCASE` para ignorar maiúsculas/minúsculas.
6.  **Busca por Atividade (CNAE):** Para perguntas sobre atividades (ex: 'logística', 'transporte'), encontre os códigos CNAE relevantes na tabela `cnaes` usando uma subconsulta. Pense em sinónimos.
7.  **Restrição a SELECT:** Apenas gere consultas `SELECT`. `INSERT`, `UPDATE`, `DELETE` são proibidos.

**EXEMPLOS PRÁTICOS:**
* **Pergunta:** "Qual o CNPJ da empresa 'Padaria Pão Quente LTDA'?"
* **SQL Gerado:** `SELECT "cnpj basico", "razao social" FROM empresas WHERE "razao social" LIKE '%PADARIA PAO QUENTE LTDA%' COLLATE NOCASE;`

* **Pergunta:** "Quais empresas de logística existem em Barueri?"
* **SQL Gerado:** `SELECT T1."razao social", T2."cnpj_basico" || T2."cnpj_ordem" || T2."cnpj_dv" AS cnpj_completo FROM empresas AS T1 JOIN estabelecimentos AS T2 ON T1."cnpj basico" = T2."cnpj basico" WHERE T2.cnae_fiscal_principal IN (SELECT codigo FROM cnaes WHERE lower(descricao) LIKE '%logistica%' OR lower(descricao) LIKE '%transporte%' OR lower(descricao) LIKE '%armazenagem%') AND T2.municipio = 'BARUERI' LIMIT {top_k};`

**A SUA TAREFA:**
Apenas retorne a consulta SQL final e completa, sem nenhum texto adicional.

Esquema do banco de dados:
{table_info}
Pergunta do Utilizador: {input}
Consulta SQL:"""
        )

        # ATUALIZAÇÃO: Prompt de correção muito mais rigoroso
        PROMPT_CORRECAO = PromptTemplate(
            input_variables=["input", "table_info", "faulty_query", "error_message"],
            template="""Sua tarefa é corrigir a consulta SQL fornecida. A consulta falhou com o seguinte erro. Siga estritamente as regras e exemplos do prompt original.
**NÃO** inclua NENHUM texto, explicação ou markdown. A sua resposta DEVE ser apenas a string SQL corrigida.

Pergunta Original: {input}
Esquema: {table_info}
Consulta com Erro: {faulty_query}
Erro SQLite: {error_message}
Consulta SQL Corrigida (APENAS O CÓDIGO):"""
        )
        
        PROMPT_RESPOSTA = PromptTemplate.from_template("Responda à pergunta do usuário em português com base no resultado: Pergunta: {question}, Resultado: {result}")
        
        # --- BLOCO 3.2: CRIAÇÃO DAS CADEIAS DE EXECUÇÃO (CHAINS) ---
        generate_query_chain = create_sql_query_chain(llm, db, prompt=PROMPT_GERACAO)
        correction_chain = PROMPT_CORRECAO | llm | StrOutputParser()
        rephrase_answer_chain = PROMPT_RESPOSTA | llm | StrOutputParser()
        
        # --- BLOCO 3.3: LÓGICA DE EXECUÇÃO COM CICLO DE AUTO-CORREÇÃO ---
        MAX_RETRIES = 3
        sql_query = ""
        last_error = ""
        df = None
        
        for attempt in range(MAX_RETRIES):
            try:
                if attempt == 0:
                    print(f"\n--- Tentativa {attempt + 1}: Gerando SQL ---")
                    prompt_usado = PROMPT_GERACAO.format(input=pergunta, table_info=db.get_table_info(), top_k=50)
                    sql_query = generate_query_chain.invoke({"question": pergunta})
                else:
                    print(f"\n--- Tentativa {attempt + 1}: Corrigindo SQL ---")
                    prompt_usado = PROMPT_CORRECAO.format(input=pergunta, table_info=db.get_table_info(), faulty_query=sql_query, error_message=last_error)
                    sql_query = correction_chain.invoke({"input": pergunta, "table_info": db.get_table_info(), "faulty_query": sql_query, "error_message": last_error})
                
                with engine.connect() as connection:
                    df = pd.read_sql_query(sql_text(sql_query), connection)
                break # Sucesso, sai do loop

            except Exception as e:
                last_error = str(e)
                print(f"ERRO na tentativa {attempt + 1}: {last_error}")
                if attempt == MAX_RETRIES - 1:
                    raise e # Falhou em todas as tentativas

        # --- BLOCO 3.4: FORMATAÇÃO DA RESPOSTA FINAL PARA A INTERFACE ---
        num_resultados = len(df) if df is not None else 0
        resposta_final_texto = "A consulta não retornou resultados."
        if num_resultados > 0:
            preview_data = df.head(5).to_string()
            resposta_final_texto = rephrase_answer_chain.invoke({"question": pergunta, "result": preview_data})
            
        return {
            "resposta_texto": resposta_final_texto, 
            "sql_gerado": sql_query, 
            "total_resultados": num_resultados,
            "dados_com_pletos": df.to_dict(orient='records') if num_resultados > 0 else [], 
            "prompt_usado": prompt_usado
        }

    except Exception as e:
        # Tratamento de erro geral, caso algo falhe fora do ciclo de tentativas
        return {"erro": str(e), "prompt_usado": prompt_usado}

