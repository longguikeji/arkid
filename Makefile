.PHONY: \
	ci \
	lint test build \
	all requirements docker docker-build docker-push \
	sql-ldap-docker sql-ldap-docker-build sql-ldap-docker-push \
	native-ldap-docker native-ldap-docker-build native-ldap-docker-push


VERSION ?= 1.0.`date +%Y%m%d`
BASE_COMMIT_ID ?= ""

ci:
	docker build --build-arg base_commit_id="origin/master" \
	-t harbor.longguikeji.com/ark-releases/arkid:$(VERSION) .

test:
	python manage.py migrate && python manage.py test siteapi.v1.tests --settings=oneid.settings_test

lint: 
	@if [ ${BASE_COMMIT_ID}x != ""x ]; \
	then \
		git reset ${BASE_COMMIT_ID}; \
		git add .; \
	fi

	.git/hooks/pre-commit

requirements:
	pipenv run pipenv_to_requirements -f

build: docker-dev-build

docker-dev: docker-dev-build docker-dev-push

docker-dev-build:
	docker build -t harbor.longguikeji.com/ark-releases/arkid:$(VERSION) .

docker-dev-push:
	docker push harbor.longguikeji.com/ark-releases/arkid:$(VERSION)

docker-prod: docker-prod-build docker-prod-push

docker-prod-build:
	docker build -t longguikeji/arkid:$(VERSION) .

docker-prod-push:
	docker push longguikeji/arkid:$(VERSION)

sql-ldap-docker: sql-ldap-docker-build sql-ldap-docker-push

sql-ldap-docker-build:
	cd ldap/sql_backend/docker && \
	docker build -t longguikeji/ark-sql-ldap:$(VERSION) .

sql-ldap-docker-push:
	docker push longguikeji/ark-sql-ldap:$(VERSION)

native-ldap-docker: native-ldap-docker-build native-ldap-docker-build

native-ldap-docker-build:
	cd ldap/native_backend && \
	docker build -t longguikeji/ark-native-ldap:$(VERSION) .

native-ldap-docker-push:
	docker push longguikeji/ark-native-ldap:$(VERSION)
