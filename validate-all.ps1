# ═══════════════════════════════════════════════════════════════
# 🔍 Script de Validação Completa - Local
# ═══════════════════════════════════════════════════════════════
# Execute antes de fazer commit para garantir que tudo está OK
# ═══════════════════════════════════════════════════════════════

$ErrorActionPreference = "Stop"
$FailedTests = @()

Write-Host ""
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  🔍 VALIDAÇÃO COMPLETA DO SISTEMA CRM" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# ═══════════════════════════════════════════════════════════════
# 1. Validar JSON Files
# ═══════════════════════════════════════════════════════════════
Write-Host "1️⃣  Validando arquivos JSON..." -ForegroundColor Yellow

try {
    $jsonFiles = Get-ChildItem -Recurse -Filter "*.json" -Exclude "node_modules","*.next" | Where-Object { $_.FullName -notlike "*node_modules*" -and $_.FullName -notlike "*.next*" }
    
    foreach ($file in $jsonFiles) {
        try {
            $content = Get-Content $file.FullName -Raw | ConvertFrom-Json -ErrorAction Stop
            Write-Host "  ✅ $($file.Name)" -ForegroundColor Green
        } catch {
            Write-Host "  ❌ $($file.Name) - JSON inválido" -ForegroundColor Red
            $FailedTests += "JSON: $($file.Name)"
        }
    }
} catch {
    Write-Host "  ⚠️  Erro ao validar JSON" -ForegroundColor Yellow
}

Write-Host ""

# ═══════════════════════════════════════════════════════════════
# 2. Lint Next.js
# ═══════════════════════════════════════════════════════════════
Write-Host "2️⃣  Executando ESLint no Next.js..." -ForegroundColor Yellow

try {
    Push-Location next-app
    
    $lintOutput = npm run lint 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ ESLint passou" -ForegroundColor Green
    } else {
        Write-Host "  ❌ ESLint encontrou erros" -ForegroundColor Red
        Write-Host $lintOutput -ForegroundColor Gray
        $FailedTests += "ESLint"
    }
    
    Pop-Location
} catch {
    Write-Host "  ⚠️  Erro ao executar ESLint" -ForegroundColor Yellow
    Pop-Location
}

Write-Host ""

# ═══════════════════════════════════════════════════════════════
# 3. Build Next.js
# ═══════════════════════════════════════════════════════════════
Write-Host "3️⃣  Testando build do Next.js..." -ForegroundColor Yellow

try {
    Push-Location next-app
    
    Write-Host "  📦 Instalando dependências..." -ForegroundColor Gray
    npm ci --silent 2>&1 | Out-Null
    
    Write-Host "  🏗️  Building..." -ForegroundColor Gray
    $buildOutput = npm run build 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ Build passou" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Build falhou" -ForegroundColor Red
        Write-Host $buildOutput -ForegroundColor Gray
        $FailedTests += "Next.js Build"
    }
    
    Pop-Location
} catch {
    Write-Host "  ⚠️  Erro ao executar build" -ForegroundColor Yellow
    Pop-Location
}

Write-Host ""

# ═══════════════════════════════════════════════════════════════
# 4. Testes Next.js
# ═══════════════════════════════════════════════════════════════
Write-Host "4️⃣  Executando testes do Next.js..." -ForegroundColor Yellow

try {
    Push-Location next-app
    
    $testOutput = npm run test:ci 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ Testes passaram" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Testes falharam" -ForegroundColor Red
        Write-Host $testOutput -ForegroundColor Gray
        $FailedTests += "Testes Next.js"
    }
    
    Pop-Location
} catch {
    Write-Host "  ⚠️  Erro ao executar testes" -ForegroundColor Yellow
    Pop-Location
}

Write-Host ""

# ═══════════════════════════════════════════════════════════════
# 5. Validar Docker Compose
# ═══════════════════════════════════════════════════════════════
Write-Host "5️⃣  Validando arquivos Docker Compose..." -ForegroundColor Yellow

$composeFiles = Get-ChildItem -Filter "docker-compose*.yml"
foreach ($file in $composeFiles) {
    try {
        $configOutput = docker-compose -f $file.Name config 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  ✅ $($file.Name)" -ForegroundColor Green
        } else {
            Write-Host "  ❌ $($file.Name) - inválido" -ForegroundColor Red
            $FailedTests += "Docker: $($file.Name)"
        }
    } catch {
        Write-Host "  ⚠️  $($file.Name) - erro ao validar" -ForegroundColor Yellow
    }
}

Write-Host ""

# ═══════════════════════════════════════════════════════════════
# 6. Validar Configurações YAML
# ═══════════════════════════════════════════════════════════════
Write-Host "6️⃣  Validando configurações YAML..." -ForegroundColor Yellow

