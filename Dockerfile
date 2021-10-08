FROM python:3.8-buster as build_deps
EXPOSE 80
WORKDIR /var/arkid
ARG DEBIAN=http://mirrors.aliyun.com/debian
ARG DEBIANSRT=http://mirrors.aliyun.com/debian-security
ARG PIP="-i https://mirrors.aliyun.com/pypi/simple/"
#ARG DEBIAN=http://deb.debian.org/debian
#ARG DEBIANSRT=http://security.debian.org/debian-security
#ARG PIP="-i https://pypi.python.org/simple"

RUN set -eux; \
    sed -i "s@http://deb.debian.org/debian@$DEBIAN/@g" /etc/apt/sources.list; \
    sed -i "s@http://security.debian.org/debian-security@$DEBIANSRT@g" /etc/apt/sources.list ; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        gettext xmlsec1 \
        python-dev default-libmysqlclient-dev tini gosu; \
    # verify that the binary works
    gosu nobody true; \
    rm -rf /var/lib/apt/lists/*; \
    groupadd -r arkid && useradd -r -g arkid arkid; \
    setcap 'cap_net_bind_service=+ep' /usr/local/bin/python3.8

ADD requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

FROM build_deps as run_lint
ADD requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt
ADD . .
# ARG base_commit_id=""
RUN pre-commit install \
    && .git/hooks/pre-commit

FROM build_deps as build
ADD . .
RUN pip install mysqlclient==1.4.6 $PIP; \
    chmod +x docker-entrypoint.sh
ENTRYPOINT ["/var/arkid/docker-entrypoint.sh"]
CMD ["tini", "--", "/usr/local/bin/python3.8", "manage.py", "runserver", "0.0.0.0:80"]
