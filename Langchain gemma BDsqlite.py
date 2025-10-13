# -*- coding: utf-8 -*-

# --- Passo 1: Importar bibliotecas padrão e verificar dependências ---
import os
import sys
import subprocess
import importlib.util
import tkinter as tk
from tkinter import filedialog
from operator import itemgetter

def verificar_e_instalar_pacotes():
    """
    Verifica se os pacotes necessários estão instalados
    e, se não estiverem, tenta instalá-los usando o pip.
    """
    pacotes_necessarios = {
        'langchain_community': 'langchain-community',
        'langchain_experimental': 'langchain-experimental',
        'sqlalchemy': 'SQLAlchemy',
        'langchain_ollama': 'langchain-ollama',
        'pandas': 'pandas',
        'reportlab': 'reportlab'
    }
    pacotes_faltando = []
    
    print("Verificando dependências...")
    for nome_modulo, nome_instalacao in pacotes_necessarios.items():
        if importlib.util.find_spec(nome_modulo) is None:
            pacotes_faltando.append(nome_instalacao)

    if pacotes_faltando:
        print(f"Pacotes faltando detectados: {', '.join(pacotes_faltando)}")
        print("Iniciando instalação automática (isso pode levar alguns minutos)...")
        
        try:
            python_executable = sys.executable
            subprocess.check_call([python_executable, '-m', 'pip', 'install', '-U', *pacotes_faltando])
            
            print("\nInstalação concluída com sucesso!")
            print("É necessário executar o script novamente para carregar as bibliotecas.")
            sys.exit()
            
        except subprocess.CalledProcessError as e:
            print(f"\nFalha ao instalar os pacotes: {e}")
            print("Por favor, instale-os manualmente com o comando:")
            print(f"pip install -U {' '.join(pacotes_faltando)}")
            sys.exit(1)
    else:
        print("Todas as dependências necessárias já estão instaladas.\n")

# --- Funções de Exportação ---
def exportar_para_csv(dataframe, nome_arquivo):
    """Salva um DataFrame do pandas em um arquivo CSV."""
    try:
        dataframe.to_csv(nome_arquivo, index=False, encoding='utf-8-sig')
        print(f"Arquivo '{nome_arquivo}' salvo com sucesso!")
    except Exception as e:
        print(f"Erro ao salvar CSV: {e}")

def exportar_para_pdf(dataframe, nome_arquivo):
    """Salva um DataFrame do pandas em um arquivo PDF."""
    try:
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import landscape, letter

        doc = SimpleDocTemplate(nome_arquivo, pagesize=landscape(letter))
        elementos = []
        
        styles = getSampleStyleSheet()
        elementos.append(Paragraph("Relatório de Consulta", styles['h1']))

        # Converte os dados do DataFrame para uma lista de listas
        dados_tabela = [dataframe.columns.tolist()] + dataframe.values.tolist()
        
        # Limita o tamanho das células para evitar quebras de página ruins
        for i, row in enumerate(dados_tabela):
            for j, cell in enumerate(row):
                dados_tabela[i][j] = str(cell)[:80] # Trunca células muito longas

        tabela = Table(dados_tabela)
        
        # Estilo da tabela
        estilo = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ])
        
        tabela.setStyle(estilo)
        elementos.append(tabela)
        
        doc.build(elementos)
        print(f"Arquivo '{nome_arquivo}' salvo com sucesso!")

    except Exception as e:
        print(f"Erro ao salvar PDF: {e}")


def selecionar_arquivo_db():
    """
    Abre uma janela de diálogo para o usuário selecionar um arquivo de banco de dados.
    """
    print("Abrindo janela para selecionar o arquivo do banco de dados...")
    root = tk.Tk()
    root.withdraw()
    
    tipos_de_arquivo = [("Bancos de dados SQLite", "*.db *.sqlite *.sqlite3"), ("Todos os arquivos", "*.*")]
    
    caminho_do_arquivo = filedialog.askopenfilename(
        title="Selecione o seu banco de dados SQLite", filetypes=tipos_de_arquivo
    )
    
    return caminho_do_arquivo

