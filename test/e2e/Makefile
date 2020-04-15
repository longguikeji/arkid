
image:
	docker build -t longguikeji/arkid-test:0.1.0 .

container:
	-docker rm -f arkid-test
	docker run -d \
		-v $(PWD)/src:/workspace/src \
		-v /var/run/docker.sock:/var/run/docker.sock \
		--name arkid-test \
		longguikeji/arkid-test:0.1.0 tail -f /etc/hosts

# test:
# 	-docker rm -f arkid-test
# 	docker run -d -it\
# 		-e CI=true \
# 		-v $(PWD)/src:/workspace/src \
# 		-v /var/run/docker.sock:/var/run/docker.sock \
# 		--name arkid-test \
# 		longguikeji/arkid-test:0.1.0
