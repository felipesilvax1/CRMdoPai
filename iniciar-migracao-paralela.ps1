# ========================================
# MIGRACAO PARALELA - Plano C
# ========================================
# ETA: 2 min para iniciar, depois roda sozinho
# Voce pode continuar trabalhando normalmente!

param(
    [switch]$SkipDump,
    [switch]$SkipContainer
)

$ErrorActionPreference = "Continue"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "INICIANDO MIGRACAO PARALELA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# ========================================
# THREAD 1: Preparar Container (2 min)
# ========================================
if (-not $SkipContainer) {
    Write-Host "`n[Thread 1] Criando container PostgreSQL..." -ForegroundColor Yellow
    
    # Verificar se ja existe
    $existing = docker ps -a --filter "name=crm-postgres" --format "{{.Names}}"
    if ($existing -eq "crm-postgres") {
        Write-Host "  Aviso: Container ja existe. Removendo..." -ForegroundColor Yellow
        docker stop crm-postgres 2>$null
        docker rm crm-postgres 2>$null
    }
    
    # Criar novo container
    docker-compose -f docker-compose.postgres.yml up -d
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  OK: Container criado com sucesso!" -ForegroundColor Green
        
        # Aguardar inicializacao
        Write-Host "  Aguardando inicializacao..." -ForegroundColor Yellow
        Start-Sleep -Seconds 10
        
        # Verificar saude
        $health = docker inspect --format='{{.State.Health.Status}}' crm-postgres 2>$null
        if ($health -eq "healthy") {
            Write-Host "  OK: Container saudavel!" -ForegroundColor Green
        } else {
            Write-Host "  Aviso: Container iniciando... (pode demorar)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  ERRO: ao criar container!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "`n[Thread 1] SKIP: Container ja existe" -ForegroundColor Gray
}

# ========================================
# THREAD 2: Dump em Background (30 min)
# ========================================
if (-not $SkipDump) {
    Write-Host "`n[Thread 2] Iniciando dump do BD em background..." -ForegroundColor Yellow
    
    # Verificar se pg_dump existe
    $pgDump = Get-Command pg_dump -ErrorAction SilentlyContinue
    if (-not $pgDump) {
        Write-Host "  Aviso: pg_dump nao encontrado no PATH!" -ForegroundColor Red
        Write-Host "  Tentando usar Docker..." -ForegroundColor Yellow
        
        # Usar pg_dump do container
        $dumpCmd = "docker run --rm --network host -v ${PWD}:/backup postgres:17 pg_dump -h 192.168.15.22 -U postgres -Fc cnpj_processado -f /backup/cnpj_processado.dump"
    } else {
        $dumpCmd = "pg_dump -h 192.168.15.22 -U postgres -Fc cnpj_processado -f cnpj_processado.dump"
    }
    
    Write-Host "  Comando: $dumpCmd" -ForegroundColor Gray
    Write-Host "  Iniciando... (vai rodar em background)" -ForegroundColor Yellow
    Write-Host "  Voce pode continuar trabalhando normalmente!" -ForegroundColor Green
    
    # Criar script de dump
    $dumpScript = @'
$ErrorActionPreference = "Continue"
$startTime = Get-Date

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "DUMP EM BACKGROUND - INICIADO" -ForegroundColor Cyan
Write-Host "Hora: $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`nExecutando dump..." -ForegroundColor Yellow

# Definir senha PostgreSQL
$env:PGPASSWORD = "postgres"

# Executar dump
'@ + "`n" + $dumpCmd + @'

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
'@
    
    Set-Content -Path "dump-background.ps1" -Value $dumpScript
    
    # Iniciar em nova janela
    Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", "dump-background.ps1"
    
    Write-Host "  OK: Dump iniciado em nova janela!" -ForegroundColor Green
    Write-Host "  Progresso: Acompanhe na janela que abriu" -ForegroundColor Cyan
} else {
    Write-Host "`n[Thread 2] SKIP: Dump ja existe" -ForegroundColor Gray
}

# ========================================
# RESUMO
# ========================================
Write-Host "`n========================================" -ForegroundColor Green
Write-Host "INICIADO COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

Write-Host "`nSTATUS ATUAL:" -ForegroundColor Cyan
Write-Host "  OK: Container PostgreSQL: Rodando (porta 5433)" -ForegroundColor Green
Write-Host "  Processando: Dump do BD: Em background (30-60 min)" -ForegroundColor Yellow
Write-Host "  OK: Sistema Windows: Continua funcionando normal" -ForegroundColor Green

Write-Host "`nVOCE PODE AGORA:" -ForegroundColor Cyan
Write-Host "  - Continuar usando o sistema" -ForegroundColor White
Write-Host "  - Ir fazer outras coisas" -ForegroundColor White
Write-Host "  - Fechar este terminal" -ForegroundColor White
Write-Host "  - O dump roda sozinho!" -ForegroundColor White

Write-Host "`nVERIFICAR PROGRESSO:" -ForegroundColor Cyan
Write-Host "  # Ver tamanho do dump (vai crescendo)" -ForegroundColor Gray
Write-Host '  Get-Item cnpj_processado.dump | Select Name,Length' -ForegroundColor Yellow

Write-Host "`nPROXIMO PASSO:" -ForegroundColor Cyan
Write-Host "  Quando dump terminar (janela vai avisar):" -ForegroundColor White
Write-Host "  .\restore-paralelo.ps1" -ForegroundColor Yellow

Write-Host "`n========================================`n" -ForegroundColor Green
