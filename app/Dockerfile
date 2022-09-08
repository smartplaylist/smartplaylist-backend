FROM python:3.10.2-alpine3.15

WORKDIR /app

ENV POSTGRES_USER=${POSTGRES_USER:-postgres}
ENV POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-example}
ENV POSTGRES_DB=${POSTGRES_DB:-spotify}
ENV POSTGRES_HOST=${POSTGRES_HOST:-db}
ENV SPOTIFY_OAUTH_TOKEN=${SPOTIFY_OAUTH_TOKEN}
ENV SPOTIPY_CLIENT_ID=${SPOTIPY_CLIENT_ID}
ENV SPOTIPY_CLIENT_SECRET=${SPOTIPY_CLIENT_SECRET}
ENV SPOTIPY_REDIRECT_URI=${SPOTIPY_REDIRECT_URI:-http://127.0.0.1:8083/}

EXPOSE 8083

ADD ./src/ ./

RUN pip install --no-cache-dir pipenv && \
    pipenv install

CMD [ "pipenv", "run", "python", "./get_followed_artists.py" ]

# for development, so you can sh into the container
# CMD [ "python", "./tools/sleep.py" ]
