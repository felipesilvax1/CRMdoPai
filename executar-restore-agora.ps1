# ========================================
# RESTORE IMEDIATO - MODO BACKGROUND
# ========================================

$ErrorActionPreference = "Continue"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "RESTORE - INICIANDO AGORA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Hora: $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Gray

# Verificar dump
if (-not (Test-Path "cnpj_processado.dump")) {
    Write-Host "`n❌ Arquivo dump não encontrado!" -ForegroundColor Red
    exit 1
}

$dumpSize = (Get-Item cnpj_processado.dump).Length / 1GB
Write-Host "`n📦 Dump: $([math]::Round($dumpSize, 2)) GB" -ForegroundColor Green

# Iniciar restore
Write-Host "`n⏳ Executando restore (40-60 min)..." -ForegroundColor Yellow
Write-Host "   Usando 4 jobs paralelos para acelerar" -ForegroundColor Gray
Write-Host "`n========================================`n" -ForegroundColor Cyan

$startTime = Get-Date

# Executar restore usando Get-Content para pipe
try {
    Get-Content -Path "cnpj_processado.dump" -Raw -ReadCount 0 | docker exec -i crm-postgres pg_restore -U postgres -d cnpj_processado --no-owner --no-privileges --jobs=4 -v 2>&1 | Tee-Object -FilePath "restore_progress.log"
    
    $endTime = Get-Date
    $duration = $endTime - $startTime
    
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "✅ RESTORE CONCLUÍDO!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Tempo: $([math]::Round($duration.TotalMinutes, 1)) minutos`n" -ForegroundColor White
    
    # Verificar dados
    Write-Host "📊 Verificando dados..." -ForegroundColor Yellow
    $count = docker exec crm-postgres psql -U postgres -d cnpj_processado -t -c "SELECT COUNT(*) FROM estabelecimentos" 2>&1
    
    if ($count -match '\d+') {
        Write-Host "✅ Registros: $($count.Trim())" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Verificação pendente (tabela ainda sendo populada)" -ForegroundColor Yellow
    }
    
    Write-Host "`n⏭️  PRÓXIMOS PASSOS:" -ForegroundColor Cyan
    Write-Host "1. Criar índices" -ForegroundColor White
    Write-Host "2. Switch da API" -ForegroundColor White
    Write-Host "3. Testar performance`n" -ForegroundColor White
    
} catch {
    Write-Host "`n❌ ERRO: $_" -ForegroundColor Red
    Write-Host "Verifique restore_progress.log para detalhes" -ForegroundColor Yellow
}

Write-Host "`nPressione qualquer tecla para fechar..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')

