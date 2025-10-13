import sqlite3
from flask import Flask, jsonify, render_template, request
import pandas as pd
import os
from tqdm import tqdm
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# --- Configurações ---
# Esta lógica calcula os caminhos baseada na localização do script
PASTA_ATUAL = os.path.dirname(os.path.abspath(__file__))
PASTA_RAIZ = os.path.dirname(PASTA_ATUAL) # A pasta CRM

# --- ALTERAÇÃO PRINCIPAL AQUI ---
# O script agora busca o banco de dados na pasta raiz (CRM), e não mais na pasta 'data'.
NOME_ARQUIVO_BANCO_DE_DADOS = os.path.join(PASTA_RAIZ, 'CNPJ_Processado.db')
NOME_ARQUIVO_CACHE_FINAL = os.path.join(PASTA_RAIZ, 'data', 'cache_coordenadas_bd.csv')

# --- DIAGNÓSTICO DE CAMINHOS ---
print("-" * 60)
print("DIAGNÓSTICO DE CAMINHOS DO SCRIPT:")
print(f"  - Pasta raiz do projeto calculada como: {PASTA_RAIZ}")
print(f"  - O script tentará abrir o banco de dados em:")
print(f"    --> {NOME_ARQUIVO_BANCO_DE_DADOS}")
print("-" * 60)

# Verificação explícita se o arquivo do banco de dados existe ANTES de tentar conectar
if not os.path.exists(NOME_ARQUIVO_BANCO_DE_DADOS):
    print("="*60)
    print("ERRO CRÍTICO: O arquivo do banco de dados NÃO FOI ENCONTRADO no caminho acima.")
    print("Por favor, verifique se:")
    print(f"  1. O nome do arquivo está exatamente como 'CNPJ_Processado.db'.")
    print(f"  2. O arquivo está localizado diretamente dentro da pasta '{PASTA_RAIZ}'.")
    print("="*60)
    exit()

# --- Funções de Processamento de Dados (sem alterações) ---

def montar_endereco_limpo(row):
    try:
        endereco = str(row['Endereco'])
        bairro = str(row['Bairro'])
        municipio = str(row['Municipio'])
        uf = str(row['UF'])
        if pd.isna(row['Bairro']):
            return f"{endereco}, {municipio}, {uf}"
        else:
            return f"{endereco}, {bairro}, {municipio}, {uf}"
    except Exception:
        return f"{row['Municipio']}, {row['UF']}"

def geocodificar_e_criar_cache():
    print("Iniciando processo único de geocodificação. Isso PODE DEMORAR BASTANTE na primeira vez.")
    try:
        conexao = sqlite3.connect(NOME_ARQUIVO_BANCO_DE_DADOS)
        consulta_sql = """
        SELECT 
            emp.razao_social,
            est.nome_fantasia,
            emp.porte_empresa,
            est.logradouro || ', ' || est.numero AS "Endereco",
            est.bairro,
            est.municipio,
            est.uf,
            est.cep,
            est.ddd_1 || est.telefone_1 AS "Telefone_1",
            cna.descricao AS "CNAE_Principal_Descricao"
        FROM estabelecimentos est
        LEFT JOIN empresas emp ON est.cnpj_basico = emp.cnpj_basico
        LEFT JOIN cnaes cna ON est.cnae_fiscal_principal = cna.codigo
        WHERE est.uf = 'SP';
        """
        print("Executando consulta no banco de dados...")
        df_bd = pd.read_sql_query(consulta_sql, conexao)
        conexao.close()
        
        df_bd.columns = ['Razão Social', 'Nome Fantasia', 'Porte da Empresa', 'Endereço', 
                         'Bairro', 'Municipio', 'UF', 'CEP', 'Telefone 1', 'CNAE Principal (Descrição)']

        print(f"{len(df_bd)} registros encontrados. Preparando para geocodificar...")
        df_bd['Endereco_Limpo'] = df_bd.apply(montar_endereco_limpo, axis=1)

        geolocator = Nominatim(user_agent="mapa_app_gerador_cache")
        geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1.1, error_wait_seconds=10)
        latitudes, longitudes = [], []

        for endereco in tqdm(df_bd['Endereco_Limpo'], desc="Buscando coordenadas"):
            try:
                location = geocode(endereco, timeout=10)
                latitudes.append(location.latitude if location else None)
                longitudes.append(location.longitude if location else None)
            except Exception as e:
                print(f"Erro em '{endereco}': {e}"); latitudes.append(None); longitudes.append(None)

        df_bd['Latitude'] = latitudes
        df_bd['Longitude'] = longitudes
        
        print(f"Geocodificação concluída. Salvando cache em '{NOME_ARQUIVO_CACHE_FINAL}'...")
        # Garante que a pasta 'data' existe antes de salvar o cache
        os.makedirs(os.path.dirname(NOME_ARQUIVO_CACHE_FINAL), exist_ok=True)
        df_bd.to_csv(NOME_ARQUIVO_CACHE_FINAL, index=False)
        return df_bd

    except Exception as e:
        print(f"Ocorreu um erro fatal durante o processamento dos dados: {e}")
        exit()


# --- Lógica Principal de Inicialização ---
if not os.path.exists(NOME_ARQUIVO_CACHE_FINAL):
    print("AVISO: Arquivo de cache com coordenadas não encontrado!")
    df_geo = geocodificar_e_criar_cache()
else:
    print("Arquivo de cache encontrado. Carregando dados para a memória...")
    df_geo = pd.read_csv(NOME_ARQUIVO_CACHE_FINAL)

df_geo.dropna(subset=['Latitude', 'Longitude'], inplace=True)
print(f"{len(df_geo)} empresas carregadas e prontas para servir.")


# --- Inicialização do Servidor Flask ---
pasta_templates_abs = os.path.abspath(os.path.join(PASTA_RAIZ, 'frontend', 'templates'))
app = Flask(__name__, template_folder=pasta_templates_abs)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/empresas')
def get_empresas():
    try:
        bounds = {k: float(v) for k, v in request.args.items()}
        df_filtrado = df_geo[
            (df_geo['Latitude'] <= bounds['north']) & (df_geo['Latitude'] >= bounds['south']) &
            (df_geo['Longitude'] <= bounds['east']) & (df_geo['Longitude'] >= bounds['west'])
        ]
        if len(df_filtrado) > 2000:
            df_filtrado = df_filtrado.sample(n=2000)
        return jsonify(df_filtrado.to_dict(orient='records'))
    except (TypeError, ValueError, KeyError):
        return jsonify({"error": "Parâmetros de geolocalização inválidos."}), 400

if __name__ == '__main__':
    print("\nServidor pronto!")
    print("Abra seu navegador e acesse: http://127.0.0.1:5000")
    app.run(debug=True, host='0.0.0.0')

