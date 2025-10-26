#!/bin/bash

CPUS=2
MEMORY=4096
NAMESPACE=meme-generator

echo "=== Iniciando Minikube ==="
minikube start --driver=docker --cpus=$CPUS --memory=$MEMORY

echo "=== Usando Docker do Minikube ==="
eval $(minikube docker-env)

echo "=== Construindo imagens Docker ==="
docker build -t image_frontend:local ./frontend
docker build -t image_producer:local ./producer
docker build -t image_worker:local ./worker
docker build -t image_viewer:local ./viewer

echo "=== Aplicando namespace e PVC ==="
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/pvc.yaml

echo "=== Deploy Redis, Producer, Worker, Frontend e Viewer ==="
kubectl apply -f k8s/redis-deployment.yaml
kubectl apply -f k8s/redis-service.yaml
kubectl apply -f k8s/producer-deployment.yaml
kubectl apply -f k8s/producer-service.yaml
kubectl apply -f k8s/worker-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/viewer-deployment.yaml

# Função para verificar e reaplicar deployments de pods que falharam
reapply_failed_pods() {
    echo "=== Verificando pods não prontos no namespace $NAMESPACE ==="
    PODS=$(kubectl get pods -n $NAMESPACE --no-headers | awk '$2 !~ /1\/1|2\/2/ {print $1}')
    if [ -z "$PODS" ]; then
        echo "Todos os pods estão prontos!"
        return
    fi

    for pod in $PODS; do
        DEPLOY=$(kubectl get pod $pod -n $NAMESPACE -o jsonpath='{.metadata.labels.app}')
        echo "⚠️  Pod $pod não está pronto. Reaplicando deployment $DEPLOY..."
        kubectl rollout restart deployment $DEPLOY -n $NAMESPACE
    done
}

# Espera e reapply até que todos os pods fiquem prontos (máx 3 minutos)
timeout=180
interval=5
elapsed=0
while [ $elapsed -lt $timeout ]; do
    reapply_failed_pods
    READY=$(kubectl get pods -n $NAMESPACE --no-headers | awk '{if($2=="1/1" || $2=="2/2") count++} END {print count}')
    TOTAL=$(kubectl get pods -n $NAMESPACE --no-headers | wc -l)
    if [ "$READY" -eq "$TOTAL" ]; then
        break
    fi
    sleep $interval
    elapsed=$((elapsed + interval))
done

echo "=== Status final dos pods ==="
kubectl get pods -n $NAMESPACE

# Abrindo serviços somente se tiverem pods prontos
for svc in frontend-service viewer-service; do
    POD_COUNT=$(kubectl get pods -n $NAMESPACE -l app=${svc%-service} -o jsonpath='{.items[*].status.containerStatuses[*].ready}' | grep -c true)
    if [ "$POD_COUNT" -eq 0 ]; then
        echo "⚠️  Nenhum pod pronto para $svc. Logs recentes:"
        kubectl logs -n $NAMESPACE -l app=${svc%-service} --tail=20
    else
        echo "✅ Serviço $svc disponível. Abrindo no navegador..."
        minikube service $svc -n $NAMESPACE &
    fi
done

echo "=== Setup concluído ==="
