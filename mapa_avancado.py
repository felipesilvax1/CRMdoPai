import pandas as pd
import folium
from folium.plugins import MarkerCluster, HeatMap
from folium.map import Layer
from jinja2 import Template
import json

# --- Configurações ---
NOME_ARQUIVO_COM_COORDENADAS = r'C:\Users\PwC\Documents\CRM\empresas_com_coordenadas_completas.csv'
NOME_ARQUIVO_MAPA = 'mapa_com_filtro_cep.html'

# --- Início do Script ---
print("Iniciando a geração do mapa final com filtro por CEP...")

# 1. Carregar os dados já geocodificados
try:
    df_geo = pd.read_csv(NOME_ARQUIVO_COM_COORDENADAS)
    print("Dados de coordenadas de rua carregados com sucesso.")
except FileNotFoundError:
    print(f"Erro Crítico: O arquivo '{NOME_ARQUIVO_COM_COORDENADAS}' não foi encontrado.")
    print("Por favor, execute a versão anterior do script ('mapa_avancado.py') primeiro para gerar este arquivo.")
    exit()

df_geo.dropna(subset=['Latitude', 'Longitude'], inplace=True)
# Garante que o CEP seja tratado como texto, preservando os zeros à esquerda
df_geo['CEP'] = df_geo['CEP'].astype(str).str.zfill(8)
print(f"{len(df_geo)} empresas com coordenadas válidas serão plotadas.")

# 2. Criar o mapa centrado em São Paulo
mapa_sp = folium.Map(location=[-23.5505, -46.6333], zoom_start=10, tiles='CartoDB positron')

# 3. Preparar os dados para o filtro
# Criamos uma estrutura GeoJson que o Folium entende bem e que pode conter propriedades (como o CEP)
features = []
for _, row in df_geo.iterrows():
    feature = {
        'type': 'Feature',
        'geometry': {
            'type':'Point', 
            'coordinates':[row['Longitude'], row['Latitude']]
        },
        'properties': {
            'cep': row['CEP'],
            'popup': f"<b>{row['Razão Social']}</b><br>CEP: {row['CEP']}<br>Endereço: {row['Endereço']}, {row['Bairro']}"
        }
    }
    features.append(feature)

geojson_data = {'type': 'FeatureCollection', 'features': features}

# 4. Adicionar os pontos ao MarkerCluster usando GeoJson
marker_cluster = MarkerCluster(name="Clientes por CEP").add_to(mapa_sp)

folium.GeoJson(
    geojson_data,
    marker=folium.Marker(icon=folium.Icon(color='blue', icon='info-sign')),
    popup=folium.GeoJsonPopup(fields=['popup']),
    name='geojson_layer'
).add_to(marker_cluster)


# 5. Adicionar o código HTML e JavaScript para o filtro
# Este bloco de código cria a caixa de busca e a lógica do filtro
html_filtro = """
<div style="position: fixed; top: 10px; right: 10px; z-index: 1000; background-color: white; padding: 10px; border-radius: 5px; box-shadow: 0 0 10px rgba(0,0,0,0.5);">
    <h4 style="margin-top: 0;">Filtrar por CEP</h4>
    <input type="text" id="cepInput" placeholder="Digite o CEP ou início...">
    <button onclick="filtrarPorCEP()">Filtrar</button>
    <button onclick="limparFiltro()">Limpar</button>
</div>
"""

js_filtro = """
<script>
    // Acessa a camada geoJson do mapa
    var geoJsonLayer = null;
    var map = {mapa_sp}; // Substituído pelo nome do objeto do mapa
    
    map.eachLayer(function(layer) {
        if (layer.options && layer.options.name === 'geojson_layer') {
            geoJsonLayer = layer;
        }
    });

    function filtrarPorCEP() {
        var cepQuery = document.getElementById('cepInput').value;
        if (!geoJsonLayer) return;

        geoJsonLayer.eachLayer(function(layer) {
            var cepFeature = layer.feature.properties.cep.toString();
            // Mostra o marcador se o CEP do marcador começar com o CEP digitado
            if (cepFeature.startsWith(cepQuery)) {
                if (!map.hasLayer(layer)) {
                     map.addLayer(layer); // Esta linha pode não funcionar bem com MarkerCluster, a abordagem de filtro é melhor
                }
                layer.getElement().style.display = '';
            } else {
                layer.getElement().style.display = 'none';
            }
        });
        // Atualiza a visualização do cluster
        geoJsonLayer.cluster.refreshClusters();
    }

    function limparFiltro() {
        document.getElementById('cepInput').value = '';
        if (!geoJsonLayer) return;

        geoJsonLayer.eachLayer(function(layer) {
            layer.getElement().style.display = '';
        });
         geoJsonLayer.cluster.refreshClusters();
    }
    
    // Pequena correção para garantir que o cluster se atualize corretamente
    var originalOnAdd = L.MarkerClusterGroup.prototype.onAdd;
    L.MarkerClusterGroup.prototype.onAdd = function (map) {
        originalOnAdd.call(this, map);
        var group = this;
        map.eachLayer(function(layer) {
            if (layer.options && layer.options.name === 'geojson_layer') {
                layer.cluster = group;
            }
        });
    };
</script>
""".replace('{mapa_sp}', mapa_sp.get_name())


# Adiciona os elementos ao mapa
mapa_sp.get_root().html.add_child(folium.Element(html_filtro))
mapa_sp.get_root().html.add_child(folium.Element(js_filtro))


# 6. Salvar o mapa final
mapa_sp.save(NOME_ARQUIVO_MAPA)

print(f"\nSucesso! Seu mapa final com filtro por CEP foi salvo como '{NOME_ARQUIVO_MAPA}'")