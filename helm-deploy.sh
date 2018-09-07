#!/bin/bash

docker run --rm -it \
  --net host \
  -e KUBECONFIG=$KUBECONFIG \
  -v $HOME/.minikube:$HOME/.minikube \
  -v $HOME/.kube:$HOME/.kube \
  -v $HOME/.config/gcloud:/root/.config/gcloud \
  -v $PWD:$PWD \
  --workdir $PWD \
  coldog/helm-deploy:latest \
  $@
