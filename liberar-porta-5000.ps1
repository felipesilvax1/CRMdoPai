# ============================================================
# 🔓 Liberar Porta 5000 no Firewall do Windows
# ============================================================
# Execute este script como ADMINISTRADOR
# Clique com botão direito → "Executar como Administrador"

Write-Host "🔥 Liberando porta 5000 no Firewall..." -ForegroundColor Cyan

try {
    # Remover regra antiga se existir
    Remove-NetFirewallRule -DisplayName "CRM API (5000)" -ErrorAction SilentlyContinue
    
    # Criar nova regra
    New-NetFirewallRule `
        -DisplayName "CRM API (5000)" `
        -Direction Inbound `
        -LocalPort 5000 `
        -Protocol TCP `
        -Action Allow `
        -Profile Any
    
    Write-Host "✅ Porta 5000 liberada com sucesso!" -ForegroundColor Green
    
    # Testar
    Write-Host "`n🧪 Testando conexão..." -ForegroundColor Yellow
    $result = Test-NetConnection -ComputerName localhost -Port 5000
    
    if ($result.TcpTestSucceeded) {
        Write-Host "✅ Porta 5000 está acessível!" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Porta pode não estar respondendo (normal se container estiver parado)" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "❌ Erro: $_" -ForegroundColor Red
    Write-Host "`n💡 Certifique-se de executar como ADMINISTRADOR!" -ForegroundColor Yellow
}

Write-Host "`n🎯 Próximo passo: Teste no navegador" -ForegroundColor Cyan
Write-Host "   http://192.168.15.22:5000/filtros/ufs" -ForegroundColor White

Read-Host "`nPressione ENTER para sair"


