@echo off
chcp 65001 >nul
echo ================================================
echo   ENVIANDO PARA SEU REPOSITORIO GITHUB
echo ================================================
echo.
echo Repositorio: https://github.com/felipesilvax1/CRMdoPai.git
echo.

cd /d "C:\Users\PwC\Documents\CRM"

REM Atualizar PATH
set PATH=%PATH%;C:\Program Files\Git\cmd

echo [1/4] Verificando Git...
git --version
if errorlevel 1 (
    echo [ERRO] Git nao encontrado!
    pause
    exit /b 1
)

echo.
echo [2/4] Adicionando remote do GitHub...
git remote remove origin 2>nul
git remote add origin https://github.com/felipesilvax1/CRMdoPai.git

echo.
echo [3/4] Verificando arquivos commitados...
git log --oneline -1

echo.
echo [4/4] Fazendo push para GitHub...
echo (Pode pedir autenticacao - use suas credenciais do GitHub)
echo.

git push -u origin main --force

if errorlevel 0 (
    echo.
    echo ================================================
    echo   SUCESSO! Codigo enviado para o GitHub!
    echo ================================================
    echo.
    echo Acesse: https://github.com/felipesilvax1/CRMdoPai
    echo.
) else (
    echo.
    echo [ERRO] Falha no push. Tente manualmente ou via GitHub Desktop.
    echo.
)

pause


