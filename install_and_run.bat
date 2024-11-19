@echo off
echo Instalando dependências do Python...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Ocorreu um erro ao instalar as dependências.
    pause
    exit /b
)
echo Dependências instaladas com sucesso.

echo Executando o programa...
python main.py
pause
