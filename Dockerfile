FROM python:3.6
EXPOSE 80

WORKDIR /var/oneid

RUN apt-get update \
    && apt-get install -y --no-install-recommends vim supervisor

RUN pip install uwsgi

ADD requirements.txt ./
RUN pip install -r requirements.txt

COPY uwsgi.ini /etc/uwsgi/uwsgi.ini

ADD . .

CMD python manage.py migrate && supervisord
