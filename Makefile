ISTIO_VERSION := 1.0.1
K8S_VERSION := v1.11.2
HELM_VERSION := v2.9.1

install/istio:
	curl -L -o istio-$(ISTIO_VERSION).tgz https://github.com/istio/istio/releases/download/$(ISTIO_VERSION)/istio-$(ISTIO_VERSION)-linux.tar.gz
	tar -xzvf istio-$(ISTIO_VERSION).tgz
	mkdir -p bin
	cp istio-$(ISTIO_VERSION)/bin/istioctl ./bin/istioctl
	rm istio-$(ISTIO_VERSION).tgz
	rm -rf istio-$(ISTIO_VERSION)
.PHONY: install/istio

install/kubectl:
	curl -LO https://storage.googleapis.com/kubernetes-release/release/$(K8S_VERSION)/bin/linux/amd64/kubectl
	chmod +x ./kubectl
	mv kubectl ./bin/
.PHONY: install/kubectl

install/helm:
	curl -L -o helm-$(HELM_VERSION).tgz https://storage.googleapis.com/kubernetes-helm/helm-$(HELM_VERSION)-linux-amd64.tar.gz
	tar -xzvf helm-$(HELM_VERSION).tgz
	mv linux-amd64/helm ./bin/helm
	rm -rf linux-amd64
	rm helm-$(HELM_VERSION).tgz
.PHONY: install/helm

install: install/istio install/kubectl install/helm
.PHONY: install

build:
	docker build -t coldog/helm-deploy:latest .
.PHONY: build

deploy/example: build
	./helm-deploy.sh apply example ./example
.PHONY: deploy/example
