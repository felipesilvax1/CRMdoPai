# Script para iniciar o CRM de forma organizada

Write-Host "═══════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "🚀 Iniciando CRM Stack..." -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar infraestrutura
Write-Host "1️⃣ Verificando infraestrutura..." -ForegroundColor Yellow
docker start cnpj_postgres_final 2>$null
docker start ollama 2>$null
Start-Sleep -Seconds 2
Write-Host "✅ PostgreSQL e Ollama iniciados" -ForegroundColor Green
Write-Host ""

# 2. Iniciar CRM Stack
Write-Host "2️⃣ Iniciando CRM Stack..." -ForegroundColor Yellow
docker-compose -f docker-compose.crm.yml up -d
Write-Host "✅ CRM API e LLM Service iniciados" -ForegroundColor Green
Write-Host ""

# 3. Aguardar containers ficarem prontos
Write-Host "3️⃣ Aguardando containers ficarem prontos..." -ForegroundColor Yellow
Start-Sleep -Seconds 8
Write-Host "✅ Containers prontos!" -ForegroundColor Green
Write-Host ""

# 4. Verificar saúde
Write-Host "4️⃣ Verificando saúde dos serviços..." -ForegroundColor Yellow
try {
    $apiHealth = Invoke-RestMethod -Uri "http://localhost:5000/health" -TimeoutSec 5
    Write-Host "✅ API de Dados: OK" -ForegroundColor Green
} catch {
    Write-Host "❌ API de Dados: ERRO" -ForegroundColor Red
}

try {
    $llmHealth = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 5
    Write-Host "✅ LLM Service: OK" -ForegroundColor Green
} catch {
    Write-Host "❌ LLM Service: ERRO" -ForegroundColor Red
}
Write-Host ""

# 5. Mostrar status
Write-Host "5️⃣ Status dos Containers:" -ForegroundColor Yellow
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" --filter "label=app=crm"
Write-Host ""

# 6. Informações finais
Write-Host "═══════════════════════════════════════════════" -ForegroundColor Green
Write-Host "✅ CRM Stack iniciado com sucesso!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Serviços disponíveis:" -ForegroundColor Cyan
Write-Host "  • API de Dados:  http://localhost:5000/health" -ForegroundColor White
Write-Host "  • LLM Service:   http://localhost:8000/health" -ForegroundColor White
Write-Host ""
Write-Host "🌐 Para acessar o frontend:" -ForegroundColor Cyan
Write-Host "  cd next-app" -ForegroundColor White
Write-Host "  npm run dev" -ForegroundColor White
Write-Host "  Depois abra: http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "📝 Ver logs: docker-compose -f docker-compose.crm.yml logs -f" -ForegroundColor Gray

