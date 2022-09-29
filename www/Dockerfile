FROM node:17-alpine3.14 AS builder
WORKDIR /app
COPY ./app ./
RUN yarn && \
    yarn build

FROM joseluisq/static-web-server:2.12
WORKDIR /app
COPY --from=builder /app/build ./
ENTRYPOINT ["/entrypoint.sh"]
CMD ["static-web-server"]