def main():
    """
    Função principal que orquestra a conexão com o DB, o LLM e o loop de perguntas.
    """
    verificar_e_instalar_pacotes()
    
    # Importações dinâmicas após a verificação
    from langchain_community.utilities import SQLDatabase
    from langchain.chains import create_sql_query_chain
    from langchain.prompts import PromptTemplate
    from langchain_ollama.llms import OllamaLLM
    from langchain_core.output_parsers import StrOutputParser
    import pandas as pd
    from sqlalchemy import text as sql_text

    caminho_do_banco = selecionar_arquivo_db()
    if not caminho_do_banco:
        print("Nenhum arquivo selecionado. Encerrando o programa.")
        return

    print(f"\nBanco de dados selecionado: {caminho_do_banco}\n")

    try:
        db = SQLDatabase.from_uri(f"sqlite:///{caminho_do_banco}")
        llm = OllamaLLM(model="gemma:latest", temperature=0)

        PROMPT_TEMPLATE = """Dada uma pergunta do usuário, crie uma consulta SQL para o dialeto SQLite sintaticamente correta para executá-la. Apenas retorne a consulta SQL, sem nenhum texto adicional antes ou depois.

Esquema do banco de dados:
{table_info}

Pergunta: {input}
Consulta SQL:"""
        
        prompt = PromptTemplate(
            input_variables=["input", "table_info"], template=PROMPT_TEMPLATE
        )
        generate_query_chain = create_sql_query_chain(llm, db, prompt=prompt)
        
        answer_prompt = PromptTemplate.from_template(
            """Dada a seguinte pergunta do usuário, a consulta SQL correspondente e uma amostra do resultado da consulta, responda à pergunta do usuário em português.

Pergunta: {question}
Consulta SQL: {query}
Amostra do Resultado da Consulta SQL: {result}
Resposta:"""
        )
        rephrase_answer_chain = answer_prompt | llm | StrOutputParser()

        print("\n--- Tudo pronto! ---")
        print('Digite "sair" a qualquer momento para terminar.')

        while True:
            pergunta = input("\nSua pergunta: ")
            if pergunta.lower() == 'sair':
                print("Até mais!")
                break
            
            try:
                # 1. Gerar a consulta SQL
                sql_query = generate_query_chain.invoke({"question": pergunta})
                print(f"\n--- SQL Gerado ---\n{sql_query.strip()}")

                # 2. Executar a consulta e obter os dados como um DataFrame do Pandas
                with db.get_dialect().connect() as connection:
                    df = pd.read_sql_query(sql_text(sql_query), connection)

                num_resultados = len(df)

                if num_resultados > 0:
                    # 3. Gerar a resposta em texto usando o resultado
                    preview_data = df.head(5).to_string()
                    
                    contexto_resposta = {"question": pergunta, "query": sql_query, "result": preview_data}
                    
                    print("\n--- Resposta do Gemma ---")
                    for chunk in rephrase_answer_chain.stream(contexto_resposta):
                        print(chunk, end="", flush=True)
                    print("\n")

                    # 4. Mostrar contagem e perguntar sobre exportação
                    print(f"Foram encontrados {num_resultados} resultados.")
                    
                    exportar = input("Deseja exportar os resultados completos? (s/n): ").lower()
                    if exportar == 's':
                        formato = input("Qual formato? (csv/pdf): ").lower()
                        nome_arquivo_base = input("Digite o nome base para o arquivo: ")
                        
                        if formato == 'csv':
                            exportar_para_csv(df, f"{nome_arquivo_base}.csv")
                        elif formato == 'pdf':
                            exportar_para_pdf(df, f"{nome_arquivo_base}.pdf")
                        else:
                            print("Formato inválido.")
                else:
                    print("\n--- Resposta do Gemma ---")
                    print("A consulta não retornou resultados.")

            except Exception as e:
                print(f"\n\nOcorreu um erro ao processar sua pergunta: {e}")

    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")

if __name__ == "__main__":
    main()