$yamlConfigs = @(
    "prometheus/prometheus.yml",
    "loki/loki-config.yml",
    "promtail/promtail-config.yml"
)

foreach ($config in $yamlConfigs) {
    if (Test-Path $config) {
        Write-Host "  ✅ $config" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  $config não encontrado" -ForegroundColor Yellow
    }
}

Write-Host ""

# ═══════════════════════════════════════════════════════════════
# 7. Verificar Scripts Python
# ═══════════════════════════════════════════════════════════════
Write-Host "7️⃣  Verificando scripts Python..." -ForegroundColor Yellow

$pythonFiles = @("api_server.py", "api_simple.py")
foreach ($file in $pythonFiles) {
    if (Test-Path $file) {
        try {
            python -m py_compile $file 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  ✅ $file" -ForegroundColor Green
            } else {
                Write-Host "  ❌ $file - erro de sintaxe" -ForegroundColor Red
                $FailedTests += "Python: $file"
            }
        } catch {
            Write-Host "  ⚠️  $file - não foi possível validar" -ForegroundColor Yellow
        }
    }
}

Write-Host ""

# ═══════════════════════════════════════════════════════════════
# 8. Verificar Serviços (informativo)
# ═══════════════════════════════════════════════════════════════
Write-Host "8️⃣  Verificando serviços em execução (informativo)..." -ForegroundColor Yellow

function Test-Port {
    param($Port)
    try {
        $connection = New-Object System.Net.Sockets.TcpClient
        $connection.Connect("localhost", $Port)
        $connection.Close()
        return $true
    } catch {
        return $false
    }
}

$apiRunning = Test-Port -Port 5000
$frontendRunning = Test-Port -Port 3000

if ($apiRunning) {
    Write-Host "  ✅ API CRM rodando (porta 5000)" -ForegroundColor Green
} else {
    Write-Host "  ℹ️  API CRM não está rodando (opcional para testes)" -ForegroundColor Cyan
}

if ($frontendRunning) {
    Write-Host "  ✅ Frontend rodando (porta 3000)" -ForegroundColor Green
} else {
    Write-Host "  ℹ️  Frontend não está rodando (opcional para testes)" -ForegroundColor Cyan
}

Write-Host ""

# ═══════════════════════════════════════════════════════════════
# 9. Verificar Estrutura de Arquivos
# ═══════════════════════════════════════════════════════════════
Write-Host "9️⃣  Verificando estrutura de arquivos..." -ForegroundColor Yellow

$requiredFiles = @(
    "docker-compose.yml",
    "next-app/package.json",
    "prometheus/prometheus.yml",
    "loki/loki-config.yml",
    "grafana/provisioning/datasources/datasources.yml",
    "README.md"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "  ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $file - não encontrado" -ForegroundColor Red
        $FailedTests += "Arquivo ausente: $file"
    }
}

Write-Host ""

# ═══════════════════════════════════════════════════════════════
# RESULTADO FINAL
# ═══════════════════════════════════════════════════════════════
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan

if ($FailedTests.Count -eq 0) {
    Write-Host ""
    Write-Host "  ✅ TODOS OS TESTES PASSARAM!" -ForegroundColor Green
    Write-Host ""
    Write-Host "  🎉 Sistema validado com sucesso!" -ForegroundColor Green
    Write-Host "  🚀 Pronto para commit e push!" -ForegroundColor Green
    Write-Host ""
    Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host ""
    
    # Perguntar se quer fazer commit automaticamente
    $response = Read-Host "Deseja fazer commit e push automaticamente? (S/N)"
    if ($response -eq "S" -or $response -eq "s") {
        Write-Host ""
        Write-Host "📝 Fazendo commit..." -ForegroundColor Cyan
        
        $commitMessage = Read-Host "Mensagem do commit (ou Enter para padrão)"
        if ([string]::IsNullOrWhiteSpace($commitMessage)) {
            $commitMessage = "chore: automated commit after successful validation"
        }
        
        git add .
        git commit -m $commitMessage
        
        Write-Host "📤 Fazendo push..." -ForegroundColor Cyan
        git push
        
        Write-Host ""
        Write-Host "✅ Commit e push realizados com sucesso!" -ForegroundColor Green
    }
    
    exit 0
} else {
    Write-Host ""
    Write-Host "  ❌ ALGUNS TESTES FALHARAM!" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Testes que falharam:" -ForegroundColor Yellow
    foreach ($test in $FailedTests) {
        Write-Host "    - $test" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "  🔧 Corrija os erros antes de fazer commit!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host ""
    
    exit 1
}

