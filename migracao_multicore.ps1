# MIGRACAO OTIMIZADA - USA TODOS OS CORES DO XEON
# Compressao paralela com 7-Zip (muito mais rapido que tar/gzip)

$REMOTE_HOST = "192.168.15.25"
$LOCAL_CONTAINER = "cnpj_postgres_final"
$DB = "cnpj_processed"
$DUMP_DIR = "dump_postgres_paralelo"
$CORES = 12  # Xeon cores

Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "  MIGRACAO MULTICORE - APROVEITANDO XEON" -ForegroundColor Cyan
Write-Host "  $CORES CORES EM PARALELO" -ForegroundColor Cyan
Write-Host "================================================================`n" -ForegroundColor Cyan

$inicioTotal = Get-Date

# ========================================================
# ETAPA 1: DUMP PARALELO NO T14 via rede (20-30 min)
# ========================================================
Write-Host "[1/4] Dump paralelo do T14 (formato directory)..." -ForegroundColor Yellow
Write-Host "  pg_dump com -j 6 (6 threads em paralelo)" -ForegroundColor Gray
Write-Host "  Formato: directory (permite paralelizacao)`n" -ForegroundColor Gray

$inicio = Get-Date

# Criar pasta para dump
New-Item -ItemType Directory -Force -Path $DUMP_DIR | Out-Null

# pg_dump PARALELO (-Fd = directory format, -j = jobs)
docker run --rm `
  -e PGPASSWORD=password `
  -v ${PWD}/${DUMP_DIR}:/dump `
  postgres:15 `
  pg_dump -h $REMOTE_HOST -U postgres -d $DB `
  -Fd -j 6 `
  -f /dump/db_dump `
  --verbose 2>&1 | ForEach-Object {
    if ($_ -match "processing|dumping|completed") {
        Write-Host "  $_" -ForegroundColor Gray
    }
  }

$tempo1 = (Get-Date) - $inicio
Write-Host "`n[OK] Dump concluido em $([math]::Round($tempo1.TotalMinutes, 1)) min" -ForegroundColor Green

