@echo off
echo ========================================
echo TESTE DE PERFORMANCE
echo ========================================
echo.
echo Query: Municipios de SP
echo Antes: 48 segundos
echo Esperado apos indices: 2 segundos
echo.
echo Executando...
echo.

docker exec crm-postgres psql -U postgres -d cnpj_processado -c "\timing on" -c "SELECT municipio, COUNT(*) FROM estabelecimentos WHERE uf = 'SP' GROUP BY municipio ORDER BY COUNT(*) DESC LIMIT 50"

echo.
echo ========================================

