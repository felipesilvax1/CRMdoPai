# ═══════════════════════════════════════════════════════════════
# 🔍 Pre-Commit Hook - Validação Rápida
# ═══════════════════════════════════════════════════════════════
# Execute antes de cada commit para validação rápida
# ═══════════════════════════════════════════════════════════════

Write-Host ""
Write-Host "🔍 Executando validações pré-commit..." -ForegroundColor Cyan
Write-Host ""

$hasErrors = $false

# Validar JSON
Write-Host "Validando JSON files..." -ForegroundColor Yellow
$jsonFiles = Get-ChildItem -Recurse -Filter "*.json" -Exclude "node_modules","*.next" | 
    Where-Object { $_.FullName -notlike "*node_modules*" -and $_.FullName -notlike "*.next*" } |
    Select-Object -First 10

foreach ($file in $jsonFiles) {
    try {
        Get-Content $file.FullName -Raw | ConvertFrom-Json -ErrorAction Stop | Out-Null
    } catch {
        Write-Host "  ❌ JSON inválido: $($file.Name)" -ForegroundColor Red
        $hasErrors = $true
    }
}

# Lint rápido (apenas arquivos staged)
Write-Host "Executando lint..." -ForegroundColor Yellow
Push-Location next-app

try {
    npm run lint --silent 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ❌ Erros de lint encontrados" -ForegroundColor Red
        $hasErrors = $true
    }
} catch {
    # Lint falhou, mas continuar
}

Pop-Location

if ($hasErrors) {
    Write-Host ""
    Write-Host "❌ Validação falhou! Corrija os erros antes de commitar." -ForegroundColor Red
    Write-Host ""
    exit 1
} else {
    Write-Host ""
    Write-Host "✅ Validação rápida passou!" -ForegroundColor Green
    Write-Host ""
    exit 0
}

