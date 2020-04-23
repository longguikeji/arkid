# chromium
FROM rastasheep/alpine-node-chromium:10-alpine

# docker client
RUN apk update && apk add --no-cache docker-cli

# src
WORKDIR /workspace
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ADD *.js *.json ./
RUN npm install
RUN npm install --only=dev
ADD . .

CMD npm run test
