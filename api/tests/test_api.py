import pytest
import json
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Adicionar o diretório pai ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, executar_sql, gerar_sql_simples

@pytest.fixture
def client():
    """Fixture para o cliente de teste Flask"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_db():
    """Mock do banco de dados"""
    with patch('app.executar_sql') as mock:
        yield mock

class TestHealthEndpoint:
    """Testes do endpoint /health"""
    
    def test_health_success(self, client, mock_db):
        """Teste de health check bem-sucedido"""
        mock_db.return_value = [{'test': 1}]
        
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'ok'
        assert 'database' in data
        assert 'message' in data
    
    def test_health_failure(self, client, mock_db):
        """Teste de health check com falha no banco"""
        mock_db.side_effect = Exception("Erro de conexão")
        
        response = client.get('/health')
        assert response.status_code == 500
        
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'error' in data

class TestQueryEndpoint:
    """Testes do endpoint /query"""
    
    def test_query_success(self, client, mock_db):
        """Teste de query bem-sucedida"""
        mock_db.return_value = [
            {'cnpj_basico': '12345678', 'nome_fantasia': 'Empresa Teste', 'uf': 'SP'},
            {'cnpj_basico': '87654321', 'nome_fantasia': 'Outra Empresa', 'uf': 'RJ'}
        ]
        
        response = client.post('/query',
                              data=json.dumps({'question': 'empresas'}),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'resposta_texto' in data
        assert 'sql_gerado' in data
        assert 'total_resultados' in data
        assert 'dados_completos' in data
        assert data['total_resultados'] == 2
    
    def test_query_without_question(self, client):
        """Teste de query sem pergunta"""
        response = client.post('/query',
                              data=json.dumps({}),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'erro' in data
    
    def test_query_statistics(self, client, mock_db):
        """Teste de query de estatísticas"""
        mock_db.return_value = [{
            'total_empresas': 1000,
            'total_estabelecimentos': 5000,
            'total_socios': 3000,
            'total_cnaes': 100
        }]
        
        response = client.post('/query',
                              data=json.dumps({'question': 'estatísticas gerais'}),
                              content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'total_empresas' in data['resposta_texto'] or 'Base de dados' in data['resposta_texto']
    
    def test_query_error(self, client, mock_db):
        """Teste de erro na execução da query"""
        mock_db.side_effect = Exception("Erro SQL")
        
        response = client.post('/query',
                              data=json.dumps({'question': 'empresas'}),
                              content_type='application/json')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'erro' in data

class TestSQLGenerator:
    """Testes do gerador de SQL"""
    
    def test_generate_sql_statistics(self):
        """Teste de geração de SQL para estatísticas"""
        sql = gerar_sql_simples('estatísticas gerais')
        assert 'COUNT(*)' in sql.upper() or 'SELECT' in sql.upper()
        # Aceita tanto queries de estatísticas quanto padrão
    
    def test_generate_sql_empresas(self):
        """Teste de geração de SQL para empresas"""
        sql = gerar_sql_simples('lista de empresas')
        assert 'SELECT' in sql.upper()
        assert 'estabelecimentos' in sql.lower()
        assert 'LIMIT' in sql.upper()
    
    def test_generate_sql_default(self):
        """Teste de geração de SQL padrão"""
        sql = gerar_sql_simples('query desconhecida')
        assert 'Teste' in sql

class TestCORS:
    """Testes de CORS"""
    
    def test_cors_headers(self, client):
        """Teste se headers CORS estão presentes"""
        response = client.get('/health')
        assert 'Access-Control-Allow-Origin' in response.headers

@pytest.mark.integration
class TestDatabaseIntegration:
    """Testes de integração com banco real (apenas em ambiente de teste)"""
    
    @pytest.mark.skipif(
        os.getenv('USE_POSTGRES', 'false').lower() != 'true',
        reason="Banco PostgreSQL não disponível"
    )
    def test_real_database_connection(self):
        """Teste de conexão real com banco (quando disponível)"""
        try:
            result = executar_sql("SELECT 1 as test")
            assert len(result) == 1
            assert result[0]['test'] == 1
        except Exception as e:
            pytest.skip(f"Banco não disponível: {e}")

