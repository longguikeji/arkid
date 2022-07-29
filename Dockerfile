ARG BASEIMAGE=registry.cn-zhangjiakou.aliyuncs.com/ark-releases/python38:latest
FROM ${BASEIMAGE}
ARG DEBIAN=http://mirrors.aliyun.com/debian
ARG DEBIANSRT=http://mirrors.aliyun.com/debian-security
ARG PIP=https://mirrors.aliyun.com/pypi/simple
WORKDIR /var/arkid

ADD . .
RUN sed -i "s@https://mirrors.aliyun.com/pypi/simple@$PIP@g" requirements.txt; \
    cat requirements.txt; \
    pip install --no-cache-dir -r requirements.txt; \
    chmod +x docker-entrypoint.sh
ENTRYPOINT ["/var/arkid/docker-entrypoint.sh"]
CMD ["tini", "--", "/usr/local/bin/python3.8", "manage.py", "runserver", "0.0.0.0:80"]
