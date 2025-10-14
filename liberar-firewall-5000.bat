@echo off
REM ============================================================
REM Liberar porta 5000 no Windows Firewall
REM EXECUTE COMO ADMINISTRADOR (Botao direito > Executar como Administrador)
REM ============================================================

echo.
echo ========================================
echo  Liberando porta 5000 no Firewall
echo ========================================
echo.

REM Remover regra antiga se existir
netsh advfirewall firewall delete rule name="CRM API 5000" >nul 2>&1

REM Criar nova regra
netsh advfirewall firewall add rule name="CRM API 5000" dir=in action=allow protocol=TCP localport=5000

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [OK] Porta 5000 liberada com sucesso!
    echo.
    echo Testando conexao...
    powershell -Command "Test-NetConnection -ComputerName localhost -Port 5000 | Select-Object TcpTestSucceeded"
) else (
    echo.
    echo [ERRO] Nao foi possivel criar a regra!
    echo Certifique-se de executar como ADMINISTRADOR
    echo.
)

echo.
echo Pressione qualquer tecla para sair...
pause >nul


