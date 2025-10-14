import requests

# Testar endpoint /query/avancada
response = requests.get('http://192.168.15.22:5000/query/avancada', params={
    'uf': 'SP',
    'municipio': 'CARAPICUIBA',
    'bairro': 'ARISTON',
    'situacao': '02',
    'limit': 5
})

print(f"Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"Total: {data.get('total', 0)}")
    print(f"Encontrados: {len(data.get('dados', []))}")
    
    if len(data.get('dados', [])) > 0:
        print("\nPrimeiras empresas:")
        for empresa in data['dados'][:3]:
            print(f"  - {empresa.get('razao_social', 'N/A')}")
            print(f"    CNPJ: {empresa.get('cnpj', 'N/A')}")
            print(f"    {empresa.get('bairro', 'N/A')}, {empresa.get('municipio_nome', empresa.get('municipio', 'N/A'))}/{empresa.get('uf', 'N/A')}")
else:
    print(f"Erro: {response.text}")

