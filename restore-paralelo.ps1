# ========================================
# RESTORE EM BACKGROUND
# ========================================
# ETA: 40-60 min em background
# Você pode ir jantar/dormir!

$ErrorActionPreference = "Continue"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "RESTORE EM BACKGROUND" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Verificar se dump existe
if (-not (Test-Path "cnpj_processado.dump")) {
    Write-Host "`n❌ ERRO: Arquivo cnpj_processado.dump não encontrado!" -ForegroundColor Red
    Write-Host "Execute primeiro: .\iniciar-migracao-paralela.ps1" -ForegroundColor Yellow
    exit 1
}

$dumpSize = (Get-Item cnpj_processado.dump).Length / 1GB
Write-Host "`n📦 Dump encontrado: $([math]::Round($dumpSize, 2)) GB" -ForegroundColor Green

# Verificar se container existe
$containerExists = docker ps --filter "name=crm-postgres" --format "{{.Names}}"
if ($containerExists -ne "crm-postgres") {
    Write-Host "`n❌ ERRO: Container crm-postgres não está rodando!" -ForegroundColor Red
    Write-Host "Execute primeiro: .\iniciar-migracao-paralela.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Container PostgreSQL: Rodando" -ForegroundColor Green

# Criar script de restore
$restoreScript = @"
`$ErrorActionPreference = "Continue"
`$startTime = Get-Date

Write-Host "``n========================================" -ForegroundColor Cyan
Write-Host "RESTORE EM BACKGROUND - INICIADO" -ForegroundColor Cyan
Write-Host "Hora: `$(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "``n⏳ Executando restore (40-60 min)..." -ForegroundColor Yellow
Write-Host "💤 Você pode ir jantar/dormir!" -ForegroundColor Green

# Executar restore
docker exec -i crm-postgres pg_restore -U postgres -d cnpj_processado --no-owner --no-privileges < cnpj_processado.dump

if (`$LASTEXITCODE -eq 0) {
    `$endTime = Get-Date
    `$duration = `$endTime - `$startTime
    
    Write-Host "``n========================================" -ForegroundColor Green
    Write-Host "✅ RESTORE CONCLUÍDO COM SUCESSO!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Tempo: `$([math]::Round(`$duration.TotalMinutes, 2)) minutos" -ForegroundColor White
    
    # Verificar dados
    Write-Host "``n📊 Verificando dados..." -ForegroundColor Yellow
    `$count = docker exec crm-postgres psql -U postgres -d cnpj_processado -t -c "SELECT COUNT(*) FROM estabelecimentos"
    Write-Host "Registros: `$(`$count.Trim())" -ForegroundColor Green
    
    Write-Host "``n⏭️  PRÓXIMO PASSO:" -ForegroundColor Cyan
    Write-Host "Amanhã execute: .\criar-indices-docker.ps1" -ForegroundColor Yellow
} else {
    Write-Host "``n❌ ERRO NO RESTORE!" -ForegroundColor Red
    Write-Host "Verifique os logs acima" -ForegroundColor Yellow
}

Write-Host "``nPressione qualquer tecla para fechar..." -ForegroundColor Gray
`$null = `$Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
"@

Set-Content -Path "restore-background-script.ps1" -Value $restoreScript

Write-Host "`n🚀 Iniciando restore em nova janela..." -ForegroundColor Yellow
Write-Host "💡 Você pode fechar este terminal!" -ForegroundColor Green

Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", "restore-background-script.ps1"

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "✅ RESTORE INICIADO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "`n📊 Acompanhe o progresso na janela que abriu" -ForegroundColor Cyan
Write-Host "⏳ ETA: 40-60 minutos" -ForegroundColor Yellow
Write-Host "`n💤 Você pode:" -ForegroundColor Cyan
Write-Host "  ✓ Ir jantar" -ForegroundColor White
Write-Host "  ✓ Ir dormir" -ForegroundColor White
Write-Host "  ✓ Fazer outras coisas" -ForegroundColor White
Write-Host "  ✓ O restore roda sozinho!" -ForegroundColor Green
Write-Host "`n========================================`n" -ForegroundColor Green

