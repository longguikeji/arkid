FROM python:3.6

EXPOSE 9094

ADD templates /templates
ADD bin/oauth-proxy.linux.amd64 /

ENTRYPOINT ["/oauth-proxy.linux.amd64"]
