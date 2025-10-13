# Diagnostico simples de gargalos
$REMOTE = "192.168.15.24"

Write-Host "`n=== DIAGNOSTICO DE GARGALOS ===`n" -ForegroundColor Cyan

# 1. REDE
Write-Host "[1/5] Testando velocidade de rede..." -ForegroundColor Yellow
$query = "SELECT repeat('x', 1024*1024)::text FROM generate_series(1, 100)"
$tempoRede = Measure-Command {
    docker run --rm -e PGPASSWORD=password postgres:15 psql -h $REMOTE -U postgres -d cnpj_processed -c $query -o nul 2>$null
}
$mbps = 100 / $tempoRede.TotalSeconds
Write-Host "Velocidade: $([math]::Round($mbps, 1)) MB/s" -ForegroundColor Cyan

# 2. DISCO
Write-Host "`n[2/5] Testando velocidade de disco..." -ForegroundColor Yellow
$arquivo = "teste.bin"
$tempoDisco = Measure-Command {
    $bytes = New-Object byte[] (100*1024*1024)
    [System.IO.File]::WriteAllBytes($arquivo, $bytes)
}
$discombps = 100 / $tempoDisco.TotalSeconds
Write-Host "Escrita: $([math]::Round($discombps, 1)) MB/s" -ForegroundColor Cyan
Remove-Item $arquivo -Force

# 3. RAM
Write-Host "`n[3/5] Verificando RAM..." -ForegroundColor Yellow
$os = Get-CimInstance Win32_OperatingSystem
$ramTotal = [math]::Round($os.TotalVisibleMemorySize / 1MB, 1)
$ramLivre = [math]::Round($os.FreePhysicalMemory / 1MB, 1)
Write-Host "Total: $ramTotal GB | Livre: $ramLivre GB" -ForegroundColor Cyan

# 4. CPU
Write-Host "`n[4/5] Testando PostgreSQL..." -ForegroundColor Yellow
$tempoCPU = Measure-Command {
    docker run --rm -e PGPASSWORD=password postgres:15 psql -h $REMOTE -U postgres -d cnpj_processed -c "SELECT COUNT(*) FROM estabelecimentos WHERE municipio LIKE '%SAO%'" -t 2>$null
}
Write-Host "Query em 79M registros: $([math]::Round($tempoCPU.TotalSeconds, 1))s" -ForegroundColor Cyan

# 5. TESTE REAL
Write-Host "`n[5/5] Teste real de transferencia..." -ForegroundColor Yellow
$inicio = Get-Date
$null = docker run --rm -e PGPASSWORD=password postgres:15 psql -h $REMOTE -U postgres -d cnpj_processed -c "\COPY cnaes TO STDOUT" 2>$null | docker exec -i cnpj_postgres_final psql -U postgres -d cnpj_processed -c "\COPY cnaes FROM STDIN" 2>$null
$fim = Get-Date
$tempo = ($fim - $inicio).TotalSeconds
$regPorSeg = 2718 / $tempo
Write-Host "Taxa: $([math]::Round($regPorSeg, 0)) registros/seg" -ForegroundColor Cyan

# ANALISE
Write-Host "`n=== ANALISE ===" -ForegroundColor Green
Write-Host ""

$gargalos = @()
if ($mbps -lt 10) { $gargalos += "REDE ($([math]::Round($mbps,1)) MB/s)" }
if ($discombps -lt 50) { $gargalos += "DISCO ($([math]::Round($discombps,1)) MB/s)" }
if ($ramLivre -lt 8) { $gargalos += "RAM ($ramLivre GB livre)" }
if ($tempoCPU.TotalSeconds -gt 30) { $gargalos += "CPU/PostgreSQL" }

if ($gargalos.Count -eq 0) {
    Write-Host "OK: Nenhum gargalo detectado!" -ForegroundColor Green
    $workers = 6
} else {
    Write-Host "GARGALOS: $($gargalos -join ', ')" -ForegroundColor Red
    $workers = 4
}

# ESTIMATIVA
$tempoHoras = (182000000 / $regPorSeg) / 3600 / $workers
Write-Host "`nWorkers recomendados: $workers" -ForegroundColor Yellow
Write-Host "Tempo estimado: $([math]::Round($tempoHoras, 1)) horas`n" -ForegroundColor Cyan

# Salvar
@"
DIAGNOSTICO - $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')

REDE: $([math]::Round($mbps, 1)) MB/s
DISCO: $([math]::Round($discombps, 1)) MB/s  
RAM: $ramTotal GB total, $ramLivre GB livre
CPU: Query OK em $([math]::Round($tempoCPU.TotalSeconds, 1))s

GARGALOS: $($gargalos -join ', ')
WORKERS: $workers
TEMPO ESTIMADO: $([math]::Round($tempoHoras, 1)) horas
"@ | Out-File "diagnostico_resultado.txt"

Write-Host "Relatorio salvo em: diagnostico_resultado.txt`n"


