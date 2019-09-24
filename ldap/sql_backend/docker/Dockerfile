FROM centos:7

RUN yum -y install \
        openldap \
        compat-openldap \
        openldap-clients \
        openldap-servers \
        openldap-servers-sql \
        openldap-devel \
        openssl

ADD http://repo.mysql.com/yum/mysql-connectors-community/el/7/x86_64//mysql-connector-odbc-5.3.9-1.el7.x86_64.rpm /tmp
RUN yum -y install unixODBC \
    && rpm -ivh  /tmp/mysql-connector-odbc-5.3.9-1.el7.x86_64.rpm

RUN touch /tmp/odbc.log
ADD start.sh /usr/local/bin/start
ADD slapd.conf /etc/openldap/slapd.conf
ADD ldap.conf /etc/openldap/ldap.conf
ADD odbc/* /etc/
ADD backends/* /etc/openldap/assets/backends/

EXPOSE 389 636

LABEL monitored=True

RUN touch /var/log/openldap.log && chmod 666 /var/log/openldap.log

CMD start