# Verificar tamanho
$tamanhoMB = [math]::Round((Get-ChildItem "$DUMP_DIR\db_dump" -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB, 0)
Write-Host "  Tamanho: $tamanhoMB MB`n" -ForegroundColor Cyan

# ========================================================
# ETAPA 2: COMPRESSAO PARALELA com 7-Zip (5-10 min)
# ========================================================
Write-Host "[2/4] Comprimindo com 7-Zip (MULTICORE)..." -ForegroundColor Yellow
Write-Host "  Usando $CORES threads em paralelo" -ForegroundColor Gray
Write-Host "  Algoritmo: ZSTD (ultra rapido)`n" -ForegroundColor Gray

$inicio = Get-Date

# Verificar se 7-Zip esta instalado
$7zipPath = "C:\Program Files\7-Zip\7z.exe"
if (-not (Test-Path $7zipPath)) {
    Write-Host "  Instalando 7-Zip..." -ForegroundColor Yellow
    winget install --id 7zip.7zip -e --accept-source-agreements --accept-package-agreements --silent
    Start-Sleep -Seconds 5
}

# Comprimir com TODAS as threads
& $7zipPath a -t7z -m0=zstd -mmt=$CORES -mx5 `
  "$DUMP_DIR\db_dump.7z" `
  "$DUMP_DIR\db_dump\*" | Out-Null

$tempo2 = (Get-Date) - $inicio
$tamanhoComprimidoMB = [math]::Round((Get-Item "$DUMP_DIR\db_dump.7z").Length / 1MB, 0)
$razaoCompressao = [math]::Round($tamanhoMB / $tamanhoComprimidoMB, 1)

Write-Host "[OK] Comprimido em $([math]::Round($tempo2.TotalMinutes, 1)) min" -ForegroundColor Green
Write-Host "  Tamanho final: $tamanhoComprimidoMB MB (ratio ${razaoCompressao}:1)`n" -ForegroundColor Cyan

# ========================================================
# ETAPA 3: DESCOMPRESSAO PARALELA (3-5 min)
# ========================================================
Write-Host "[3/4] Descomprimindo com $CORES cores..." -ForegroundColor Yellow

$inicio = Get-Date

# Descomprimir usando todos os cores
Remove-Item -Path "$DUMP_DIR\db_dump" -Recurse -Force -ErrorAction SilentlyContinue
& $7zipPath x "$DUMP_DIR\db_dump.7z" -o"$DUMP_DIR" -mmt=$CORES -y | Out-Null

$tempo = (Get-Date) - $inicio
Write-Host "[OK] Descomprimido em $([math]::Round($tempo.TotalMinutes, 1)) min`n" -ForegroundColor Green

# ========================================================
# ETAPA 4: RESTORE PARALELO (30-40 min)
# ========================================================
Write-Host "[4/4] Restore paralelo no PostgreSQL local..." -ForegroundColor Yellow
Write-Host "  pg_restore com -j 8 (8 threads em paralelo)`n" -ForegroundColor Gray

$inicio = Get-Date

# Copiar dump para container
docker cp "$DUMP_DIR\db_dump" ${LOCAL_CONTAINER}:/tmp/

# Restore PARALELO
docker exec $LOCAL_CONTAINER `
  pg_restore -U postgres -d ${DB}_new `
  -j 8 -Fd /tmp/db_dump `
  --no-owner --no-acl `
  --verbose 2>&1 | Select-String "processing|restoring|creating|index" | ForEach-Object {
    if ($_ -notmatch "ERROR") {
        Write-Host "  $_" -ForegroundColor Gray
    }
  }

$tempo4 = (Get-Date) - $inicio
Write-Host "`n[OK] Restore concluido em $([math]::Round($tempo4.TotalMinutes, 1)) min`n" -ForegroundColor Green

# ========================================================
# VALIDACAO FINAL
# ========================================================
Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "  VALIDACAO COMPLETA" -ForegroundColor Cyan
Write-Host "================================================================`n" -ForegroundColor Cyan

Write-Host "Tabela               Remoto (T14)    Local (PC)      Diferenca" -ForegroundColor White
Write-Host "----------------------------------------------------------------" -ForegroundColor Gray

$tudoOk = $true

foreach ($tabela in @('empresas', 'estabelecimentos', 'socios', 'cnaes')) {
    $remoto = [long](docker run --rm -e PGPASSWORD=password postgres:15 psql -h $REMOTE_HOST -U postgres -d $DB -t -c "SELECT COUNT(*) FROM $tabela;" 2>$null).Trim()
    $local = [long](docker exec $LOCAL_CONTAINER psql -U postgres -d ${DB}_new -t -c "SELECT COUNT(*) FROM $tabela;" 2>$null).Trim()
    
    $diff = $remoto - $local
    $status = if ($diff -eq 0) { "[OK]" } else { "DIFF: $diff" }
    $cor = if ($diff -eq 0) { "Green" } else { "Red" }
    
    if ($diff -ne 0) { $tudoOk = $false }
    
    Write-Host "$($tabela.PadRight(20)) $($remoto.ToString('N0').PadLeft(15)) $($local.ToString('N0').PadLeft(15)) $status" -ForegroundColor $cor
}

if ($tudoOk) {
    Write-Host "`n[SUCESSO] Ativando novo banco..." -ForegroundColor Green
    docker exec $LOCAL_CONTAINER psql -U postgres -c "DROP DATABASE IF EXISTS ${DB}_old;" 2>$null
    docker exec $LOCAL_CONTAINER psql -U postgres -c "ALTER DATABASE $DB RENAME TO ${DB}_old;" 2>$null  
    docker exec $LOCAL_CONTAINER psql -U postgres -c "ALTER DATABASE ${DB}_new RENAME TO $DB;" 2>$null
}

$tempoTotal = (Get-Date) - $inicioTotal

Write-Host "`n================================================================" -ForegroundColor Green
Write-Host "  TEMPO TOTAL: $([math]::Round($tempoTotal.TotalHours, 2)) HORAS" -ForegroundColor Green
Write-Host "================================================================`n" -ForegroundColor Green

Write-Host "Breakdown:" -ForegroundColor Cyan
Write-Host "  Dump:         $([math]::Round($tempo1.TotalMinutes, 1)) min" -ForegroundColor White
Write-Host "  Compressao:   $([math]::Round($tempo2.TotalMinutes, 1)) min" -ForegroundColor White
Write-Host "  Restore:      $([math]::Round($tempo4.TotalMinutes, 1)) min" -ForegroundColor White
Write-Host "`n================================================================`n" -ForegroundColor Cyan

