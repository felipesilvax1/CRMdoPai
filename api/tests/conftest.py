import pytest
import os

# Configurar variáveis de ambiente para testes
os.environ['USE_POSTGRES'] = 'true'
os.environ['DB_HOST'] = os.getenv('DB_HOST', 'localhost')
os.environ['DB_PORT'] = os.getenv('DB_PORT', '5432')
os.environ['DB_NAME'] = os.getenv('DB_NAME', 'test_db')
os.environ['DB_USER'] = os.getenv('DB_USER', 'postgres')
os.environ['DB_PASSWORD'] = os.getenv('DB_PASSWORD', 'test_password')

def pytest_configure(config):
    """Configuração inicial do pytest"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )

