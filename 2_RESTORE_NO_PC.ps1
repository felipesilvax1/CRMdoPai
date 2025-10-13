# ========================================================
# EXECUTAR ESTE SCRIPT NO PC PRINCIPAL
# ========================================================
# Tempo estimado: 30-40 minutos

$LOCAL_CONTAINER = "cnpj_postgres_final"
$DB = "cnpj_processed"
$SSD_PATH = "D:"  # AJUSTE para a letra do SSD!

Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "  RESTORE LOCAL NO PC - DO SSD" -ForegroundColor Cyan
Write-Host "  TEMPO: 30-40 MINUTOS" -ForegroundColor Cyan
Write-Host "================================================================`n" -ForegroundColor Cyan

# Verificar SSD
if (-not (Test-Path "${SSD_PATH}\dump_cnpj_processed")) {
    Write-Host "[ERRO] Dump nao encontrado em ${SSD_PATH}\dump_cnpj_processed!" -ForegroundColor Red
    Write-Host "Verifique se o SSD esta conectado e ajuste SSD_PATH`n" -ForegroundColor Yellow
    exit 1
}

$tamanhoGB = [math]::Round((Get-ChildItem "${SSD_PATH}\dump_cnpj_processed" -Recurse | Measure-Object -Property Length -Sum).Sum / 1GB, 2)
Write-Host "Dump encontrado: $tamanhoGB GB`n" -ForegroundColor Green

$inicio = Get-Date

# Preparar banco
Write-Host "[1/3] Preparando banco PostgreSQL..." -ForegroundColor Yellow
docker exec $LOCAL_CONTAINER psql -U postgres -c "DROP DATABASE IF EXISTS ${DB}_new;" 2>$null
docker exec $LOCAL_CONTAINER psql -U postgres -c "CREATE DATABASE ${DB}_new;" 2>$null
Write-Host "[OK] Banco criado`n" -ForegroundColor Green

# Copiar dump para container
Write-Host "[2/3] Copiando dump do SSD para container..." -ForegroundColor Yellow
docker cp "${SSD_PATH}\dump_cnpj_processed" ${LOCAL_CONTAINER}:/tmp/dump_cnpj
Write-Host "[OK] Dump copiado`n" -ForegroundColor Green

# Restore PARALELO com 8 threads
Write-Host "[3/3] Restore com 8 threads paralelos (30-40 min)..." -ForegroundColor Yellow
Write-Host "  Isso vai usar TODOS os cores do Xeon!`n" -ForegroundColor Gray

$contadorLinhas = 0
docker exec $LOCAL_CONTAINER `
  pg_restore -U postgres -d ${DB}_new `
  -j 8 -Fd /tmp/dump_cnpj `
  --no-owner --no-acl `
  --verbose 2>&1 | ForEach-Object {
    $contadorLinhas++
    if ($contadorLinhas % 100 -eq 0) {
        Write-Host "  Processadas $contadorLinhas operacoes..." -ForegroundColor Gray
    }
    if ($_ -match "restoring|creating.*TABLE|creating.*INDEX") {
        Write-Host "  $_" -ForegroundColor Cyan
    }
  }

$tempo = (Get-Date) - $inicio
Write-Host "`n[OK] Restore concluido em $([math]::Round($tempo.TotalMinutes, 1)) min!`n" -ForegroundColor Green

# VALIDACAO
Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "  VALIDACAO" -ForegroundColor Cyan
Write-Host "================================================================`n" -ForegroundColor Cyan

$tabelas = @('empresas', 'estabelecimentos', 'socios', 'cnaes')

Write-Host "Tabela               Registros       Status" -ForegroundColor White
Write-Host "------------------------------------------------" -ForegroundColor Gray

$totalRegistros = 0

foreach ($tabela in $tabelas) {
    $count = [long](docker exec $LOCAL_CONTAINER psql -U postgres -d ${DB}_new -t -c "SELECT COUNT(*) FROM $tabela;" 2>$null).Trim()
    $totalRegistros += $count
    
    $esperado = switch ($tabela) {
        "empresas" { 77041156 }
        "estabelecimentos" { 79225899 }
        "socios" { 26197302 }
        "cnaes" { 2718 }
    }
    
    $status = if ($count -eq $esperado) { "[OK]" } else { "($count de $esperado)" }
    $cor = if ($count -eq $esperado) { "Green" } else { "Yellow" }
    
    Write-Host "$($tabela.PadRight(20)) $($count.ToString('N0').PadLeft(15)) $status" -ForegroundColor $cor
}

Write-Host "------------------------------------------------" -ForegroundColor Gray
Write-Host "TOTAL: $($totalRegistros.ToString('N0')) registros`n" -ForegroundColor White

if ($totalRegistros -gt 180000000) {
    Write-Host "[SUCESSO] Ativando novo banco..." -ForegroundColor Green
    docker exec $LOCAL_CONTAINER psql -U postgres -c "DROP DATABASE IF EXISTS ${DB}_old;" 2>$null
    docker exec $LOCAL_CONTAINER psql -U postgres -c "ALTER DATABASE $DB RENAME TO ${DB}_old;" 2>$null
    docker exec $LOCAL_CONTAINER psql -U postgres -c "ALTER DATABASE ${DB}_new RENAME TO $DB;" 2>$null
    
    Write-Host "`n================================================================" -ForegroundColor Green
    Write-Host "  MIGRACAO 100% CONCLUIDA!" -ForegroundColor Green
    Write-Host "  Banco local pronto para uso!" -ForegroundColor Green
    Write-Host "================================================================`n" -ForegroundColor Green
    
    Write-Host "Proximos passos:" -ForegroundColor Cyan
    Write-Host "1. Atualizar docker-compose.yml (mudar IP para localhost)" -ForegroundColor White
    Write-Host "2. Reiniciar API: docker compose restart api" -ForegroundColor White
    Write-Host "3. Testar: http://localhost:3000`n" -ForegroundColor White
} else {
    Write-Host "[AVISO] Migracao incompleta. Faltam dados!`n" -ForegroundColor Yellow
}

# Limpar
Write-Host "[LIMPEZA] Removendo dump temporario do container..." -ForegroundColor Gray
docker exec $LOCAL_CONTAINER rm -rf /tmp/dump_cnpj 2>$null

Write-Host "`nTempo total: $([math]::Round($tempo.TotalMinutes, 1)) minutos`n" -ForegroundColor Cyan


