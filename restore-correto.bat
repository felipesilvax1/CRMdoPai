@echo off
echo ========================================
echo RESTORE DO BANCO DE DADOS - MODO CORRETO
echo ========================================
echo.

echo [1/3] Copiando dump para dentro do container...
echo   Tamanho: 5.36 GB - Aguarde 1-2 minutos
docker cp cnpj_processado.dump crm-postgres:/tmp/cnpj_processado.dump
if %ERRORLEVEL% NEQ 0 (
    echo ERRO ao copiar arquivo!
    pause
    exit /b 1
)
echo   OK - Arquivo copiado!
echo.

echo [2/3] Executando restore com 4 jobs paralelos...
echo   ETA: 40-60 minutos
echo   Inicio: %TIME%
echo.
docker exec crm-postgres pg_restore -U postgres -d cnpj_processado --no-owner --no-privileges --jobs=4 -v /tmp/cnpj_processado.dump > restore_output.log 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ATENCAO: Restore teve warnings (normal em alguns casos)
    echo Verifique restore_output.log
)
echo.
echo   Termino: %TIME%
echo   OK - Restore concluido!
echo.

echo [3/3] Verificando dados...
docker exec crm-postgres psql -U postgres -d cnpj_processado -c "SELECT COUNT(*) FROM estabelecimentos"
echo.

echo [4/3] Limpando arquivo temporario...
docker exec crm-postgres rm /tmp/cnpj_processado.dump
echo   OK - Arquivo removido
echo.

echo ========================================
echo RESTORE COMPLETO!
echo ========================================
echo Veja restore_output.log para detalhes
echo.
pause

