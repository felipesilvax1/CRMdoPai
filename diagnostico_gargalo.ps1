# Script de diagnóstico de gargalos para migração PostgreSQL

Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "  DIAGNÓSTICO DE GARGALOS - MIGRAÇÃO POSTGRESQL" -ForegroundColor Cyan
Write-Host "================================================================`n" -ForegroundColor Cyan

$REMOTE_HOST = "192.168.15.24"

# ===================================================================
# TESTE 1: REDE (Throughput)
# ===================================================================
Write-Host "`n[1/5] TESTANDO VELOCIDADE DE REDE..." -ForegroundColor Yellow

$inicioRede = Get-Date

# Transferir 100MB de dados dummy via PostgreSQL
Write-Host "  Transferindo 100MB de teste..."
$query = "SELECT repeat('x', 1024*1024)::text as data FROM generate_series(1, 100)"
$tempo = Measure-Command {
    docker run --rm -e PGPASSWORD=password postgres:15 `
      psql -h $REMOTE_HOST -U postgres -d cnpj_processed `
      -c $query -o nul 2>$null
}

$velocidadeMBps = 100 / $tempo.TotalSeconds
Write-Host "  Velocidade: $([math]::Round($velocidadeMBps, 2)) MB/s" -ForegroundColor Cyan
Write-Host "  Latência: $([math]::Round($tempo.TotalMilliseconds / 100, 2)) ms por MB" -ForegroundColor Gray

if ($velocidadeMBps -lt 10) {
    Write-Host "  [!] GARGALO IDENTIFICADO: REDE LENTA!" -ForegroundColor Red
    $gargaloRede = $true
} else {
    Write-Host "  [OK] Rede está boa!" -ForegroundColor Green
    $gargaloRede = $false
}

# ===================================================================
# TESTE 2: DISCO (I/O de Escrita)
# ===================================================================
Write-Host "`n[2/5] TESTANDO VELOCIDADE DE DISCO..." -ForegroundColor Yellow

$arquivoTeste = "teste_disco_1gb.bin"
Write-Host "  Escrevendo 1GB de teste..."

$tempoDisco = Measure-Command {
    # Criar arquivo de 1GB
    $bytes = New-Object byte[] (1024*1024*100) # 100MB por vez
    $stream = [System.IO.File]::OpenWrite($arquivoTeste)
    for ($i = 0; $i -lt 10; $i++) {
        $stream.Write($bytes, 0, $bytes.Length)
    }
    $stream.Close()
}

$velocidadeDiscoMBps = 1024 / $tempoDisco.TotalSeconds
Write-Host "  Velocidade escrita: $([math]::Round($velocidadeDiscoMBps, 2)) MB/s" -ForegroundColor Cyan

Remove-Item $arquivoTeste -Force

if ($velocidadeDiscoMBps -lt 50) {
    Write-Host "  [!] GARGALO IDENTIFICADO: DISCO LENTO (HDD?)!" -ForegroundColor Red
    $gargaloDisco = $true
} elseif ($velocidadeDiscoMBps -lt 200) {
    Write-Host "  [~] Disco OK, mas não é SSD NVMe" -ForegroundColor Yellow
    $gargaloDisco = $false
} else {
    Write-Host "  [OK] Disco rápido (SSD)!" -ForegroundColor Green
    $gargaloDisco = $false
}

# ===================================================================
# TESTE 3: RAM (Disponível)
# ===================================================================
Write-Host "`n[3/5] TESTANDO MEMÓRIA RAM..." -ForegroundColor Yellow

$os = Get-CimInstance Win32_OperatingSystem
$ramTotalGB = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
$ramLivreGB = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
$ramUsoPercent = [math]::Round((($ramTotalGB - $ramLivreGB) / $ramTotalGB) * 100, 1)

Write-Host "  RAM Total: $ramTotalGB GB" -ForegroundColor Cyan
Write-Host "  RAM Livre: $ramLivreGB GB" -ForegroundColor Cyan
Write-Host "  Uso atual: $ramUsoPercent%" -ForegroundColor Cyan

if ($ramLivreGB -lt 8) {
    Write-Host "  [!] GARGALO IDENTIFICADO: RAM INSUFICIENTE!" -ForegroundColor Red
    Write-Host "     Feche aplicações para liberar memória" -ForegroundColor Yellow
    $gargaloRAM = $true
} else {
    Write-Host "  [OK] RAM suficiente para migração!" -ForegroundColor Green
    $gargaloRAM = $false
}

