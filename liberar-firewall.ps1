# ═══════════════════════════════════════════════════════════════
# Script para Liberar Portas no Firewall do Windows
# ═══════════════════════════════════════════════════════════════
# Execute como Administrador para acessar serviços do Mac/rede
# ═══════════════════════════════════════════════════════════════

Write-Host ""
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  🔓 Liberando Portas no Firewall para Acesso Remoto" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Verificar se está rodando como administrador
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "❌ Este script precisa ser executado como Administrador!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Clique com botão direito no PowerShell e escolha 'Executar como Administrador'" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

Write-Host "✅ Rodando como Administrador" -ForegroundColor Green
Write-Host ""

# Portas a serem liberadas
$portas = @(
    @{Nome="Frontend Next.js"; Porta=3000},
    @{Nome="Grafana"; Porta=3002},
    @{Nome="Loki"; Porta=3100},
    @{Nome="LocalStack"; Porta=4566},
    @{Nome="API CRM"; Porta=5000},
    @{Nome="LLM Service"; Porta=8000},
    @{Nome="cAdvisor"; Porta=8080},
    @{Nome="Prometheus"; Porta=9090}
)

Write-Host "🔓 Liberando portas no Firewall..." -ForegroundColor Yellow
Write-Host ""

foreach ($porta in $portas) {
    $ruleName = "CRM - $($porta.Nome)"
    
    # Remover regra antiga se existir
    Remove-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
    
    # Criar nova regra
    try {
        New-NetFirewallRule `
            -DisplayName $ruleName `
            -Direction Inbound `
            -Protocol TCP `
            -LocalPort $porta.Porta `
            -Action Allow `
            -Profile Private,Public | Out-Null
        
        Write-Host "  ✅ Porta $($porta.Porta) liberada ($($porta.Nome))" -ForegroundColor Green
    } catch {
        Write-Host "  ⚠️  Erro ao liberar porta $($porta.Porta)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  ✅ Portas Liberadas no Firewall!" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Mostrar IP local
Write-Host "📡 Seu IP na rede local:" -ForegroundColor Cyan
$ip = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias "Wi-Fi*" | Select-Object -First 1).IPAddress
if (-not $ip) {
    $ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -like "192.168.*"} | Select-Object -First 1).IPAddress
}

if ($ip) {
    Write-Host ""
    Write-Host "  $ip" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 No Mac, acesse:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Grafana:    " -NoNewline -ForegroundColor White
    Write-Host "http://${ip}:3002" -ForegroundColor Green
    Write-Host "  Prometheus: " -NoNewline -ForegroundColor White
    Write-Host "http://${ip}:9090" -ForegroundColor Green
    Write-Host "  Frontend:   " -NoNewline -ForegroundColor White
    Write-Host "http://${ip}:3000" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "  ⚠️  Não foi possível detectar o IP automaticamente" -ForegroundColor Yellow
    Write-Host "  Use: ipconfig no PowerShell para ver seu IP" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

