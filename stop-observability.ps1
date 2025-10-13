# ═══════════════════════════════════════════════════════════════
# 🛑 Script para Parar - Stack de Observabilidade
# ═══════════════════════════════════════════════════════════════
# Para apenas os serviços de observabilidade e LocalStack
# NÃO afeta PostgreSQL, Ollama ou outros containers
# ═══════════════════════════════════════════════════════════════

Write-Host ""
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  🛑 Parando Stack de Observabilidade do CRM" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
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
    Write-Host "  ⏸️  Parando $service..." -ForegroundColor Yellow
    docker-compose stop $service 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ $service parado" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  $service não estava rodando" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  ✅ Stack de Observabilidade Parada!" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Host "💡 Nota: PostgreSQL, Ollama e outros serviços não foram afetados" -ForegroundColor Yellow
Write-Host ""
Write-Host "🔄 Para reiniciar: " -NoNewline -ForegroundColor Cyan
Write-Host ".\start-observability.ps1" -ForegroundColor White
Write-Host ""

