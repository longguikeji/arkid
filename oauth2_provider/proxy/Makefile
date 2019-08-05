BINDIR = ./bin


all: clean oauth-proxy.darwin.amd64 oauth-proxy.linux.amd64
init:
	glide install

oauth-proxy.darwin.amd64: main.go
	env GOOS=darwin GOARCH=amd64 \
		go build -o $(BINDIR)/$@ $^

oauth-proxy.linux.amd64: main.go
	env GOOS=linux GOARCH=amd64 \
		go build -o $(BINDIR)/$@ $^


clean:
	rm -f $(BINDIR)/oauth-proxy.*

docker:
	make all
	docker build -t harbor.longguikeji.com/ark-core/oauth-proxy:$(TAG) ./
