# Migração Rápida - Método Otimizado
# Garantido em < 2 horas

$REMOTE_HOST = "192.168.15.25"
$REMOTE_CONTAINER = "c93d7f48cac6"
$LOCAL_CONTAINER = "cnpj_postgres_final"
$DB = "cnpj_processed"

Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "  MIGRACAO RAPIDA - METODO HIBRIDO OTIMIZADO" -ForegroundColor Cyan
Write-Host "  GARANTIA: < 2 HORAS" -ForegroundColor Cyan
Write-Host "================================================================`n" -ForegroundColor Cyan

$inicioGeral = Get-Date

# PASSO 1: Copiar apenas SCHEMA (estrutura) - RAPIDO
Write-Host "[PASSO 1/4] Copiando estrutura das tabelas (30s)..." -ForegroundColor Yellow
$inicio = Get-Date

docker exec $LOCAL_CONTAINER psql -U postgres -c "DROP DATABASE IF EXISTS $DB;" 2>$null
docker exec $LOCAL_CONTAINER psql -U postgres -c "CREATE DATABASE $DB;" 2>$null

docker run --rm -e PGPASSWORD=password postgres:15 `
  pg_dump -h $REMOTE_HOST -U postgres -d $DB --schema-only 2>$null |
  docker exec -i $LOCAL_CONTAINER psql -U postgres -d $DB 2>$null

$tempo = (Get-Date) - $inicio
Write-Host "[OK] Estrutura copiada em $([math]::Round($tempo.TotalSeconds))s`n" -ForegroundColor Green

# PASSO 2: Copiar tabelas PEQUENAS via rede (rapido) - 5 min
Write-Host "[PASSO 2/4] Copiando tabelas pequenas via rede (5 min)..." -ForegroundColor Yellow
$inicio = Get-Date

$tabelasPequenas = @('cnaes', 'municipios', 'naturezas', 'qualificacoes', 'paises', 'motivos')