# ===================================================================
# TESTE 4: CPU (Processamento PostgreSQL)
# ===================================================================
Write-Host "`n[4/5] TESTANDO CAPACIDADE DE PROCESSAMENTO..." -ForegroundColor Yellow

Write-Host "  Testando query pesada no PostgreSQL remoto..."
$queryPesada = "SELECT COUNT(*) FROM estabelecimentos WHERE municipio LIKE '%SAO%'"

$tempoCPU = Measure-Command {
    docker run --rm -e PGPASSWORD=password postgres:15 `
      psql -h $REMOTE_HOST -U postgres -d cnpj_processed `
      -c $queryPesada -t 2>$null
}

Write-Host "  Tempo de query em 79M registros: $([math]::Round($tempoCPU.TotalSeconds, 2))s" -ForegroundColor Cyan

if ($tempoCPU.TotalSeconds -gt 30) {
    Write-Host "  [!] PostgreSQL remoto está lento!" -ForegroundColor Red
    $gargaloCPU = $true
} else {
    Write-Host "  [OK] PostgreSQL respondendo bem!" -ForegroundColor Green
    $gargaloCPU = $false
}

# ===================================================================
# TESTE 5: TAXA REAL DE TRANSFERÊNCIA (Teste Prático)
# ===================================================================
Write-Host "`n[5/5] TESTE REAL: Transferindo tabela pequena..." -ForegroundColor Yellow

Write-Host "  Migrando tabela 'cnaes' (2.718 registros)..."

$inicioTransf = Get-Date

# Exportar
$dumpCnaes = docker run --rm -e PGPASSWORD=password postgres:15 `
  psql -h $REMOTE_HOST -U postgres -d cnpj_processed `
  -c "\COPY cnaes TO STDOUT WITH (FORMAT CSV, HEADER)" 2>$null

# Importar
$dumpCnaes | docker exec -i cnpj_postgres_final `
  psql -U postgres -d cnpj_processed `
  -c "\COPY cnaes FROM STDIN WITH (FORMAT CSV, HEADER)" 2>$null

$fimTransf = Get-Date
$tempoTransf = ($fimTransf - $inicioTransf).TotalSeconds

Write-Host "  Tempo: $([math]::Round($tempoTransf, 2))s para 2.718 registros" -ForegroundColor Cyan

# Extrapolar para tabelas grandes
$registrosPorSeg = 2718 / $tempoTransf
$tempoEmpresasMin = (77041156 / $registrosPorSeg) / 60
$tempoEstabMin = (79225899 / $registrosPorSeg) / 60
$tempoSociosMin = (26197302 / $registrosPorSeg) / 60
$tempoTotalHoras = ($tempoEmpresasMin + $tempoEstabMin + $tempoSociosMin) / 60

Write-Host "`n  ESTIMATIVAS (single-thread):" -ForegroundColor Magenta
Write-Host "  - Empresas: $([math]::Round($tempoEmpresasMin, 1)) minutos" -ForegroundColor Gray
Write-Host "  - Estabelecimentos: $([math]::Round($tempoEstabMin, 1)) minutos" -ForegroundColor Gray
Write-Host "  - Socios: $([math]::Round($tempoSociosMin, 1)) minutos" -ForegroundColor Gray
Write-Host "  - TOTAL: $([math]::Round($tempoTotalHoras, 1)) horas" -ForegroundColor White

# ===================================================================
# ANÁLISE FINAL
# ===================================================================
Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "  ANÁLISE DE GARGALOS" -ForegroundColor Cyan
Write-Host "================================================================`n" -ForegroundColor Cyan

$gargalos = @()

if ($gargaloRede) { $gargalos += "REDE" }
if ($gargaloDisco) { $gargalos += "DISCO" }
if ($gargaloRAM) { $gargalos += "RAM" }
if ($gargaloCPU) { $gargalos += "CPU/PostgreSQL" }

