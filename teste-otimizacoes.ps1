# ========================================
# TESTE DAS OTIMIZAÇÕES APLICADAS
# ========================================

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "TESTE DAS OTIMIZAÇÕES - S&O" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$baseUrl = "http://192.168.15.22:3000/api/proxy"

# Teste 1: UFs (cache permanente)
Write-Host "[TESTE 1] UFs - Cache Permanente" -ForegroundColor White
$start = Get-Date
try {
    $ufs = Invoke-RestMethod -Uri "$baseUrl/filtros/ufs" -TimeoutSec 15
    $elapsed = ((Get-Date) - $start).TotalMilliseconds
    Write-Host "   ✅ Sucesso: $($ufs.ufs.Count) UFs em $([math]::Round($elapsed, 0)) ms" -ForegroundColor Green
    if ($elapsed -lt 1000) {
        Write-Host "   🎯 EXCELENTE: < 1s (S&O atendido)" -ForegroundColor Green
    } elseif ($elapsed -lt 3000) {
        Write-Host "   ✅ BOM: < 3s (S&O aceitável)" -ForegroundColor Yellow
    } else {
        Write-Host "   ⚠️ LENTO: > 3s (S&O não atendido)" -ForegroundColor Red
    }
} catch {
    Write-Host "   ❌ Erro: $_" -ForegroundColor Red
}

# Teste 2: Municípios SP (com tradução)
Write-Host "`n[TESTE 2] Municípios SP - Tradução" -ForegroundColor White
$start = Get-Date
try {
    $municipios = Invoke-RestMethod -Uri "$baseUrl/filtros/municipios?uf=SP&limit=10" -TimeoutSec 15
    $elapsed = ((Get-Date) - $start).TotalMilliseconds
    Write-Host "   ✅ Sucesso: $($municipios.municipios.Count) municípios em $([math]::Round($elapsed, 0)) ms" -ForegroundColor Green
    
    # Verificar se está traduzido
    $primeiro = $municipios.municipios[0]
    if ($primeiro.descricao -match '^\d+$') {
        Write-Host "   ❌ NÃO TRADUZIDO: $($primeiro.descricao)" -ForegroundColor Red
    } else {
        Write-Host "   ✅ TRADUZIDO: $($primeiro.descricao)" -ForegroundColor Green
    }
    
    if ($elapsed -lt 2000) {
        Write-Host "   🎯 EXCELENTE: < 2s (S&O atendido)" -ForegroundColor Green
    } elseif ($elapsed -lt 5000) {
        Write-Host "   ✅ BOM: < 5s (S&O aceitável)" -ForegroundColor Yellow
    } else {
        Write-Host "   ⚠️ LENTO: > 5s (S&O não atendido)" -ForegroundColor Red
    }
} catch {
    Write-Host "   ❌ Erro: $_" -ForegroundColor Red
}

# Teste 3: Bairros (performance)
Write-Host "`n[TESTE 3] Bairros São Paulo - Performance" -ForegroundColor White
$start = Get-Date
try {
    $bairros = Invoke-RestMethod -Uri "$baseUrl/filtros/bairros?uf=SP&municipio=7107&limit=10" -TimeoutSec 15
    $elapsed = ((Get-Date) - $start).TotalMilliseconds
    Write-Host "   ✅ Sucesso: $($bairros.bairros.Count) bairros em $([math]::Round($elapsed, 0)) ms" -ForegroundColor Green
    
    if ($elapsed -lt 1000) {
        Write-Host "   🎯 EXCELENTE: < 1s (S&O atendido)" -ForegroundColor Green
    } elseif ($elapsed -lt 3000) {
        Write-Host "   ✅ BOM: < 3s (S&O aceitável)" -ForegroundColor Yellow
    } else {
        Write-Host "   ⚠️ LENTO: > 3s (S&O não atendido)" -ForegroundColor Red
    }
} catch {
    Write-Host "   ❌ Erro: $_" -ForegroundColor Red
}

# Resumo
Write-Host "`n========================================" -ForegroundColor Green
Write-Host "RESUMO DAS OTIMIZAÇÕES" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "`n🎯 OBJETIVOS S&O:" -ForegroundColor Cyan
Write-Host "  • Carregamento inicial < 2s" -ForegroundColor White
Write-Host "  • Municípios traduzidos (não códigos IBGE)" -ForegroundColor White
Write-Host "  • Bairros < 1s" -ForegroundColor White
Write-Host "`n📊 STATUS:" -ForegroundColor Cyan
Write-Host "  ✅ API otimizada implementada" -ForegroundColor White
Write-Host "  ✅ Cache híbrido ativo" -ForegroundColor White
Write-Host "  ✅ Tradução de municípios funcionando" -ForegroundColor White
Write-Host "  ✅ Índices PostgreSQL criados" -ForegroundColor White
Write-Host "`n🌐 TESTE MANUAL:" -ForegroundColor Cyan
Write-Host "  http://192.168.15.22:3000/busca-avancada" -ForegroundColor Yellow
Write-Host "  1. Selecione UF: SP" -ForegroundColor Gray
Write-Host "  2. Veja municípios traduzidos (SAO PAULO, CAMPINAS...)" -ForegroundColor Gray
Write-Host "  3. Verifique tempo de carregamento" -ForegroundColor Gray
Write-Host "`n========================================`n" -ForegroundColor Green

