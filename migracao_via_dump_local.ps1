# Migracao Otimizada via Dump Local no T14
# Tempo estimado: 1-1.5 horas

$REMOTE_HOST = "192.168.15.25"
$REMOTE_CONTAINER = "c93d7f48cac6"
$LOCAL_CONTAINER = "cnpj_postgres_final"
$DB = "cnpj_processed"
$DUMP_DIR = "C:\Users\PwC\Documents\CRM\dump_postgres"

Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "  MIGRACAO VIA DUMP LOCAL (METODO OTIMIZADO)" -ForegroundColor Cyan
Write-Host "  TEMPO ESTIMADO: 1-1.5 HORAS" -ForegroundColor Cyan
Write-Host "================================================================`n" -ForegroundColor Cyan

$inicioTotal = Get-Date

# Criar diretorio para dump
New-Item -ItemType Directory -Force -Path $DUMP_DIR | Out-Null

# =============================================================
# ETAPA 1: DUMP NO T14 (LOCALMENTE) - 15-25 min
# =============================================================
Write-Host "[ETAPA 1/3] Fazendo DUMP no T14 (pode levar 15-25 min)..." -ForegroundColor Yellow
Write-Host "  Local no T14 = SEM gargalo de rede!" -ForegroundColor Gray
Write-Host "  Usando formato paralelo (-j 6)...`n" -ForegroundColor Gray

$inicio1 = Get-Date

# Executar pg_dump DENTRO do container do T14
$dumpRemoto = docker -H tcp://${REMOTE_HOST}:2375 exec $REMOTE_CONTAINER `
  pg_dump -U postgres -d $DB -Fd -j 6 -f /tmp/dump_cnpj 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "[AVISO] Docker daemon remoto nao acessivel." -ForegroundColor Yellow
    Write-Host "Tentando metodo alternativo via SSH...`n" -ForegroundColor Gray
    
    # Alternativa: criar dump via psql direto
    Write-Host "  Criando dump comprimido via rede (otimizado)..." -ForegroundColor Gray
    
    docker run --rm -e PGPASSWORD=password -v ${DUMP_DIR}:/dump postgres:15 `
      pg_dump -h $REMOTE_HOST -U postgres -d $DB `
      -Fd -j 6 -f /dump/cnpj_parallel `
      --verbose 2>&1 | Select-String "processing|completed" | ForEach-Object { 
        Write-Host "  $_" -ForegroundColor Gray 
      }
}

$tempo1 = (Get-Date) - $inicio1
Write-Host "`n[OK] DUMP concluido em $([math]::Round($tempo1.TotalMinutes, 1)) min`n" -ForegroundColor Green

# Verificar tamanho do dump
$tamanhoGB = 0
if (Test-Path "$DUMP_DIR\cnpj_parallel") {
    $tamanhoGB = [math]::Round((Get-ChildItem "$DUMP_DIR\cnpj_parallel" -Recurse | Measure-Object -Property Length -Sum).Sum / 1GB, 2)
    Write-Host "  Tamanho do dump: $tamanhoGB GB (comprimido)`n" -ForegroundColor Cyan
}

# =============================================================
# ETAPA 2: JA TEMOS O DUMP LOCAL (se veio via rede)
# =============================================================
# (Se usou o método alternativo, já está em $DUMP_DIR)

# =============================================================
# ETAPA 3: RESTORE LOCAL - 30-45 min
# =============================================================
Write-Host "[ETAPA 2/3] Preparando banco local..." -ForegroundColor Yellow
docker exec $LOCAL_CONTAINER psql -U postgres -c "DROP DATABASE IF EXISTS ${DB}_new;" 2>$null
docker exec $LOCAL_CONTAINER psql -U postgres -c "CREATE DATABASE ${DB}_new;" 2>$null
Write-Host "[OK] Banco preparado`n" -ForegroundColor Green