if ($gargalos.Count -eq 0) {
    Write-Host "✓ Nenhum gargalo crítico detectado!" -ForegroundColor Green
    Write-Host "`nRecomendação: Use -j 6 para migração paralela" -ForegroundColor Cyan
    Write-Host "Tempo estimado: $([math]::Round($tempoTotalHoras / 6, 1)) horas com 6 workers`n" -ForegroundColor Yellow
} else {
    Write-Host "GARGALOS IDENTIFICADOS: $($gargalos -join ', ')" -ForegroundColor Red
    Write-Host ""
    
    if ($gargaloRede) {
        Write-Host "[REDE] Solucoes:" -ForegroundColor Yellow
        Write-Host "  - Conectar ambos laptops via cabo ethernet direto" -ForegroundColor White
        Write-Host "  - Usar switch Gigabit dedicado" -ForegroundColor White
        Write-Host "  - Verificar se esta em WiFi (troque para cabo!)" -ForegroundColor White
    }
    
    if ($gargaloDisco) {
        Write-Host "[DISCO] Solucoes:" -ForegroundColor Yellow
        Write-Host "  - Fazer dump para SSD externo" -ForegroundColor White
        Write-Host "  - Limpar espaco no disco principal" -ForegroundColor White
        Write-Host "  - Desativar antivirus temporariamente" -ForegroundColor White
    }
    
    if ($gargaloRAM) {
        Write-Host "[RAM] Solucoes:" -ForegroundColor Yellow
        Write-Host "  - Fechar Chrome, IDE, aplicacoes" -ForegroundColor White
        Write-Host "  - Use apenas -j 2 ou -j 4" -ForegroundColor White
        Write-Host "  - Fazer migracao tabela por tabela" -ForegroundColor White
    }
    
    Write-Host ""
}

# ===================================================================
# RECOMENDAÇÃO FINAL
# ===================================================================
Write-Host "`n================================================================" -ForegroundColor Green
Write-Host "  RECOMENDAÇÃO FINAL" -ForegroundColor Green
Write-Host "================================================================`n" -ForegroundColor Green

$workersRecomendados = [math]::Min(6, [math]::Floor($ramLivreGB / 5))

Write-Host "Workers recomendados: $workersRecomendados" -ForegroundColor Cyan
Write-Host "Tempo estimado: $([math]::Round($tempoTotalHoras / $workersRecomendados, 1)) horas" -ForegroundColor Yellow
Write-Host ""
Write-Host "Comando para amanhã:" -ForegroundColor White
Write-Host "docker run --rm -e PGPASSWORD=password \\" -ForegroundColor Gray
Write-Host "  -v `${PWD}/dump:/dump postgres:15 \\" -ForegroundColor Gray
Write-Host "  pg_dump -h 192.168.15.24 -U postgres -d cnpj_processed \\" -ForegroundColor Gray
Write-Host "  -Fd -j $workersRecomendados -f /dump/cnpj_parallel/" -ForegroundColor Gray
Write-Host "`n================================================================`n" -ForegroundColor Cyan

# Salvar relatório
$relatorio = @"
DIAGNOSTICO DE GARGALOS - $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
================================================================

REDE:
  Velocidade: $([math]::Round($velocidadeMBps, 2)) MB/s
  Status: $(if ($gargaloRede) {"GARGALO"} else {"OK"})

DISCO:
  Velocidade escrita: $([math]::Round($velocidadeDiscoMBps, 2)) MB/s
  Status: $(if ($gargaloDisco) {"GARGALO"} else {"OK"})

RAM:
  Total: $ramTotalGB GB
  Livre: $ramLivreGB GB
  Uso: $ramUsoPercent%
  Status: $(if ($gargaloRAM) {"GARGALO"} else {"OK"})

CPU/PostgreSQL:
  Query em 79M registros: $([math]::Round($tempoCPU.TotalSeconds, 2))s
  Status: $(if ($gargaloCPU) {"GARGALO"} else {"OK"})

TESTE REAL:
  Taxa: $([math]::Round($registrosPorSeg, 0)) registros/segundo
  Tempo estimado total: $([math]::Round($tempoTotalHoras, 1)) horas (single-thread)
  Com $workersRecomendados workers: $([math]::Round($tempoTotalHoras / $workersRecomendados, 1)) horas

GARGALOS: $($gargalos -join ', ')
WORKERS RECOMENDADOS: $workersRecomendados
"@

$relatorio | Out-File -FilePath "diagnostico_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt" -Encoding UTF8
Write-Host "Relatório salvo em: diagnostico_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt`n" -ForegroundColor Gray

