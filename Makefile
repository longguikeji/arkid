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
	python manage.py migrate && python manage.py test siteapi.v1.tests infrastructure.tests.test_file infrastructure.tests.test_sms --settings=oneid.settings_test
	# 需单独采用mysql对接测试, 并将 test_user.SKIP_GET_USER_LIST__CUSTOM 置为 False 后执行此命令
# 	python manage.py test siteapi.v1.tests.test_user.UserTestCase.test_get_user_list__custom --settings=settings_local

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


docker-compose:
	INSTANCE_ID=arkid WORKSPACE=/Users/yanghan/volume/arkid SQL_PWD=root LDAP_PASSWORD=root docker-compose up -d

dataset:
	python manage.py migrate && python test/utils/test_data_manager.py -l

sqlset:
	python test/utils/test_data_manager.py -d

run:
	python manage.py runserver 0:8000