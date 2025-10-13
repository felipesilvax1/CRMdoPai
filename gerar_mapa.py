import pandas as pd
import folium
from folium.plugins import HeatMap
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time

# Carrega a planilha do Excel (CORRIGIDO)
df = pd.read_excel(r'C:\Users\PwC\Documents\CRM\Relatorio_Empresas_2025_09_13.xlsx', header=1)

# Agrupa por Município e UF para contar as empresas
location_counts = df.groupby(['Município', 'UF']).size().reset_index(name='count')

# Ordena para pegar as top 10 com mais empresas
top_10_locations = location_counts.sort_values(by='count', ascending=False).head(10)

# Geocodificação dos endereços
geolocator = Nominatim(user_agent="heatmap_app")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

top_10_locations['location'] = top_10_locations['Município'] + ', ' + top_10_locations['UF']
top_10_locations['point'] = top_10_locations['location'].apply(geocode)
top_10_locations['latitude'] = top_10_locations['point'].apply(lambda loc: loc.latitude if loc else None)
top_10_locations['longitude'] = top_10_locations['point'].apply(lambda loc: loc.longitude if loc else None)

# Cria o mapa
mapa = folium.Map(location=[-14.2350, -51.9253], zoom_start=4)

# Adiciona o mapa de calor
heat_data = [[row['latitude'], row['longitude'], row['count']] for index, row in top_10_locations.iterrows() if pd.notnull(row['latitude'])]
HeatMap(heat_data).add_to(mapa)

# Salva o mapa em um arquivo HTML
mapa.save('mapa_de_calor_clientes.html')

print("Mapa de calor salvo como 'mapa_de_calor_clientes.html'")
print("\nTop 10 Cidades/Regiões com mais clientes:")
print(top_10_locations[['Município', 'UF', 'count']])