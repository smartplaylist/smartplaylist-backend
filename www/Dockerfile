FROM node:17-alpine3.14

WORKDIR /app

ENV PORT=${APP_PORT:-3001}

ADD ./app/ ./

EXPOSE 3001

RUN yarn && \
    yarn build

# TODO: Tutaj trzeba dopisać coś, żeby w wersji produkcyjnej
# było serwowana zbudowana wersja z ./build
# a w wersji deweloperskiej z yarn start, żeby był hot reload

CMD [ "yarn", "start" ]
