FROM python:3.6 as build_deps
EXPOSE 80
WORKDIR /var/oneid
RUN echo 'deb http://mirrors.aliyun.com/debian/ buster main non-free contrib \n\
deb-src http://mirrors.aliyun.com/debian/ buster main non-free contrib    \n\
deb http://mirrors.aliyun.com/debian-security buster/updates main         \n\
deb-src http://mirrors.aliyun.com/debian-security buster/updates main      \n\
deb http://mirrors.aliyun.com/debian/ buster-updates main non-free contrib \n\
deb-src http://mirrors.aliyun.com/debian/ buster-updates main non-free contrib \n\
deb http://mirrors.aliyun.com/debian/ buster-backports main non-free contrib    \n\
deb-src http://mirrors.aliyun.com/debian/ buster-backports main non-free contrib  \n'\
> /etc/apt/sources.list  \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        vim supervisor gettext xmlsec1 \
        python-dev default-libmysqlclient-dev
ADD devops/pip.conf /etc/pip.conf
ADD requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

FROM build_deps as run_lint
ADD requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt
ADD . .
ARG base_commit_id=""
RUN pre-commit install \
    && make BASE_COMMIT_ID=${base_commit_id} lint

FROM build_deps as run_test
ADD . .
RUN make test

FROM build_deps as build
RUN pip install uwsgi mysqlclient==1.4.6
ADD . .
COPY uwsgi.ini /etc/uwsgi/uwsgi.ini
RUN python manage.py compilemessages
CMD python manage.py migrate && supervisord

