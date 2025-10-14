# ========================================
# MONITORAMENTO DO RESTORE EM TEMPO REAL
# ========================================

$ErrorActionPreference = "Continue"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "MONITORAMENTO DO RESTORE" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Pressione Ctrl+C para sair`n" -ForegroundColor Gray

$startTime = Get-Date "2025-10-14 15:14:00"  # Hora que o restore iniciou
$iteration = 0

while ($true) {
    $iteration++
    $now = Get-Date
    $elapsed = ($now - $startTime).TotalMinutes
    
    Clear-Host
    
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "RESTORE - PROGRESSO EM TEMPO REAL" -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
    
    Write-Host "Tempo decorrido: $([math]::Round($elapsed, 1)) minutos" -ForegroundColor Yellow
    Write-Host "Hora atual: $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Gray
    Write-Host "ETA conclusao: 16:00-16:15 (40-60 min total)`n" -ForegroundColor Cyan
    
    # Verificar processos
    Write-Host "----------------------------------------" -ForegroundColor Gray
    Write-Host "PROCESSOS PG_RESTORE:" -ForegroundColor White
    $processes = docker exec crm-postgres sh -c "ps aux | grep 'pg_restore' | grep -v grep | wc -l" 2>&1
    if ($processes -match '\d+' -and [int]$processes -gt 0) {
        Write-Host "  OK $processes processos rodando (1 principal + 4 workers)" -ForegroundColor Green
    } else {
        Write-Host "  CONCLUIDO ou PARADO" -ForegroundColor Yellow
    }
    
    # Verificar tabelas criadas
    Write-Host "`nTABELAS CRIADAS:" -ForegroundColor White
    $tables = docker exec crm-postgres psql -U postgres -d cnpj_processado -t -c "SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public'" 2>&1
    if ($tables -match '\d+') {
        Write-Host "  $($tables.Trim()) tabelas" -ForegroundColor Green
    }
    
    # Verificar registros em estabelecimentos (tabela principal)
    Write-Host "`nREGISTROS EM ESTABELECIMENTOS:" -ForegroundColor White
    $count = docker exec crm-postgres psql -U postgres -d cnpj_processado -t -c "SELECT COUNT(*) FROM estabelecimentos" 2>&1
    
    if ($count -match '\d+') {
        $countNum = [long]$count.Trim().Replace(",", "")
        $progress = ($countNum / 77000000.0) * 100
        Write-Host "  $($count.Trim()) de ~77,000,000" -ForegroundColor Green
        Write-Host "  Progresso: $([math]::Round($progress, 1))%" -ForegroundColor Cyan
        
        # Barra de progresso visual
        $barLength = 40
        $filled = [math]::Floor($progress / 100 * $barLength)
        $empty = $barLength - $filled
        $bar = "[" + ("=" * $filled) + ("." * $empty) + "]"
        Write-Host "  $bar $([math]::Round($progress, 1))%" -ForegroundColor Yellow
    } else {
        Write-Host "  Aguardando estrutura..." -ForegroundColor Yellow
    }
    
    # Log (ultimas linhas)
    Write-Host "`n----------------------------------------" -ForegroundColor Gray
    Write-Host "ULTIMAS ATIVIDADES (log):" -ForegroundColor White
    if (Test-Path "restore_output.log") {
        $lastLines = Get-Content "restore_output.log" -Tail 5 -ErrorAction SilentlyContinue
        if ($lastLines) {
            foreach ($line in $lastLines) {
                if ($line -match "finished") {
                    Write-Host "  $line" -ForegroundColor Green
                } elseif ($line -match "creating") {
                    Write-Host "  $line" -ForegroundColor Cyan
                } else {
                    Write-Host "  $line" -ForegroundColor Gray
                }
            }
        }
    }
    
    Write-Host "`n----------------------------------------" -ForegroundColor Gray
    Write-Host "Atualizando em 30 segundos..." -ForegroundColor Gray
    Write-Host "Iteracao: $iteration | Proxima atualizacao: $(Get-Date -Date ($now.AddSeconds(30)) -Format 'HH:mm:ss')" -ForegroundColor DarkGray
    
    Start-Sleep -Seconds 30
}

