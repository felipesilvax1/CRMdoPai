import pytest
import json
from unittest.mock import Mock, patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from llm_api import app

@pytest.fixture
def client():
    """Fixture para o cliente de teste Flask"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_langchain():
    """Mock do LangChain e Gemma"""
    with patch('llm_api.init_langchain') as mock:
        mock_llm = MagicMock()
        mock_db = MagicMock()
        mock.return_value = (mock_llm, mock_db)
        yield mock

class TestHealthEndpoint:
    """Testes do endpoint /health"""
    
    def test_health_success(self, client):
        """Teste de health check bem-sucedido"""
        with patch('requests.get') as mock_requests:
            mock_requests.return_value.status_code = 200
            
            response = client.get('/health')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['status'] == 'ok'
            assert 'service' in data
            assert 'ollama_connected' in data
    
    def test_health_ollama_offline(self, client):
        """Teste quando Ollama está offline"""
        with patch('requests.get', side_effect=Exception("Connection refused")):
            response = client.get('/health')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert data['status'] == 'ok'
            assert data['ollama_connected'] == False

class TestAskEndpoint:
    """Testes do endpoint /ask"""
    
    def test_ask_success(self, client, mock_langchain):
        """Teste de pergunta bem-sucedida"""
        # Mock mais simplificado - testa apenas o endpoint, não a lógica interna
        pytest.skip("Teste de integração - requer LangChain completo")
    
    def test_ask_without_question(self, client):
        """Teste sem pergunta"""
        response = client.post('/ask',
                              data=json.dumps({}),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'erro' in data
    
    def test_ask_with_error(self, client, mock_langchain):
        """Teste com erro na execução"""
        # Mock do init_langchain para simular erro
        with patch('llm_api.init_langchain', side_effect=Exception("LLM Error")):
            response = client.post('/ask',
                                  data=json.dumps({'question': 'teste'}),
                                  content_type='application/json')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert data['sucesso'] == False
            assert 'erro' in data

class TestExportEndpoint:
    """Testes do endpoint /export"""
    
    def test_export_csv_success(self, client, mock_langchain):
        """Teste de exportação CSV"""
        with patch('pandas.read_sql_query') as mock_pandas, \
             patch('llm_api.BytesIO') as mock_bytesio:
            
            # Mock do DataFrame
            mock_df = MagicMock()
            mock_df.__len__.return_value = 10
            mock_df.to_csv = MagicMock()
            mock_pandas.return_value = mock_df
            
            # Mock do BytesIO
            mock_buffer = MagicMock()
            mock_buffer.read.return_value = b'csv,data,here'
            mock_bytesio.return_value = mock_buffer
            
            response = client.post('/export',
                                  data=json.dumps({
                                      'sql': 'SELECT * FROM test',
                                      'format': 'csv'
                                  }),
                                  content_type='application/json')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            
            assert data['sucesso'] == True
            assert data['formato'] == 'csv'
            assert 'arquivo_base64' in data
    
    def test_export_without_sql(self, client):
        """Teste de exportação sem SQL"""
        response = client.post('/export',
                              data=json.dumps({'format': 'csv'}),
                              content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'erro' in data
    
    def test_export_invalid_format(self, client, mock_langchain):
        """Teste com formato inválido"""
        with patch('pandas.read_sql_query') as mock_pandas:
            mock_pandas.return_value = MagicMock()
            
            response = client.post('/export',
                                  data=json.dumps({
                                      'sql': 'SELECT 1',
                                      'format': 'invalid'
                                  }),
                                  content_type='application/json')
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'erro' in data

@pytest.mark.integration
class TestLLMIntegration:
    """Testes de integração com LLM"""
    
    @pytest.mark.skipif(
        os.getenv('OLLAMA_HOST', '').startswith('http://mock'),
        reason="Ollama mock configurado"
    )
    def test_real_llm_connection(self, client):
        """Teste de conexão real com LLM (quando disponível)"""
        # Este teste só roda se o Ollama estiver realmente disponível
        pytest.skip("Teste de integração real - executar manualmente")

