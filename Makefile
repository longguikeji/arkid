VERSION ?= `date +%Y%m%d`

all: docker

requirements:
	pipenv run pipenv_to_requirements -f

docker: docker-build docker-push

docker-build:
	docker build -t harbor.longguikeji.com/ark-releases/ark-oneid:$(VERSION) .

docker-push:
	docker push harbor.longguikeji.com/ark-releases/ark-oneid:$(VERSION)


sql-ldap-docker: sql-ldap-docker-build sql-ldap-docker-push

sql-ldap-docker-build:
	cd ldap/sql_backend/docker && \
	docker build -t harbor.longguikeji.com/ark-releases/ark-sql-ldap:$(VERSION) .
sql-ldap-docker-push:
	docker push harbor.longguikeji.com/ark-releases/ark-sql-ldap:$(VERSION)


native-ldap-docker-build:
	cd ldap/native_backend && \
	docker build -t harbor.longguikeji.com/ark-releases/ark-native-ldap:$(VERSION) .

native-ldap-docker-push:
	docker push harbor.longguikeji.com/ark-releases/ark-native-ldap:$(VERSION)
