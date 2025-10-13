import pandas as pd
import folium
from folium.plugins import MarkerCluster
import time
import os
import sqlite3 # Biblioteca para conectar com o banco de dados
from tqdm import tqdm
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# --- Configurações ---
# Caminho completo para o seu banco de dados.
NOME_ARQUIVO_BANCO_DE_DADOS = r'C:\Users\PwC\Documents\CRM\CNPJ_Processado.db' 
NOME_ARQUIVO_CACHE_FINAL = r'C:\Users\PwC\Documents\CRM\cache_coordenadas_bd.csv' # Arquivo de cache para não buscar coordenadas repetidamente
NOME_ARQUIVO_MAPA = 'mapa_prospeccao_banco_de_dados.html'

# --- FUNÇÃO DE LIMPEZA DE ENDEREÇO (adaptada para colunas do BD) ---
def montar_endereco_limpo(row):
    """Monta uma string de endereço limpa para a geocodificação."""
    try:
        endereco = str(row['Endereço'])
        bairro = str(row['Bairro'])
        municipio = str(row['Município'])
        uf = str(row['UF'])

        if pd.isna(row['Bairro']):
            return f"{endereco}, {municipio}, {uf}"
        else:
            return f"{endereco}, {bairro}, {municipio}, {uf}"
    except Exception:
        return f"{row['Município']}, {row['UF']}"

# --- FUNÇÃO DE GEOCIDIFICAÇÃO (sem alterações) ---
def geocodificar_enderecos(df):
    """Busca as coordenadas geográficas para uma lista de endereços, usando cache para acelerar."""
    if os.path.exists(NOME_ARQUIVO_CACHE_FINAL):
        print(f"Arquivo de cache '{NOME_ARQUIVO_CACHE_FINAL}' encontrado. Carregando dados...")
        return pd.read_csv(NOME_ARQUIVO_CACHE_FINAL)

    print("Iniciando geocodificação de precisão a partir dos dados do banco (pode demorar na primeira vez)...")
    geolocator = Nominatim(user_agent="mapa_final_bd_precisao")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1.1, error_wait_seconds=10)
    latitudes = []
    longitudes = []

    for endereco in tqdm(df['Endereco_Limpo'], desc="Buscando coordenadas de rua"):
        try:
            location = geocode(endereco, timeout=10)
            if location: latitudes.append(location.latitude); longitudes.append(location.longitude)
            else: latitudes.append(None); longitudes.append(None)
        except Exception as e:
            print(f"Erro em '{endereco}': {e}"); latitudes.append(None); longitudes.append(None)

    df['Latitude'] = latitudes
    df['Longitude'] = longitudes
    df.to_csv(NOME_ARQUIVO_CACHE_FINAL, index=False)
    print(f"Geocodificação concluída. Dados salvos em '{NOME_ARQUIVO_CACHE_FINAL}' para uso futuro.")
    return df

# --- Processamento Principal ---
print("Iniciando a geração do mapa a partir do Banco de Dados...")

# 1. Conectar ao banco de dados e carregar os dados
try:
    print(f"Conectando ao banco de dados em '{NOME_ARQUIVO_BANCO_DE_DADOS}'...")
    conexao = sqlite3.connect(NOME_ARQUIVO_BANCO_DE_DADOS)
    
    # Consulta SQL para unir as tabelas e pegar os dados de SP
    # CORREÇÃO FINAL: Alterado "cnpj basico" para cnpj_basico na cláusula ON
    consulta_sql = """
    SELECT 
        emp.razao_social AS "Razao_Social",
        est.nome_fantasia AS "Nome_Fantasia",
        emp.porte_empresa AS "Porte_Empresa",
        est.logradouro || ', ' || est.numero AS "Endereco",
        est.bairro AS "Bairro",
        est.municipio AS "Municipio",
        est.uf AS "UF",
        est.cep AS "CEP",
        est.ddd_1 || est.telefone_1 AS "Telefone_1",
        cna.descricao AS "CNAE_Principal_Descricao"
    FROM 
        estabelecimentos est
    LEFT JOIN 
        empresas emp ON est.cnpj_basico = emp.cnpj_basico
    LEFT JOIN 
        cnaes cna ON est.cnae_fiscal_principal = cna.codigo
    WHERE 
        est.uf = 'SP';
    """
    
    print("Executando consulta no banco...")
    df_bd = pd.read_sql_query(consulta_sql, conexao)
    conexao.close()
    print(f"{len(df_bd)} registros de empresas em SP encontrados no banco.")
    
    # Renomeando colunas para o padrão que o resto do script espera
    df_bd.columns = ['Razão Social', 'Nome Fantasia', 'Porte da Empresa', 'Endereço', 
                     'Bairro', 'Município', 'UF', 'CEP', 'Telefone 1', 'CNAE Principal (Descrição)']

    # 2. Preparar e geocodificar os dados
    print("Preparando endereços para geocodificação...")
    df_bd['Endereco_Limpo'] = df_bd.apply(montar_endereco_limpo, axis=1)
    df_geo = geocodificar_enderecos(df_bd.copy())

except Exception as e:
    print(f"Ocorreu um erro ao conectar ou ler o banco de dados: {e}")
    exit()

df_geo.dropna(subset=['Latitude', 'Longitude'], inplace=True)
df_geo['CEP'] = df_geo['CEP'].astype(str).str.zfill(8)
print(f"{len(df_geo)} empresas com coordenadas válidas serão plotadas.")

# 3. Criar o mapa
mapa = folium.Map(location=[-23.5505, -46.6333], zoom_start=10, tiles='CartoDB positron')

# 4. Adicionar marcadores em cluster com pop-ups ricos em informação
marker_cluster = MarkerCluster(name="Empresas").add_to(mapa)
for _, row in df_geo.iterrows():
    popup_html = f"""
    <div style='width: 350px;'>
        <h4 style='margin-bottom:5px; color:#003366;'>{row['Razão Social']}</h4>
        """
    if pd.notna(row['Nome Fantasia']):
        popup_html += f"<i>{row['Nome Fantasia']}</i><br>"
    popup_html += f"""
        <hr style='margin: 5px 0;'>
        <b>Porte:</b> {row['Porte da Empresa']}<br>
        <b>Telefone:</b> {row['Telefone 1']}<br>
        <b>Atividade Principal:</b> {row['CNAE Principal (Descrição)']}<br>
        <hr style='margin: 5px 0;'>
        <b>CEP:</b> {row['CEP']}<br>
        <b>Endereço:</b> {row['Endereco_Limpo']}
    </div>
    """
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=folium.Popup(popup_html, max_width=400),
        icon=folium.Icon(color='darkblue', icon='building', prefix='fa')
    ).add_to(marker_cluster)

# 5. Salvar o mapa
mapa.save(NOME_ARQUIVO_MAPA)
print(f"\nSucesso! Seu mapa final, alimentado pelo banco de dados, foi salvo como '{NOME_ARQUIVO_MAPA}'")

