#!/bin/bash

DEPLOYMENT="deployment.yaml"
SERVICE="service.yaml"

# Verifica se o minikube está rodando
if command -v minikube >/dev/null 2>&1;
then
    echo "Verificando se o Minikube está rodando..."
    if ! minikube status | grep -q "host: Running"; then
        echo "Minikube não está rodando. Iniciando o Minikube..."
        minikube start
    else
        echo "Minikube já está rodando."
    fi
else
    echo "Minikube não encontrado. Por favor, instale o Minikube para continuar."
    exit 1
fi

echo "Criando o deployment..."
kubectl apply -f $DEPLOYMENT

echo "Criando o service..."
kubectl apply -f $SERVICE

echo "Aguardando os pods ficarem prontos..."
kubectl wait --for=condition=available --timeout=60s deployment/livros-api

echo "Iniciando o port-forwarding para localhost:8000 -> service porta 80..."
kubectl port-forward svc/livros-api-service 8000:80 >/dev/null & 2>&1 &

sleep 3

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open http://localhost:8000
elif [[ "$OSTYPE" == "darwin"* ]]; then
    open http://localhost:8000
elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    start http://localhost:8000
else
    echo "Sistema operacional não suportado para abrir o navegador automaticamente. Por favor, acesse http://localhost:8000 manualmente."
fi

echo "aplicação está rodando em http://localhost:8000"
echo "use Ctrl+C para parar o port-foward quando quiser."

wait