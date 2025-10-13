# Script PowerShell para importação com barra de progresso
$ErrorActionPreference = "Continue"

$REMOTE_HOST = "192.168.15.24"
$REMOTE_DB = "cnpj_processed"
$LOCAL_CONTAINER = "cnpj_postgres_final"
$LOCAL_DB = "cnpj_processed"
$USER = "postgres"
$PASSWORD = "password"

# Tabelas e seus tamanhos estimados (em registros)
$tabelas = @(
    @{Nome="estabelecimentos"; Registros=79225899; Peso=40},
    @{Nome="empresas"; Registros=77041156; Peso=35},
    @{Nome="socios"; Registros=26197302; Peso=20},
    @{Nome="simples"; Registros=1000000; Peso=2},
    @{Nome="cnaes"; Registros=2718; Peso=1},
    @{Nome="municipios"; Registros=5570; Peso=1},
    @{Nome="naturezas"; Registros=100; Peso=0.5},
    @{Nome="qualificacoes"; Registros=100; Peso=0.5}
)

$pesoTotal = ($tabelas | Measure-Object -Property Peso -Sum).Sum

Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "  IMPORTAÇÃO POSTGRESQL - MODO PARALELO COM PROGRESSO" -ForegroundColor Cyan
Write-Host "================================================================`n" -ForegroundColor Cyan

Write-Host "[INFO] Preparando banco de dados local..." -ForegroundColor Yellow

# Dropar e recriar banco
docker exec $LOCAL_CONTAINER psql -U $USER -c "DROP DATABASE IF EXISTS $LOCAL_DB;" 2>$null
docker exec $LOCAL_CONTAINER psql -U $USER -c "CREATE DATABASE $LOCAL_DB;" 2>$null

# Copiar schema
Write-Host "[INFO] Copiando estrutura das tabelas..." -ForegroundColor Yellow
docker run --rm -e PGPASSWORD=$PASSWORD postgres:15 pg_dump -h $REMOTE_HOST -U $USER -d $REMOTE_DB --schema-only 2>$null | docker exec -i $LOCAL_CONTAINER psql -U $USER -d $LOCAL_DB 2>$null

Write-Host "[OK] Estrutura criada!`n" -ForegroundColor Green

$inicioGeral = Get-Date
$progressoGeral = 0

foreach ($tabela in $tabelas) {
    $nome = $tabela.Nome
    $peso = $tabela.Peso
    
    Write-Host "`n[$nome] Iniciando..." -ForegroundColor Cyan
    $inicio = Get-Date
    
    # Exportar
    Write-Progress -Activity "Importando banco de dados" -Status "Exportando $nome..." -PercentComplete $progressoGeral
    
    $dumpFile = "dump_$nome.csv"
    $cmdExport = "docker run --rm -e PGPASSWORD=$PASSWORD postgres:15 psql -h $REMOTE_HOST -U $USER -d $REMOTE_DB -c `"\COPY $nome TO STDOUT WITH (FORMAT CSV, HEADER)`" > $dumpFile"
    
    Invoke-Expression $cmdExport 2>$null
    
    if (Test-Path $dumpFile) {
        $tamanhoMB = [math]::Round((Get-Item $dumpFile).Length / 1MB, 1)
        Write-Host "[$nome] Exportado: $tamanhoMB MB" -ForegroundColor Gray
        
        # Importar
        Write-Progress -Activity "Importando banco de dados" -Status "Importando $nome..." -PercentComplete ($progressoGeral + ($peso/2))
        
        Get-Content $dumpFile | docker exec -i $LOCAL_CONTAINER psql -U $USER -d $LOCAL_DB -c "\COPY $nome FROM STDIN WITH (FORMAT CSV, HEADER)" 2>$null
        
        # Contar
        $count = docker exec $LOCAL_CONTAINER psql -U $USER -d $LOCAL_DB -t -c "SELECT COUNT(*) FROM $nome;" 2>$null
        $count = $count.Trim()
        
        $fim = Get-Date
        $tempo = ($fim - $inicio).TotalSeconds
        
        Write-Host "[$nome] CONCLUÍDO: $count registros em $([math]::Round($tempo, 1))s" -ForegroundColor Green
        
        # Limpar
        Remove-Item $dumpFile -Force
        
        $progressoGeral += $peso
        
        # Calcular ETA
        $tempoDecorrido = (Get-Date) - $inicioGeral
        $velocidade = $progressoGeral / $tempoDecorrido.TotalSeconds
        $tempoRestante = ($pesoTotal - $progressoGeral) / $velocidade
        
        Write-Host "  Progresso geral: $([math]::Round($progressoGeral/$pesoTotal*100, 1))% | ETA: $([math]::Round($tempoRestante/60, 1)) min" -ForegroundColor Yellow
    }
    else {
        Write-Host "[$nome] ERRO ao exportar!" -ForegroundColor Red
    }
}

Write-Progress -Activity "Importando banco de dados" -Completed

$fimGeral = Get-Date
$tempoTotal = ($fimGeral - $inicioGeral).TotalMinutes

Write-Host "`n================================================================" -ForegroundColor Green
Write-Host "  IMPORTAÇÃO CONCLUÍDA EM $([math]::Round($tempoTotal, 1)) MINUTOS!" -ForegroundColor Green
Write-Host "================================================================`n" -ForegroundColor Green

# Validação
Write-Host "`n[VALIDAÇÃO] Comparando contagens..." -ForegroundColor Cyan

$validacao = @()

foreach ($tabela in $tabelas) {
    $nome = $tabela.Nome
    
    # Remoto
    $countRemoto = docker run --rm -e PGPASSWORD=$PASSWORD postgres:15 psql -h $REMOTE_HOST -U $USER -d $REMOTE_DB -t -c "SELECT COUNT(*) FROM $nome;" 2>$null
    $countRemoto = $countRemoto.Trim()
    
    # Local
    $countLocal = docker exec $LOCAL_CONTAINER psql -U $USER -d $LOCAL_DB -t -c "SELECT COUNT(*) FROM $nome;" 2>$null
    $countLocal = $countLocal.Trim()
    
    $status = if ($countRemoto -eq $countLocal) { "OK" } else { "ERRO" }
    
    $validacao += [PSCustomObject]@{
        Tabela = $nome
        Remoto = $countRemoto
        Local = $countLocal
        Status = $status
    }
}

$validacao | Format-Table -AutoSize

$erros = ($validacao | Where-Object { $_.Status -eq "ERRO" }).Count

if ($erros -eq 0) {
    Write-Host "`n================================================================" -ForegroundColor Green
    Write-Host "  [OK] VALIDACAO COMPLETA: TODOS OS DADOS INTEGROS!" -ForegroundColor Green
    Write-Host "================================================================`n" -ForegroundColor Green
}
else {
    Write-Host "`n[!] ATENCAO: $erros tabela(s) com diferencas!" -ForegroundColor Red
}

