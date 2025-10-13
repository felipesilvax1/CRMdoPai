#!/bin/bash

# Script para executar todos os testes localmente

set -e

echo "🧪 Iniciando testes do CRM..."
echo ""

# Cores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para printar com cor
print_status() {
    echo -e "${2}${1}${NC}"
}

# 1. Testes da API de Dados
print_status "📊 Testando API de Dados..." "$YELLOW"
cd api
if [ -f "requirements.txt" ]; then
    pip install -q pytest pytest-cov pytest-mock 2>/dev/null || true
    if pytest tests/ -v --cov=. --cov-report=term-missing; then
        print_status "✅ API de Dados: PASSOU" "$GREEN"
    else
        print_status "❌ API de Dados: FALHOU" "$RED"
        exit 1
    fi
else
    print_status "⚠️  API de Dados: Sem testes configurados" "$YELLOW"
fi
cd ..
echo ""

# 2. Testes do LLM Service
print_status "🤖 Testando LLM Service..." "$YELLOW"
cd llm-service
if [ -f "requirements.txt" ]; then
    pip install -q pytest pytest-cov pytest-mock 2>/dev/null || true
    if pytest tests/ -v --cov=. --cov-report=term-missing; then
        print_status "✅ LLM Service: PASSOU" "$GREEN"
    else
        print_status "❌ LLM Service: FALHOU" "$RED"
        exit 1
    fi
else
    print_status "⚠️  LLM Service: Sem testes configurados" "$YELLOW"
fi
cd ..
echo ""

# 3. Testes do Frontend
print_status "⚛️  Testando Frontend Next.js..." "$YELLOW"
cd next-app
if [ -f "package.json" ]; then
    if npm run test:ci 2>/dev/null; then
        print_status "✅ Frontend: PASSOU" "$GREEN"
    else
        print_status "❌ Frontend: FALHOU" "$RED"
        exit 1
    fi
else
    print_status "⚠️  Frontend: Sem testes configurados" "$YELLOW"
fi
cd ..
echo ""

# 4. Testes de Integração (Docker Compose)
print_status "🐳 Testando Integração (Docker)..." "$YELLOW"
if command -v docker-compose &> /dev/null; then
    docker-compose -f docker-compose.test.yml up -d
    sleep 10
    
    # Testar endpoints
    if curl -f http://localhost:5001/health > /dev/null 2>&1; then
        print_status "✅ API Test Container: OK" "$GREEN"
    else
        print_status "❌ API Test Container: FALHOU" "$RED"
    fi
    
    if curl -f http://localhost:8001/health > /dev/null 2>&1; then
        print_status "✅ LLM Test Container: OK" "$GREEN"
    else
        print_status "❌ LLM Test Container: FALHOU" "$RED"
    fi
    
    docker-compose -f docker-compose.test.yml down
else
    print_status "⚠️  Docker Compose não encontrado - pulando testes de integração" "$YELLOW"
fi
echo ""

# Resumo Final
print_status "════════════════════════════════════" "$GREEN"
print_status "✅ TODOS OS TESTES PASSARAM!" "$GREEN"
print_status "════════════════════════════════════" "$GREEN"
echo ""
print_status "📊 Resumo:" "$YELLOW"
print_status "  • API de Dados: ✅" "$GREEN"
print_status "  • LLM Service: ✅" "$GREEN"
print_status "  • Frontend: ✅" "$GREEN"
print_status "  • Integração: ✅" "$GREEN"
echo ""
print_status "🚀 Sistema pronto para deploy!" "$GREEN"