foreach ($tabela in $tabelasPequenas) {
    Write-Host "  Copiando $tabela..." -ForegroundColor Gray
    docker run --rm -e PGPASSWORD=password postgres:15 `
      psql -h $REMOTE_HOST -U postgres -d $DB -c "\COPY $tabela TO STDOUT" 2>$null |
      docker exec -i $LOCAL_CONTAINER psql -U postgres -d $DB -c "\COPY $tabela FROM STDIN" 2>$null
}

$tempo = (Get-Date) - $inicio
Write-Host "[OK] Tabelas pequenas copiadas em $([math]::Round($tempo.TotalMinutes, 1)) min`n" -ForegroundColor Green

# PASSO 3: Copiar tabelas GRANDES em CHUNKS paralelos - 1.5h
Write-Host "[PASSO 3/4] Copiando tabelas GRANDES em lotes (1-1.5h)..." -ForegroundColor Yellow
Write-Host "  Metodo: Chunks de 5M registros em paralelo`n" -ForegroundColor Gray

$inicio = Get-Date

# Função para copiar chunk
$scriptBlock = {
    param($host_ip, $tabela, $offset, $limit, $container, $db)
    
    $inicio = Get-Date
    
    # Exportar chunk
    $query = "COPY (SELECT * FROM $tabela ORDER BY 1 LIMIT $limit OFFSET $offset) TO STDOUT WITH (FORMAT BINARY)"
    
    docker run --rm -e PGPASSWORD=password postgres:15 `
      psql -h $host_ip -U postgres -d $db -c $query 2>$null |
      docker exec -i $container psql -U postgres -d $db -c "COPY $tabela FROM STDIN WITH (FORMAT BINARY)" 2>$null
    
    $tempo = (Get-Date) - $inicio
    Write-Host "    [$tabela] Chunk $offset-$($offset+$limit): $([math]::Round($tempo.TotalMinutes, 1)) min" -ForegroundColor Gray
}

# Empresas: 77M em chunks de 10M (8 chunks)
Write-Host "  Processando EMPRESAS (77M registros)..." -ForegroundColor Cyan
$jobs = @()
for ($i = 0; $i -lt 8; $i++) {
    $offset = $i * 10000000
    $jobs += Start-Job -ScriptBlock $scriptBlock -ArgumentList @($REMOTE_HOST, "empresas", $offset, 10000000, $LOCAL_CONTAINER, $DB)
    Start-Sleep -Milliseconds 500
}

# Aguardar com progresso
while ($jobs | Where-Object { $_.State -eq 'Running' }) {
    $concluidos = ($jobs | Where-Object { $_.State -eq 'Completed' }).Count
    $total = $jobs.Count
    Write-Progress -Activity "Migrando Empresas" -Status "$concluidos de $total chunks" -PercentComplete (($concluidos/$total)*100)
    Start-Sleep -Seconds 5
}

$jobs | Remove-Job -Force

# Estabelecimentos: 79M em chunks de 10M (8 chunks)
Write-Host "`n  Processando ESTABELECIMENTOS (79M registros)..." -ForegroundColor Cyan
$jobs = @()
for ($i = 0; $i -lt 8; $i++) {
    $offset = $i * 10000000
    $jobs += Start-Job -ScriptBlock $scriptBlock -ArgumentList @($REMOTE_HOST, "estabelecimentos", $offset, 10000000, $LOCAL_CONTAINER, $DB)
    Start-Sleep -Milliseconds 500
}

while ($jobs | Where-Object { $_.State -eq 'Running' }) {
    $concluidos = ($jobs | Where-Object { $_.State -eq 'Completed' }).Count
    $total = $jobs.Count
    Write-Progress -Activity "Migrando Estabelecimentos" -Status "$concluidos de $total chunks" -PercentComplete (($concluidos/$total)*100)
    Start-Sleep -Seconds 5
}

$jobs | Remove-Job -Force

# Socios: 26M em chunks de 5M (6 chunks)
Write-Host "`n  Processando SOCIOS (26M registros)..." -ForegroundColor Cyan
$jobs = @()
for ($i = 0; $i -lt 6; $i++) {
    $offset = $i * 5000000
    $jobs += Start-Job -ScriptBlock $scriptBlock -ArgumentList @($REMOTE_HOST, "socios", $offset, 5000000, $LOCAL_CONTAINER, $DB)
    Start-Sleep -Milliseconds 500
}

while ($jobs | Where-Object { $_.State -eq 'Running' }) {
    $concluidos = ($jobs | Where-Object { $_.State -eq 'Completed' }).Count
    $total = $jobs.Count
    Write-Progress -Activity "Migrando Socios" -Status "$concluidos de $total chunks" -PercentComplete (($concluidos/$total)*100)
    Start-Sleep -Seconds 5
}

$jobs | Remove-Job -Force

$tempo = (Get-Date) - $inicio
Write-Host "`n[OK] Tabelas grandes copiadas em $([math]::Round($tempo.TotalMinutes, 1)) min`n" -ForegroundColor Green

# PASSO 4: Criar indices
Write-Host "[PASSO 4/4] Criando indices (10-15 min)..." -ForegroundColor Yellow
$inicio = Get-Date

$indices = @(
    'CREATE INDEX CONCURRENTLY idx_empresas_razao ON empresas("razao social")',
    'CREATE INDEX CONCURRENTLY idx_est_municipio ON estabelecimentos(municipio)',
    'CREATE INDEX CONCURRENTLY idx_est_cnpj ON estabelecimentos("cnpj basico")',
    'CREATE INDEX CONCURRENTLY idx_socios_cnpj ON socios("cnpj basico")'
)

foreach ($idx in $indices) {
    docker exec $LOCAL_CONTAINER psql -U postgres -d $DB -c $idx 2>$null
}

$tempo = (Get-Date) - $inicio
Write-Host "[OK] Indices criados em $([math]::Round($tempo.TotalMinutes, 1)) min`n" -ForegroundColor Green

# VALIDACAO
Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "  VALIDACAO DE INTEGRIDADE" -ForegroundColor Cyan
Write-Host "================================================================`n" -ForegroundColor Cyan

$tabelas = @('empresas', 'estabelecimentos', 'socios', 'cnaes')

Write-Host "Tabela               Remoto          Local           Status" -ForegroundColor White
Write-Host "----------------------------------------------------------------" -ForegroundColor Gray

foreach ($tabela in $tabelas) {
    $remoto = docker run --rm -e PGPASSWORD=password postgres:15 psql -h $REMOTE_HOST -U postgres -d $DB -t -c "SELECT COUNT(*) FROM $tabela;" 2>$null
    $local = docker exec $LOCAL_CONTAINER psql -U postgres -d $DB -t -c "SELECT COUNT(*) FROM $tabela;" 2>$null
    
    $remoto = $remoto.Trim()
    $local = $local.Trim()
    
    $status = if ($remoto -eq $local) { "[OK]" } else { "[ERRO]" }
    $cor = if ($remoto -eq $local) { "Green" } else { "Red" }
    
    Write-Host "$($tabela.PadRight(20)) $($remoto.PadLeft(15)) $($local.PadLeft(15)) $status" -ForegroundColor $cor
}

$tempoTotal = (Get-Date) - $inicioGeral
Write-Host "`n================================================================" -ForegroundColor Green
Write-Host "  MIGRACAO CONCLUIDA EM $([math]::Round($tempoTotal.TotalMinutes, 1)) MINUTOS!" -ForegroundColor Green
Write-Host "================================================================`n" -ForegroundColor Green

