# ========================================
# DUMP MANUAL COM SENHA CUSTOMIZADA
# ========================================
# Execute: .\dump-manual.ps1 -Senha "SUA_SENHA_AQUI"

param(
    [Parameter(Mandatory=$true)]
    [string]$Senha
)

$ErrorActionPreference = "Continue"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "DUMP COM SENHA CUSTOMIZADA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$startTime = Get-Date

# Definir senha
$env:PGPASSWORD = $Senha

Write-Host "`nIniciando dump..." -ForegroundColor Yellow
Write-Host "Host: 192.168.15.22" -ForegroundColor Gray
Write-Host "Database: cnpj_processado" -ForegroundColor Gray
Write-Host "Usuario: postgres" -ForegroundColor Gray

# Tentar pg_dump local primeiro
$pgDump = Get-Command pg_dump -ErrorAction SilentlyContinue
if ($pgDump) {
    Write-Host "`nUsando pg_dump local: $($pgDump.Source)" -ForegroundColor Green
    
    pg_dump -h 192.168.15.22 -U postgres -Fc cnpj_processado -f cnpj_processado.dump
    
} else {
    Write-Host "`nUsando pg_dump via Docker..." -ForegroundColor Yellow
    
    docker run --rm --network host -e PGPASSWORD=$Senha -v ${PWD}:/backup postgres:17 pg_dump -h 192.168.15.22 -U postgres -Fc cnpj_processado -f /backup/cnpj_processado.dump
}

if ($LASTEXITCODE -eq 0) {
    $endTime = Get-Date
    $duration = $endTime - $startTime
    $fileSize = (Get-Item cnpj_processado.dump).Length / 1GB
    
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "DUMP CONCLUIDO COM SUCESSO!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Tempo: $([math]::Round($duration.TotalMinutes, 2)) minutos" -ForegroundColor White
    Write-Host "Tamanho: $([math]::Round($fileSize, 2)) GB" -ForegroundColor White
    Write-Host "`nProximo passo: .\restore-paralelo.ps1" -ForegroundColor Yellow
} else {
    Write-Host "`n========================================" -ForegroundColor Red
    Write-Host "ERRO NO DUMP!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "`nVerifique:" -ForegroundColor Yellow
    Write-Host "  1. Senha esta correta?" -ForegroundColor White
    Write-Host "  2. PostgreSQL esta rodando em 192.168.15.22:5432?" -ForegroundColor White
    Write-Host "  3. Usuario 'postgres' tem permissao?" -ForegroundColor White
}

Write-Host "`n"

