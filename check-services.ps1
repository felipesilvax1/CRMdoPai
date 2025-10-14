# ═══════════════════════════════════════════════════════════════
# 🔍 Script de Verificação de Serviços
# ═══════════════════════════════════════════════════════════════
# Verifica quais serviços estão rodando e inicia os que faltam
# ═══════════════════════════════════════════════════════════════

Write-Host ""
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  🔍 VERIFICAÇÃO DE SERVIÇOS DO CRM" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Função para testar se uma porta está em uso
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

# Serviços e suas portas
$services = @(
    @{Name="Frontend Next.js"; Port=3000; Required=$false; StartCmd="cd next-app; npm run dev"},
    @{Name="API CRM"; Port=5000; Required=$true; StartCmd="docker-compose up -d crm-api"},
    @{Name="LLM Service"; Port=8000; Required=$false; StartCmd="docker-compose up -d crm-llm"},
    @{Name="Grafana"; Port=3002; Required=$false; StartCmd=".\start-observability.ps1"},
    @{Name="Prometheus"; Port=9090; Required=$false; StartCmd=".\start-observability.ps1"},
    @{Name="cAdvisor"; Port=8080; Required=$false; StartCmd=".\start-observability.ps1"},
    @{Name="LocalStack"; Port=4566; Required=$false; StartCmd=".\start-observability.ps1"}
)

$runningServices = @()
$stoppedServices = @()

Write-Host "Verificando serviços..." -ForegroundColor Yellow
Write-Host ""

foreach ($service in $services) {
    $isRunning = Test-Port -Port $service.Port
    
    if ($isRunning) {
        Write-Host "  ✅ " -NoNewline -ForegroundColor Green
        Write-Host "$($service.Name)" -NoNewline
        Write-Host " (porta $($service.Port))" -ForegroundColor Gray
        $runningServices += $service
    } else {
        if ($service.Required) {
            Write-Host "  ❌ " -NoNewline -ForegroundColor Red
        } else {
            Write-Host "  ⚪ " -NoNewline -ForegroundColor Gray
        }
        Write-Host "$($service.Name)" -NoNewline
        Write-Host " (porta $($service.Port))" -ForegroundColor Gray
        $stoppedServices += $service
    }
}

Write-Host ""
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Resumo
$totalServices = $services.Count
$runningCount = $runningServices.Count
$stoppedCount = $stoppedServices.Count

Write-Host "📊 Resumo:" -ForegroundColor Cyan
Write-Host "  🟢 Rodando: $runningCount de $totalServices" -ForegroundColor Green
Write-Host "  ⚪ Parados: $stoppedCount de $totalServices" -ForegroundColor Gray
Write-Host ""

# Verificar serviços obrigatórios
$missingRequired = $stoppedServices | Where-Object { $_.Required }

if ($missingRequired.Count -gt 0) {
    Write-Host "⚠️  SERVIÇOS OBRIGATÓRIOS NÃO ESTÃO RODANDO!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Para iniciar:" -ForegroundColor Cyan
    
    foreach ($service in $missingRequired) {
        Write-Host "  • $($service.Name): " -NoNewline
        Write-Host "$($service.StartCmd)" -ForegroundColor White
    }
    
    Write-Host ""
    $response = Read-Host "Deseja iniciar os serviços obrigatórios agora? (S/N)"
    
    if ($response -eq "S" -or $response -eq "s") {
        Write-Host ""
        Write-Host "🚀 Iniciando serviços..." -ForegroundColor Cyan
        
        foreach ($service in $missingRequired) {
            Write-Host "  Iniciando $($service.Name)..." -ForegroundColor Yellow
            
            if ($service.Name -eq "API CRM") {
                docker-compose up -d crm-api
            }
        }
        
        Write-Host ""
        Write-Host "✅ Serviços iniciados!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Aguarde alguns segundos para os serviços ficarem prontos..." -ForegroundColor Gray
        Start-Sleep -Seconds 5
    }
} else {
    Write-Host "✅ Todos os serviços obrigatórios estão rodando!" -ForegroundColor Green
}

Write-Host ""
Write-Host "💡 Dica: Execute " -NoNewline -ForegroundColor Yellow
Write-Host ".\start-observability.ps1" -NoNewline -ForegroundColor White
Write-Host " para iniciar observabilidade" -ForegroundColor Yellow
Write-Host ""
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

