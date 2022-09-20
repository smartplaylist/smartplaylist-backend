FROM node:17-alpine3.14

WORKDIR /app

ADD ./app ./

RUN yarn && \
    yarn build && \
    yarn global add serve

CMD [ "serve", "-s", "build" ]
