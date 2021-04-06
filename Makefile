build:
	docker build -t harbor.longguikeji.com/ark-releases/arkid:v2dev .
push:
	docker push harbor.longguikeji.com/ark-releases/arkid:v2dev