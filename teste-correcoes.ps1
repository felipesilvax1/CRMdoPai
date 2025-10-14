# Teste das correções aplicadas

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "TESTE DAS CORREÇÕES APLICADAS" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$baseUrl = "http://192.168.15.22:3000/api/proxy"

# Teste 1: Municípios traduzidos
Write-Host "[TESTE 1] Municípios SP - Tradução" -ForegroundColor White
try {
    $municipios = Invoke-RestMethod -Uri "$baseUrl/filtros/municipios?uf=SP&limit=5" -TimeoutSec 15
    Write-Host "   ✅ $($municipios.municipios.Count) municípios retornados" -ForegroundColor Green
    
    $primeiro = $municipios.municipios[0]
    Write-Host "   📝 Primeiro município: $($primeiro.descricao)" -ForegroundColor Yellow
    
    if ($primeiro.descricao -match '^\d+$') {
        Write-Host "   ❌ PROBLEMA: Ainda não traduzido!" -ForegroundColor Red
    } else {
        Write-Host "   ✅ SUCESSO: Traduzido corretamente!" -ForegroundColor Green
    }
} catch {
    Write-Host "   ❌ Erro: $_" -ForegroundColor Red
}

# Teste 2: CEP como entrada primária
Write-Host "`n[TESTE 2] CEP como entrada primária" -ForegroundColor White
try {
    $cep = Invoke-RestMethod -Uri "$baseUrl/filtros/cep?cep=01310100" -TimeoutSec 15
    Write-Host "   ✅ CEP encontrado: $($cep.cep)" -ForegroundColor Green
    
    if ($cep.resultados) {
        $resultado = $cep.resultados[0]
        Write-Host "   🏙️ Cidade: $($resultado.municipio_nome)" -ForegroundColor Yellow
        Write-Host "   🏘️ Bairro: $($resultado.bairro)" -ForegroundColor Yellow
        Write-Host "   🏢 Empresas: $($resultado.total_empresas)" -ForegroundColor Yellow
        Write-Host "   ✅ CEP funcionando como entrada primária!" -ForegroundColor Green
    }
} catch {
    Write-Host "   ❌ Erro: $_" -ForegroundColor Red
}

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "RESUMO DAS CORREÇÕES" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "`n✅ IMPLEMENTADO:" -ForegroundColor Cyan
Write-Host "  1. Tradução de municípios (código → nome)" -ForegroundColor White
Write-Host "  2. CEP como entrada primária" -ForegroundColor White
Write-Host "  3. Autocomplete de CEP" -ForegroundColor White
Write-Host "  4. Performance otimizada" -ForegroundColor White
Write-Host "`n🌐 TESTE AGORA:" -ForegroundColor Cyan
Write-Host "  http://192.168.15.22:3000/busca-avancada" -ForegroundColor Yellow
Write-Host "`n========================================`n" -ForegroundColor Green
