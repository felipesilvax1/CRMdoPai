#!/usr/bin/env pwsh
# -*- coding: utf-8 -*-
<#
.SYNOPSIS
    Teste completo de busca avançada direto no localhost

.DESCRIPTION
    Testa o endpoint /query/avancada diretamente no localhost:5000
    Cidades: Carapicuíba, Barueri, Osasco, Jandira
#>

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TESTE COMPLETO DE BUSCA AVANCADA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$API_URL = "http://localhost:5000"

function Testar-Busca {
    param(
        [string]$Nome,
        [hashtable]$Filtros
    )
    
    Write-Host "`n[TESTE] $Nome" -ForegroundColor Yellow
    
    try {
        $start = Get-Date
        $response = Invoke-RestMethod -Uri "$API_URL/query/avancada" -Body $Filtros -Method Get -ErrorAction Stop
        $elapsed = (Get-Date) - $start
        
        $total = $response.total
        $encontrados = $response.dados.Count
        $tempo_api = $response.tempo_ms
        
        Write-Host "  Resultado: $encontrados registros de $total total" -ForegroundColor Green
        Write-Host "  Tempo API: ${tempo_api}ms" -ForegroundColor Green
        Write-Host "  Tempo Total: $($elapsed.TotalMilliseconds)ms" -ForegroundColor Green
        
        if ($encontrados -gt 0) {
            Write-Host "  Primeiras empresas:" -ForegroundColor White
            for ($i = 0; $i -lt [Math]::Min(2, $encontrados); $i++) {
                $empresa = $response.dados[$i]
                $razao = if ($empresa.razao_social) { $empresa.razao_social } else { "N/A" }
                Write-Host "    - $razao" -ForegroundColor Gray
                Write-Host "      CNPJ: $($empresa.cnpj) | $($empresa.bairro), $($empresa.municipio_nome)/$($empresa.uf)" -ForegroundColor DarkGray
            }
            Write-Host "  [SUCESSO]" -ForegroundColor Green
            return $true
        } else {
            Write-Host "  [FALHA] Nenhum registro encontrado" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "  [ERRO] $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# ===========================================
# TESTES POR CIDADE
# ===========================================

$sucessos = 0
$total_testes = 0

# TESTE 1: Carapicuíba + Bairro Ariston (caso reportado)
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "CARAPICUIBA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$total_testes++
if (Testar-Busca -Nome "Carapicuíba - Bairro ARISTON" -Filtros @{
    uf = "SP"
    municipio = "CARAPICUIBA"
    bairro = "ARISTON"
    situacao = "02"
    limit = 5
}) { $sucessos++ }

$total_testes++
if (Testar-Busca -Nome "Carapicuíba - Bairro CIDADE ARISTON" -Filtros @{
    uf = "SP"
    municipio = "CARAPICUIBA"
    bairro = "CIDADE ARISTON"
    situacao = "02"
    limit = 5
}) { $sucessos++ }

$total_testes++
if (Testar-Busca -Nome "Carapicuíba - Todas empresas ativas" -Filtros @{
    uf = "SP"
    municipio = "CARAPICUIBA"
    situacao = "02"
    limit = 10
}) { $sucessos++ }

# TESTE 2: Barueri
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "BARUERI" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$total_testes++
if (Testar-Busca -Nome "Barueri - Bairro ALPHAVILLE" -Filtros @{
    uf = "SP"
    municipio = "BARUERI"
    bairro = "ALPHAVILLE"
    situacao = "02"
    limit = 5
}) { $sucessos++ }

$total_testes++
if (Testar-Busca -Nome "Barueri - Bairro CENTRO" -Filtros @{
    uf = "SP"
    municipio = "BARUERI"
    bairro = "CENTRO"
    situacao = "02"
    limit = 5
}) { $sucessos++ }

$total_testes++
if (Testar-Busca -Nome "Barueri - Todas empresas ativas" -Filtros @{
    uf = "SP"
    municipio = "BARUERI"
    situacao = "02"
    limit = 10
}) { $sucessos++ }

# TESTE 3: Osasco
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "OSASCO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$total_testes++
if (Testar-Busca -Nome "Osasco - Bairro CENTRO" -Filtros @{
    uf = "SP"
    municipio = "OSASCO"
    bairro = "CENTRO"
    situacao = "02"
    limit = 5
}) { $sucessos++ }

$total_testes++
if (Testar-Busca -Nome "Osasco - Bairro PRESIDENTE ALTINO" -Filtros @{
    uf = "SP"
    municipio = "OSASCO"
    bairro = "PRESIDENTE ALTINO"
    situacao = "02"
    limit = 5
}) { $sucessos++ }

$total_testes++
if (Testar-Busca -Nome "Osasco - Todas empresas ativas" -Filtros @{
    uf = "SP"
    municipio = "OSASCO"
    situacao = "02"
    limit = 10
}) { $sucessos++ }

# TESTE 4: Jandira
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "JANDIRA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$total_testes++
if (Testar-Busca -Nome "Jandira - Bairro CENTRO" -Filtros @{
    uf = "SP"
    municipio = "JANDIRA"
    bairro = "CENTRO"
    situacao = "02"
    limit = 5
}) { $sucessos++ }

$total_testes++
if (Testar-Busca -Nome "Jandira - Bairro JARDIM ALVORADA" -Filtros @{
    uf = "SP"
    municipio = "JANDIRA"
    bairro = "JARDIM ALVORADA"
    situacao = "02"
    limit = 5
}) { $sucessos++ }

$total_testes++
if (Testar-Busca -Nome "Jandira - Todas empresas ativas" -Filtros @{
    uf = "SP"
    municipio = "JANDIRA"
    situacao = "02"
    limit = 10
}) { $sucessos++ }

# TESTE 5: Apenas UF (sem município)
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "TESTES GERAIS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$total_testes++
if (Testar-Busca -Nome "São Paulo - Apenas UF (limit 10)" -Filtros @{
    uf = "SP"
    situacao = "02"
    limit = 10
}) { $sucessos++ }

$total_testes++
if (Testar-Busca -Nome "São Paulo - Matriz (limit 10)" -Filtros @{
    uf = "SP"
    matrizFilial = "1"
    situacao = "02"
    limit = 10
}) { $sucessos++ }

# ===========================================
# RESULTADO FINAL
# ===========================================

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "RESULTADO FINAL" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$taxa_sucesso = [math]::Round(($sucessos / $total_testes) * 100, 2)

Write-Host "Total de testes: $total_testes" -ForegroundColor White
Write-Host "Sucessos: $sucessos" -ForegroundColor Green
Write-Host "Falhas: $($total_testes - $sucessos)" -ForegroundColor Red
Write-Host "Taxa de sucesso: $taxa_sucesso%" -ForegroundColor $(if ($taxa_sucesso -ge 90) { "Green" } elseif ($taxa_sucesso -ge 70) { "Yellow" } else { "Red" })

if ($sucessos -eq $total_testes) {
    Write-Host "`n[TODOS OS TESTES PASSARAM!]" -ForegroundColor Green
    exit 0
} elseif ($taxa_sucesso -ge 80) {
    Write-Host "`n[MAIORIA DOS TESTES PASSOU]" -ForegroundColor Yellow
    exit 0
} else {
    Write-Host "`n[MUITOS TESTES FALHARAM - VERIFICAR]" -ForegroundColor Red
    exit 1
}