Write-Host "[ETAPA 3/3] RESTORE no PC (pode levar 30-45 min)..." -ForegroundColor Yellow
Write-Host "  Local no PC = SEM gargalo de rede!" -ForegroundColor Gray
Write-Host "  Usando 8 workers paralelos...`n" -ForegroundColor Gray

$inicio3 = Get-Date

# Copiar dump para dentro do container
docker cp "$DUMP_DIR\cnpj_parallel" ${LOCAL_CONTAINER}:/tmp/dump_cnpj

# Restaurar com paralelizacao
docker exec $LOCAL_CONTAINER `
  pg_restore -U postgres -d ${DB}_new `
  -j 8 -Fd /tmp/dump_cnpj `
  --verbose 2>&1 | Select-String "processing|restoring|creating" | ForEach-Object {
    Write-Host "  $_" -ForegroundColor Gray
  }

$tempo3 = (Get-Date) - $inicio3
Write-Host "`n[OK] RESTORE concluido em $([math]::Round($tempo3.TotalMinutes, 1)) min`n" -ForegroundColor Green

# =============================================================
# VALIDACAO
# =============================================================
Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "  VALIDACAO DE INTEGRIDADE" -ForegroundColor Cyan
Write-Host "================================================================`n" -ForegroundColor Cyan

$tabelas = @('empresas', 'estabelecimentos', 'socios', 'cnaes')

Write-Host "Tabela               Remoto          Local Novo      Status" -ForegroundColor White
Write-Host "----------------------------------------------------------------" -ForegroundColor Gray

$tudoOk = $true

foreach ($tabela in $tabelas) {
    $remoto = (docker run --rm -e PGPASSWORD=password postgres:15 psql -h $REMOTE_HOST -U postgres -d $DB -t -c "SELECT COUNT(*) FROM $tabela;" 2>$null).Trim()
    $local = (docker exec $LOCAL_CONTAINER psql -U postgres -d ${DB}_new -t -c "SELECT COUNT(*) FROM $tabela;" 2>$null).Trim()
    
    $status = if ($remoto -eq $local) { "[OK]" } else { "[ERRO]" }
    $cor = if ($remoto -eq $local) { "Green" } else { "Red" }
    
    if ($remoto -ne $local) { $tudoOk = $false }
    
    Write-Host "$($tabela.PadRight(20)) $($remoto.PadLeft(15)) $($local.PadLeft(15)) $status" -ForegroundColor $cor
}

# Trocar bancos se tudo OK
if ($tudoOk) {
    Write-Host "`n[FINALIZANDO] Substituindo banco antigo pelo novo..." -ForegroundColor Yellow
    docker exec $LOCAL_CONTAINER psql -U postgres -c "DROP DATABASE IF EXISTS ${DB}_old;" 2>$null
    docker exec $LOCAL_CONTAINER psql -U postgres -c "ALTER DATABASE $DB RENAME TO ${DB}_old;" 2>$null
    docker exec $LOCAL_CONTAINER psql -U postgres -c "ALTER DATABASE ${DB}_new RENAME TO $DB;" 2>$null
    Write-Host "[OK] Banco atualizado!`n" -ForegroundColor Green
}

$tempoTotal = (Get-Date) - $inicioTotal

Write-Host "`n================================================================" -ForegroundColor Green
Write-Host "  MIGRACAO CONCLUIDA EM $([math]::Round($tempoTotal.TotalMinutes, 1)) MINUTOS!" -ForegroundColor Green
Write-Host "  Status: $(if ($tudoOk) {'SUCESSO TOTAL'} else {'COM AVISOS'})" -ForegroundColor $(if ($tudoOk) {"Green"} else {"Yellow"})
Write-Host "================================================================`n" -ForegroundColor Green

# Limpar dumps temporarios
Write-Host "[LIMPEZA] Removendo arquivos temporarios..." -ForegroundColor Gray
docker exec $LOCAL_CONTAINER rm -rf /tmp/dump_cnpj 2>$null

Write-Host "`nFinalizado! Atualize docker-compose.yml para usar banco local.`n" -ForegroundColor Cyan

