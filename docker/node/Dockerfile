FROM node:22

Label maintainer="bgm"

WORKDIR app

COPY config/node/frontend/package.json .
RUN npm install

COPY config/node/frontend .

ENV CI=false

CMD ["npm", "start"]