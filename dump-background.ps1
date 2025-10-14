$ErrorActionPreference = "Continue"
$startTime = Get-Date

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "DUMP EM BACKGROUND - INICIADO" -ForegroundColor Cyan
Write-Host "Hora: $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`nExecutando dump..." -ForegroundColor Yellow

# Executar dump
docker run --rm --network host -v C:\Users\PwC\Documents\CRM:/backup postgres:17 pg_dump -h 192.168.15.22 -U postgres -Fc cnpj_processado -f /backup/cnpj_processado.dump
if ($LASTEXITCODE -eq 0) {
    $endTime = Get-Date
    $duration = $endTime - $startTime
    $fileSize = (Get-Item cnpj_processado.dump).Length / 1GB
    
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "OK: DUMP CONCLUIDO COM SUCESSO!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Tempo: $([math]::Round($duration.TotalMinutes, 2)) minutos" -ForegroundColor White
    Write-Host "Tamanho: $([math]::Round($fileSize, 2)) GB" -ForegroundColor White
    Write-Host "`nProximo passo: Execute restore-paralelo.ps1" -ForegroundColor Yellow
} else {
    Write-Host "`nERRO NO DUMP!" -ForegroundColor Red
    Write-Host "Verifique os logs acima" -ForegroundColor Yellow
}

Write-Host "`nPressione qualquer tecla para fechar..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
