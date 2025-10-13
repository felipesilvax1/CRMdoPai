# Script para parar o CRM de forma organizada

Write-Host "═══════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "⏹️  Parando CRM Stack..." -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Parar CRM
Write-Host "Parando containers do CRM..." -ForegroundColor Yellow
docker-compose -f docker-compose.crm.yml down

Write-Host ""
Write-Host "✅ CRM Stack parado!" -ForegroundColor Green
Write-Host ""
Write-Host "ℹ️  Infraestrutura (PostgreSQL, Ollama, Supabase) continua rodando" -ForegroundColor Gray
Write-Host "   Para parar tudo: docker stop `$(docker ps -q)" -ForegroundColor Gray

