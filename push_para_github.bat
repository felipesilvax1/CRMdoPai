@echo off
echo ================================================
echo   ENVIANDO PROJETO PARA GITHUB
echo ================================================
echo.

REM Reiniciar ambiente para pegar PATH atualizado
call refreshenv 2>nul

REM Verificar se git funciona
git --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Git nao encontrado. Feche este terminal e abra um novo.
    pause
    exit /b 1
)

echo [1/4] Verificando autenticacao do GitHub...
gh auth status
if errorlevel 1 (
    echo.
    echo [!] Nao autenticado. Executando login...
    gh auth login
)

echo.
echo [2/4] Criando repositorio no GitHub...
gh repo create sistema-crm-cnpj ^
    --public ^
    --source=. ^
    --description="Sistema CRM com 77M+ empresas - Next.js + Flask + PostgreSQL" ^
    --disable-wiki

if errorlevel 1 (
    echo [!] Repositorio pode ja existir. Continuando...
)

echo.
echo [3/4] Verificando status...
git status --short | more

echo.
echo [4/4] Fazendo push para GitHub...
git push -u origin main

echo.
echo ================================================
echo   CONCLUIDO!
echo ================================================
echo.
echo Acesse: https://github.com/SEU_USUARIO/sistema-crm-cnpj
echo.
pause


