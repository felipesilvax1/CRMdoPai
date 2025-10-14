@echo off
echo ========================================
echo RESTORE DO BANCO DE DADOS
echo ========================================
echo.
echo Arquivo: cnpj_processado.dump (5.36 GB)
echo Destino: crm-postgres container
echo ETA: 40-60 minutos
echo.
echo Iniciando...
echo.

REM Usar type para pipe no Windows
type cnpj_processado.dump | docker exec -i crm-postgres pg_restore -U postgres -d cnpj_processado --no-owner --no-privileges --jobs=4 -v > restore_output.log 2>&1

echo.
echo ========================================
echo RESTORE CONCLUIDO!
echo ========================================
echo.
echo Verificando dados...
docker exec crm-postgres psql -U postgres -d cnpj_processado -c "SELECT COUNT(*) FROM estabelecimentos"
echo.
echo Verifique restore_output.log para detalhes
echo.
pause

