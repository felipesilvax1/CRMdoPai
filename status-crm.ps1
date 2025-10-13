# Script para ver status do CRM

Write-Host "═══════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "📊 Status do CRM" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Host "🎯 CRM Stack:" -ForegroundColor Yellow
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" --filter "label=app=crm"
Write-Host ""

Write-Host "🏗️  Infraestrutura:" -ForegroundColor Yellow
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" --filter "name=postgres"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" --filter "name=ollama"
Write-Host ""

Write-Host "🔍 Supabase (se estiver rodando):" -ForegroundColor Yellow
$supabase = docker ps --filter "name=supabase" --format "{{.Names}}" | Measure-Object
Write-Host "  $($supabase.Count) containers Supabase ativos" -ForegroundColor Gray
Write-Host ""

Write-Host "💾 Uso de Recursos:" -ForegroundColor Yellow
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" crm-api crm-llm 2>$null
Write-Host ""

Write-Host "🌐 Health Checks:" -ForegroundColor Yellow
try {
    $api = Invoke-RestMethod -Uri "http://localhost:5000/health" -TimeoutSec 2
    Write-Host "  ✅ API: $($api.status)" -ForegroundColor Green
} catch {
    Write-Host "  ❌ API: Offline" -ForegroundColor Red
}

try {
    $llm = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 2
    Write-Host "  ✅ LLM: $($llm.status) - Ollama: $($llm.ollama_connected)" -ForegroundColor Green
} catch {
    Write-Host "  ❌ LLM: Offline" -ForegroundColor Red
}

