#!/bin/bash
echo "Instalando dependências do Python..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Erro ao instalar dependências."
    exit 1
fi
echo "Dependências instaladas com sucesso."
echo "Executando o programa..."
python main.py
