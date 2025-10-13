# Teste simples do LLM Service

Write-Host "Testando LLM Service..." -ForegroundColor Cyan
Write-Host ""

try {
    $body = @{
        question = "Quantos estabelecimentos temos em Sao Paulo?"
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "http://localhost:8000/ask" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 30

    if ($response.sucesso) {
        Write-Host "SUCESSO!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Resposta:" -ForegroundColor Cyan
        Write-Host $response.resposta_texto
        Write-Host ""
        Write-Host "Total de resultados: $($response.total_resultados)" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "SQL Gerado:" -ForegroundColor Gray
        Write-Host $response.sql_gerado
        Write-Host ""
        
        if ($response.total_resultados -gt 0) {
            Write-Host "Primeiros 3 registros:" -ForegroundColor Yellow
            $response.dados | Select-Object -First 3 | Format-Table
        }
    } else {
        Write-Host "ERRO:" -ForegroundColor Red
        Write-Host $response.erro
    }
} catch {
    Write-Host "ERRO de conexao:" -ForegroundColor Red
    Write-Host $_.Exception.Message
    Write-Host ""
    Write-Host "Verifique se o container esta rodando:" -ForegroundColor Yellow
    Write-Host "docker logs crm-llm --tail 20"
}

