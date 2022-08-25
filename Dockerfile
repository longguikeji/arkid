ARG BASEIMAGE=registry.cn-zhangjiakou.aliyuncs.com/ark-releases/python38:latest
FROM ${BASEIMAGE}
ARG DEBIAN=http://mirrors.aliyun.com/debian
ARG DEBIANSRT=http://mirrors.aliyun.com/debian-security
ARG PIP=https://mirrors.aliyun.com/pypi/simple
WORKDIR /var/arkid

ENV PYTHONUSERBASE=/var/arkid/arkid_extensions PATH=$PATH:/var/arkid/arkid_extensions/bin

ADD . .
RUN sed -i 's/MinProtocol = TLSv1.2/MinProtocol = TLSv1.0/g' /etc/ssl/openssl.cnf; \
    sed -i "s@https://mirrors.aliyun.com/pypi/simple@$PIP@g" requirements.txt; \
    cat requirements.txt; \
    pip install --disable-pip-version-check -r requirements.txt; \
    chmod +x docker-entrypoint.sh; \
    for i in `tree -f -i extension_root|grep requirements.txt`; \
    do  sed -i "s@https://mirrors.aliyun.com/pypi/simple@$PIP@g" $i; \
        pip install --disable-pip-version-check -r $i; done ; \
    mv pip.conf /etc/pip.conf
ENTRYPOINT ["/var/arkid/docker-entrypoint.sh"]
CMD ["tini", "--", "/usr/local/bin/python3.8", "manage.py", "runserver", "0.0.0.0:80"]
