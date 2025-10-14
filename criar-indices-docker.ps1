# ========================================
# CRIAR ÍNDICES DE PERFORMANCE - DOCKER
# ========================================
# ETA: 20-40 min
# Executa em background

$ErrorActionPreference = "Continue"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "CRIANDO INDICES DE PERFORMANCE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$startTime = Get-Date
Write-Host "`nHora inicio: $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Gray
Write-Host "ETA: 20-40 minutos`n" -ForegroundColor Yellow

# Índices a criar
$indices = @(
    @{
        nome = "idx_estabelecimentos_uf"
        sql = "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_estabelecimentos_uf ON estabelecimentos(uf)"
        desc = "Filtro UF"
    },
    @{
        nome = "idx_estabelecimentos_municipio"
        sql = "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_estabelecimentos_municipio ON estabelecimentos(municipio)"
        desc = "Filtro Município"
    },
    @{
        nome = "idx_estabelecimentos_uf_municipio"
        sql = "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_estabelecimentos_uf_municipio ON estabelecimentos(uf, municipio)"
        desc = "Filtro UF + Município (cascata)"
    },
    @{
        nome = "idx_estabelecimentos_bairro"
        sql = "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_estabelecimentos_bairro ON estabelecimentos(bairro)"
        desc = "Filtro Bairro"
    },
    @{
        nome = "idx_estabelecimentos_cnae"
        sql = "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_estabelecimentos_cnae ON estabelecimentos(cnae_fiscal)"
        desc = "Filtro CNAE"
    },
    @{
        nome = "idx_estabelecimentos_situacao"
        sql = "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_estabelecimentos_situacao ON estabelecimentos(situacao_cadastral)"
        desc = "Filtro Situação"
    },
    @{
        nome = "idx_estabelecimentos_cep"
        sql = "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_estabelecimentos_cep ON estabelecimentos(cep)"
        desc = "Filtro CEP"
    },
    @{
        nome = "idx_estabelecimentos_ddd"
        sql = "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_estabelecimentos_ddd ON estabelecimentos(ddd1)"
        desc = "Filtro DDD"
    }
)

$criadosComSucesso = 0
$total = $indices.Count

Write-Host "Total de indices a criar: $total`n" -ForegroundColor White
Write-Host "Modo: CONCURRENTLY (nao bloqueia o BD)`n" -ForegroundColor Green

# Criar cada índice
foreach ($i in 0..($total-1)) {
    $indice = $indices[$i]
    $num = $i + 1
    
    Write-Host "[$num/$total] $($indice.desc)" -ForegroundColor Cyan
    Write-Host "    Indice: $($indice.nome)" -ForegroundColor Gray
    
    # Verificar se já existe
    $checkSql = "SELECT 1 FROM pg_indexes WHERE indexname = '$($indice.nome)'"
    $exists = docker exec crm-postgres psql -U postgres -d cnpj_processado -t -c "$checkSql" 2>&1
    
    if ($exists -match "1") {
        Write-Host "    ✅ Ja existe, pulando..." -ForegroundColor Green
        $criadosComSucesso++
        continue
    }
    
    # Criar índice
    Write-Host "    ⏳ Criando..." -ForegroundColor Yellow
    $indexStart = Get-Date
    
    $result = docker exec crm-postgres psql -U postgres -d cnpj_processado -c "$($indice.sql)" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        $indexDuration = ((Get-Date) - $indexStart).TotalSeconds
        Write-Host "    ✅ Criado em $([math]::Round($indexDuration, 1))s" -ForegroundColor Green
        $criadosComSucesso++
    } else {
        Write-Host "    ⚠️  Erro: $result" -ForegroundColor Red
    }
    
    Write-Host ""
}

# Resumo
$endTime = Get-Date
$duration = ($endTime - $startTime).TotalMinutes

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "✅ INDICES CRIADOS COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

Write-Host "`n📊 Estatisticas:" -ForegroundColor Cyan
Write-Host "   • Indices criados: $criadosComSucesso/$total" -ForegroundColor White
Write-Host "   • Tempo total: $([math]::Round($duration, 1)) min" -ForegroundColor White
Write-Host "   • Hora termino: $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor White

# Verificar performance
Write-Host "`n🔍 Testando performance..." -ForegroundColor Yellow
$testStart = Get-Date
$testSql = "SELECT municipio, COUNT(*) FROM estabelecimentos WHERE uf = 'SP' GROUP BY municipio ORDER BY COUNT(*) DESC LIMIT 50"
$testResult = docker exec crm-postgres psql -U postgres -d cnpj_processado -c "\timing on" -c "$testSql" 2>&1

if ($testResult -match "Time: (\d+\.\d+) ms") {
    $ms = [math]::Round([decimal]$matches[1])
    $seconds = [math]::Round($ms / 1000, 2)
    
    Write-Host "   Query teste (SP municipios): ${seconds}s" -ForegroundColor Green
    
    if ($seconds -lt 5) {
        Write-Host "   🎉 EXCELENTE! Muito mais rapido que antes (48s)!" -ForegroundColor Green
    } elseif ($seconds -lt 10) {
        Write-Host "   ✅ BOM! Melhoria significativa!" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Ainda lento, pode precisar de otimizacao adicional" -ForegroundColor Yellow
    }
}

Write-Host "`n🚀 Proximo passo: Switch da API para Docker!" -ForegroundColor Cyan
Write-Host "`n========================================`n" -ForegroundColor Green

# Salvar resultado
$report = @"
========================================
RELATÓRIO - CRIAÇÃO DE ÍNDICES
========================================
Data: $(Get-Date -Format 'dd/MM/yyyy HH:mm:ss')

ÍNDICES CRIADOS: $criadosComSucesso/$total
TEMPO TOTAL: $([math]::Round($duration, 1)) min

DETALHES:
$(foreach ($indice in $indices) { "  • $($indice.nome): $($indice.desc)`n" })

PRÓXIMOS PASSOS:
1. Switch da API para Docker (porta 5433)
2. Validar performance final
3. Teste completo do sistema
========================================
"@

Set-Content -Path "relatorio_indices.txt" -Value $report
Write-Host "📄 Relatorio salvo em: relatorio_indices.txt" -ForegroundColor Gray

Write-Host "`nPressione qualquer tecla para fechar..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')

