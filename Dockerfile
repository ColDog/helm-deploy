FROM python:3.7.0-alpine3.8
WORKDIR /bin/helm-deploy

RUN apk add --no-cache ca-certificates && \
  pip --no-cache-dir install pyyaml ansicolors

ADD bin/ /bin
ADD helm-deploy /bin/helm-deploy
ENTRYPOINT ["python", "/bin/helm-deploy/main.py"]
