FROM python:3.6
EXPOSE 80

WORKDIR /var/oneid

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        vim supervisor gettext

RUN pip install uwsgi

ADD requirements.txt ./
RUN pip install -r requirements.txt

COPY uwsgi.ini /etc/uwsgi/uwsgi.ini

ADD . .

RUN \
    sed -i "s|LANGUAGE_CODE = 'zh_hans'|LANGUAGE_CODE = 'zh-hans'|g" oneid/settings.py && \
    python manage.py compilemessages && \
    sed -i "s|LANGUAGE_CODE = 'zh-hans'|LANGUAGE_CODE = 'zh_hans'|g" oneid/settings.py

CMD python manage.py migrate && supervisord
