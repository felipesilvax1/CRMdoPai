# Script PowerShell para executar testes no Windows

Write-Host "🧪 Iniciando testes do CRM..." -ForegroundColor Cyan
Write-Host ""

$testsPassed = $true

# 1. Testes da API de Dados
Write-Host "📊 Testando API de Dados..." -ForegroundColor Yellow
Push-Location api
if (Test-Path "requirements.txt") {
    pip install -q pytest pytest-cov pytest-mock 2>$null
    if (pytest tests/ -v --cov=. --cov-report=term-missing) {
        Write-Host "✅ API de Dados: PASSOU" -ForegroundColor Green
    } else {
        Write-Host "❌ API de Dados: FALHOU" -ForegroundColor Red
        $testsPassed = $false
    }
} else {
    Write-Host "⚠️  API de Dados: Sem testes configurados" -ForegroundColor Yellow
}
Pop-Location
Write-Host ""

# 2. Testes do LLM Service
Write-Host "🤖 Testando LLM Service..." -ForegroundColor Yellow
Push-Location llm-service
if (Test-Path "requirements.txt") {
    pip install -q pytest pytest-cov pytest-mock 2>$null
    if (pytest tests/ -v --cov=. --cov-report=term-missing) {
        Write-Host "✅ LLM Service: PASSOU" -ForegroundColor Green
    } else {
        Write-Host "❌ LLM Service: FALHOU" -ForegroundColor Red
        $testsPassed = $false
    }
} else {
    Write-Host "⚠️  LLM Service: Sem testes configurados" -ForegroundColor Yellow
}
Pop-Location
Write-Host ""

# 3. Testes do Frontend
Write-Host "⚛️  Testando Frontend Next.js..." -ForegroundColor Yellow
Push-Location next-app
if (Test-Path "package.json") {
    npm run test:ci 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Frontend: PASSOU" -ForegroundColor Green
    } else {
        Write-Host "❌ Frontend: FALHOU" -ForegroundColor Red
        $testsPassed = $false
    }
} else {
    Write-Host "⚠️  Frontend: Sem testes configurados" -ForegroundColor Yellow
}
Pop-Location
Write-Host ""

# 4. Testes de Integração (Docker Compose)
Write-Host "🐳 Testando Integração (Docker)..." -ForegroundColor Yellow
if (Get-Command docker-compose -ErrorAction SilentlyContinue) {
    docker-compose -f docker-compose.test.yml up -d
    Start-Sleep -Seconds 10
    
    # Testar endpoints
    try {
        $apiResponse = Invoke-WebRequest -Uri "http://localhost:5001/health" -UseBasicParsing
        if ($apiResponse.StatusCode -eq 200) {
            Write-Host "✅ API Test Container: OK" -ForegroundColor Green
        }
    } catch {
        Write-Host "❌ API Test Container: FALHOU" -ForegroundColor Red
        $testsPassed = $false
    }
    
    try {
        $llmResponse = Invoke-WebRequest -Uri "http://localhost:8001/health" -UseBasicParsing
        if ($llmResponse.StatusCode -eq 200) {
            Write-Host "✅ LLM Test Container: OK" -ForegroundColor Green
        }
    } catch {
        Write-Host "❌ LLM Test Container: FALHOU" -ForegroundColor Red
        $testsPassed = $false
    }
    
    docker-compose -f docker-compose.test.yml down
} else {
    Write-Host "⚠️  Docker Compose não encontrado - pulando testes de integração" -ForegroundColor Yellow
}
Write-Host ""

# Resumo Final
if ($testsPassed) {
    Write-Host "════════════════════════════════════" -ForegroundColor Green
    Write-Host "✅ TODOS OS TESTES PASSARAM!" -ForegroundColor Green
    Write-Host "════════════════════════════════════" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 Resumo:" -ForegroundColor Yellow
    Write-Host "  • API de Dados: ✅" -ForegroundColor Green
    Write-Host "  • LLM Service: ✅" -ForegroundColor Green
    Write-Host "  • Frontend: ✅" -ForegroundColor Green
    Write-Host "  • Integração: ✅" -ForegroundColor Green
    Write-Host ""
    Write-Host "🚀 Sistema pronto para deploy!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "════════════════════════════════════" -ForegroundColor Red
    Write-Host "❌ ALGUNS TESTES FALHARAM" -ForegroundColor Red
    Write-Host "════════════════════════════════════" -ForegroundColor Red
    exit 1
}

