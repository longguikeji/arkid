# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.134.0/containers/python-3/.devcontainer/base.Dockerfile
ARG VARIANT="3.6"
# FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}

# FROM newbe36524/vscode_python:0-3
FROM registry.cn-hangzhou.aliyuncs.com/newbe36524/vscode_python:0-3.6

# [Optional] Allow the vscode user to pip install globally w/o sudo
ENV PIP_TARGET=/usr/local/pip-global
ENV PYTHONPATH=${PIP_TARGET}:${PYTHONPATH}
ENV PATH=${PIP_TARGET}/bin:${PATH}
RUN if ! cat /etc/group | grep -e "^pip-global:" > /dev/null 2>&1; then groupadd -r pip-global; fi \
    && usermod -a -G pip-global vscode \
    && umask 0002 && mkdir -p ${PIP_TARGET} \
    && chown :pip-global ${PIP_TARGET} \
    && ( [ ! -f "/etc/profile.d/00-restore-env.sh" ] || sed -i -e "s/export PATH=/export PATH=\/usr\/local\/pip-global:/" /etc/profile.d/00-restore-env.sh )

RUN sed -i "s@http://deb.debian.org/debian@http://mirrors.aliyun.com/debian/@g" /etc/apt/sources.list &&\
    sed -i "s@http://security.debian.org/debian-security@http://mirrors.aliyun.com/debian-security@g" /etc/apt/sources.list

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        vim supervisor gettext xmlsec1 \
        python-dev default-libmysqlclient-dev

RUN pip install uwsgi mysqlclient==1.4.6 -i https://mirrors.aliyun.com/pypi/simple/


# RUN apt-get update \
#     && apt-get install -y --no-install-recommends \
#         vim supervisor gettext xmlsec1 \
#         python-dev default-libmysqlclient-dev
# RUN pip install uwsgi mysqlclient==1.4.6
# [Optional] If your pip requirements rarely change, uncomment this section to add them to the image.
# COPY requirements.txt /tmp/pip-tmp/
# RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \
#    && rm -rf /tmp/pip-tmp

# [Optional] Uncomment this section to install additional OS packages.
# RUN apt-get update \
#     && export DEBIAN_FRONTEND=noninteractive \
#     && apt-get -y install --no-install-recommends <your-package-list-here>
