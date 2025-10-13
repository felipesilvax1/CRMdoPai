# ========================================================
# EXECUTAR ESTE SCRIPT NO T14 (192.168.15.25)
# ========================================================
# Tempo estimado: 15-25 minutos

$CONTAINER = "c93d7f48cac6"
$DB = "cnpj_processed"
$SSD_PATH = "D:"  # AJUSTE para a letra do seu SSD externo!

Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "  DUMP LOCAL NO T14 - DIRETO NO SSD" -ForegroundColor Cyan
Write-Host "  TEMPO: 15-25 MINUTOS" -ForegroundColor Cyan
Write-Host "================================================================`n" -ForegroundColor Cyan

# Verificar se SSD esta montado
if (-not (Test-Path $SSD_PATH)) {
    Write-Host "[ERRO] SSD nao encontrado em ${SSD_PATH}!" -ForegroundColor Red
    Write-Host "Ajuste a variavel SSD_PATH no script!`n" -ForegroundColor Yellow
    exit 1
}

$espacoLivreGB = [math]::Round((Get-PSDrive ($SSD_PATH -replace ":"," ")).Free / 1GB, 1)
Write-Host "SSD montado: $SSD_PATH" -ForegroundColor Green
Write-Host "Espaco livre: $espacoLivreGB GB`n" -ForegroundColor Cyan

if ($espacoLivreGB -lt 30) {
    Write-Host "[AVISO] SSD com pouco espaco! Dump precisa ~20-25GB" -ForegroundColor Red
    $resposta = Read-Host "Continuar mesmo assim? (s/n)"
    if ($resposta -ne 's') { exit }
}

$inicio = Get-Date

Write-Host "[INICIANDO] pg_dump paralelo com 8 threads..." -ForegroundColor Yellow
Write-Host "Destino: ${SSD_PATH}\dump_cnpj_processed`n" -ForegroundColor Gray

# Dump PARALELO direto no SSD
docker exec $CONTAINER `
  pg_dump -U postgres -d $DB `
  -Fd -j 8 `
  -f /mnt/ssd/dump_cnpj_processed `
  --verbose

# Nota: Voce precisa montar o SSD no container:
# docker run --rm -v ${SSD_PATH}:/mnt/ssd ...

# Alternativa SEM montar (mais simples):
Write-Host "`n[ALTERNATIVA] Criando dump em /tmp e copiando para SSD..." -ForegroundColor Yellow

docker exec $CONTAINER `
  pg_dump -U postgres -d $DB `
  -Fd -j 8 `
  -f /tmp/dump_cnpj `
  --verbose 2>&1 | Select-String "processing|completed" | ForEach-Object {
    Write-Host "  $_" -ForegroundColor Gray
  }

# Copiar do container para SSD
Write-Host "`nCopiando dump do container para SSD..." -ForegroundColor Yellow
docker cp ${CONTAINER}:/tmp/dump_cnpj "${SSD_PATH}\dump_cnpj_processed"

$tempo = (Get-Date) - $inicio

Write-Host "`n================================================================" -ForegroundColor Green
Write-Host "  DUMP CONCLUIDO EM $([math]::Round($tempo.TotalMinutes, 1)) MINUTOS!" -ForegroundColor Green
Write-Host "================================================================`n" -ForegroundColor Green

$tamanhoGB = [math]::Round((Get-ChildItem "${SSD_PATH}\dump_cnpj_processed" -Recurse | Measure-Object -Property Length -Sum).Sum / 1GB, 2)
Write-Host "Tamanho do dump: $tamanhoGB GB" -ForegroundColor Cyan
Write-Host "`nAGORA:" -ForegroundColor Yellow
Write-Host "1. Desconecte o SSD do T14" -ForegroundColor White
Write-Host "2. Conecte no PC principal" -ForegroundColor White  
Write-Host "3. Execute: 2_RESTORE_NO_PC.ps1`n" -ForegroundColor White

Write-Host "================================================================`n" -ForegroundColor Cyan


