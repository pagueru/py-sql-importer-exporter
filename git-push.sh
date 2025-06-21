#!/bin/bash
# Script para adicionar, commitar e fazer push no git com mensagens claras
# bash git-push.sh

echo "Adicionando arquivos ao git..."
git add .

if git diff --cached --quiet; then
    echo "Nenhuma alteração para commitar."
    exit 1
fi

echo "Realizando commit..."
if git commit -F tools/commit.txt; then
    echo "Commit realizado com sucesso."
else
    echo "Erro ao realizar commit."
    exit 1
fi

echo "Enviando para o repositório remoto..."
if git push; then
    echo "Push realizado com sucesso."
else
    echo "Erro ao realizar push."
    exit 1
fi
