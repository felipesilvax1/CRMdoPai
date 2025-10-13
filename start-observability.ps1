# ═══════════════════════════════════════════════════════════════
# 🚀 Script de Inicialização - Stack de Observabilidade
# ═══════════════════════════════════════════════════════════════
# Inicia apenas os serviços de observabilidade e LocalStack
# NÃO afeta PostgreSQL, Ollama ou outros containers já rodando
# ═══════════════════════════════════════════════════════════════

Write-Host ""
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  🚀 Iniciando Stack de Observabilidade do CRM" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Verifica se Docker está rodando
Write-Host "🔍 Verificando Docker..." -ForegroundColor Yellow
$dockerRunning = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker não está rodando!" -ForegroundColor Red
    Write-Host "   Por favor, inicie o Docker Desktop e tente novamente." -ForegroundColor Red
    exit 1
}
Write-Host "✅ Docker está rodando" -ForegroundColor Green
Write-Host ""

# Iniciar serviços de observabilidade
Write-Host "📊 Iniciando serviços de observabilidade..." -ForegroundColor Yellow
Write-Host ""

$services = @(
    "prometheus",
    "loki",
    "promtail",
    "grafana",
    "cadvisor",
    "localstack"
)

foreach ($service in $services) {
    Write-Host "  ⚡ Iniciando $service..." -ForegroundColor Cyan
    docker-compose up -d $service 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ $service iniciado" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  Erro ao iniciar $service" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "⏳ Aguardando serviços ficarem prontos..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Verificar status
Write-Host ""
Write-Host "📋 Status dos serviços:" -ForegroundColor Yellow
docker-compose ps prometheus loki promtail grafana cadvisor localstack

Write-Host ""
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  ✅ Stack de Observabilidade Iniciada!" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Host "🌐 URLs de Acesso:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  📊 Grafana:      " -NoNewline -ForegroundColor White
Write-Host "http://localhost:3002" -ForegroundColor Green
Write-Host "                   Login: admin / Senha: admin" -ForegroundColor Gray
Write-Host ""
Write-Host "  📈 Prometheus:   " -NoNewline -ForegroundColor White
Write-Host "http://localhost:9090" -ForegroundColor Green
Write-Host ""
Write-Host "  📝 Loki:         " -NoNewline -ForegroundColor White
Write-Host "http://localhost:3100" -ForegroundColor Green
Write-Host ""
Write-Host "  📦 cAdvisor:     " -NoNewline -ForegroundColor White
Write-Host "http://localhost:8080" -ForegroundColor Green
Write-Host ""
Write-Host "  ☁️  LocalStack:   " -NoNewline -ForegroundColor White
Write-Host "http://localhost:4566" -ForegroundColor Green
Write-Host ""

Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Host "📝 Próximos Passos:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  1. Iniciar frontend:" -ForegroundColor White
Write-Host "     cd next-app" -ForegroundColor Gray
Write-Host "     npm run dev" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. Acessar Grafana e explorar o dashboard CRM - Overview" -ForegroundColor White
Write-Host ""
Write-Host "  3. Ver métricas em tempo real:" -ForegroundColor White
Write-Host "     http://localhost:3000/api/metrics" -ForegroundColor Gray
Write-Host ""
Write-Host "  4. Quando terminar importação do BD, iniciar API e LLM:" -ForegroundColor White
Write-Host "     docker-compose up -d crm-api crm-llm" -ForegroundColor Gray
Write-Host ""

Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 Dica: Use " -NoNewline -ForegroundColor Yellow
Write-Host "docker-compose logs -f grafana" -NoNewline -ForegroundColor White
Write-Host " para ver logs" -ForegroundColor Yellow
Write-Host ""
Write-Host "📖 Documentação: " -NoNewline -ForegroundColor Yellow
Write-Host "INICIAR_OBSERVABILIDADE.md" -ForegroundColor White
Write-Host ""

