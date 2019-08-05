#!/bin/bash

# set -o errexit

# sed -i "s|exit 10|exit 0|g" /usr/sbin/policy-rc.d

# CONFD=/etc/ldap  # ubuntu
# USER=openldap
# CONFD=/etc/openldap  # centos
# USER=ldap

USER=ldap
GROUP=ldap
CONFD=/etc/openldap

function handle_domain() {
    IFS='.' read -ra LDAP_BASE_DN_TABLE <<< "$LDAP_DOMAIN"
    for i in "${LDAP_BASE_DN_TABLE[@]}"; do
        EXT="dc=$i,"
        LDAP_BASE_DN=$LDAP_BASE_DN$EXT
    done

    LDAP_BASE_DN=${LDAP_BASE_DN::-1}
    ORG_NAME=${LDAP_BASE_DN_TABLE[0]}
}

if [ ! ${LDAP_DOMAIN} ]; then
    LDAP_DOMAIN='example.com'
fi


function gen_ssl() {
    if [ ! -e ${CONFD}/assets/certs ]; then
        mkdir -p ${CONFD}/assets/certs
        CERTS=${CONFD}/assets/certs
        INFO="/C=CN/ST=Beijing/L=Beijing/O=${ORG_NAME}/OU=ITDepartment/CN=${LDAP_DOMAIN}"
        openssl req -new -x509 -nodes -out $CERTS/ldap.crt -keyout $CERTS/ldap.key -days 1095 \
          -subj ${INFO}
    else
        sed -i "s|ldap.crt|${TLS_CRT_FILENAME}|g" ${CONFD}/slapd.conf
        sed -i "s|ldap.key|${TLS_KEY_FILENAME}|g" ${CONFD}/slapd.conf
        if [  ${TLS_CA_FILENAME} ]; then
            echo 'TLSCACertificateFile /etc/openldap/assets/certs/ca.crt' >> ${CONFD}/slapd.conf
            sed -i "s|ca.crt|${TLS_CA_FILENAME}|g" ${CONFD}/slapd.conf
        fi
    fi
}


if [ ! -e ${CONFD}/bootstrap.lock ]; then
    echo "start"
    handle_domain

    echo "start gen_ssl"
    gen_ssl

    # backend
    if [ ${BACKEND}x == 'sql'x ]; then

        if [ ${SQL_HOST} ]; then
            sed -i "s|Server=mysql|Server=${SQL_HOST}|g" /etc/odbc.ini
        fi

        if [ ${SQL_PORT} ]; then
            sed -i "s|Port=3306|Port=${SQL_PORT}|g" /etc/odbc.ini
        fi

        if [ ${SQL_DB} ]; then
            sed -i "s|Database=oneid|Database=${SQL_DB}|g" /etc/odbc.ini
        fi

        if [ ${SQL_USER} ]; then
            sed -i "s|UserName=root|UserName=${SQL_USER}|g" /etc/odbc.ini
            sed -i "s|dbuser root|dbuser ${SQL_USER}|g" ${CONFD}/assets/backends/sql
        fi

        if [ ${SQL_PWD} ]; then
            sed -i "s|Password=root|Password=${SQL_PWD}|g" /etc/odbc.ini
            sed -i "s|dbpasswd root|dbpasswd ${SQL_PWD}|g" ${CONFD}/assets/backends/sql
        fi

        cat ${CONFD}/assets/backends/sql >> ${CONFD}/slapd.conf
    elif [ ${BACKEND}x == 'man'x ]; then
        echo 'backend: depended on mounted slapd.conf'
    else
        echo 'backend: hdb(default)' >> /var/log/openldap.log
        cat ${CONFD}/assets/backends/hdb >> ${CONFD}/slapd.conf
    fi

    if [ ${LDAP_BASE_DN} ]; then
        sed -i "s|dc=example,dc=com|${LDAP_BASE_DN}|g" ${CONFD}/ldap.conf
        sed -i "s|dc=example,dc=com|${LDAP_BASE_DN}|g" ${CONFD}/slapd.conf
    fi

    if [ ${LDAP_PASSWORD} ]; then
        sed -i "s|rootpw admin|rootpw ${LDAP_PASSWORD}|g" ${CONFD}/slapd.conf
    fi

    echo "start slapd.d"
    # rm -rf ${CONFD}/slapd.d/*
    # slaptest -f ${CONFD}/slapd.conf -F ${CONFD}/slapd.d -u
    # chown -R ${USER}:${GROUP} ${CONFD}/slapd.d

    touch /var/run/slapd.args /var/run/slapd.pid
    chown ${USER}:${GROUP} /var/run/slapd.args /var/run/slapd.pid
    touch ${CONFD}/bootstrap.lock
else
    echo "Already bootstrapped. Skipping."
fi

if [ ! ${LDAP_DEBUG} ]; then
    LDAP_DEBUG=256
fi

echo "Starting OpenLDAP"
exec slapd -h 'ldaps:/// ldap:/// ldapi:///' -d -${LDAP_DEBUG} -f ${CONFD}/slapd.conf -u ${USER} -g ${GROUP} 
