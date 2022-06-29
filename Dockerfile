ARG BASEIMAGE=python:3.8-buster
FROM ${BASEIMAGE} as build_deps
EXPOSE 80
WORKDIR /var/arkid
ARG DEBIAN=http://mirrors.aliyun.com/debian
ARG DEBIANSRT=http://mirrors.aliyun.com/debian-security
ARG PIP="https://mirrors.aliyun.com/pypi/simple/"
#ARG DEBIAN=http://deb.debian.org/debian
#ARG DEBIANSRT=http://security.debian.org/debian-security
#ARG PIP="https://pypi.python.org/simple"

RUN set -eux; \
    sed -i 's/MinProtocol = TLSv1.2/MinProtocol = TLSv1.0/g' /etc/ssl/openssl.cnf; \
    sed -i "s@http://deb.debian.org/debian@$DEBIAN/@g" /etc/apt/sources.list; \
    sed -i "s@http://security.debian.org/debian-security@$DEBIANSRT@g" /etc/apt/sources.list ; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        gettext xmlsec1 supervisor \
        freetds-dev freetds-bin \
        python-dev python-pip \
        python-dev default-libmysqlclient-dev tini gosu; \
    # verify that the binary works
    gosu nobody true; \
    rm -rf /var/lib/apt/lists/*; \
    groupadd -r arkid && useradd -r -g arkid arkid; \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/python3.8

ADD requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

ADD . .
RUN chmod +x docker-entrypoint.sh
ENTRYPOINT ["/var/arkid/docker-entrypoint.sh"]
CMD ["tini", "--", "/usr/local/bin/python3.8", "manage.py", "runserver", "0.0.0.0:80"]
