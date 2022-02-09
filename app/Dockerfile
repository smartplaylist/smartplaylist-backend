FROM python:3.10.2-alpine3.15

WORKDIR /usr/src/app

ENV SPOTIPY_CLIENT_ID=your_client_id_here
ENV SPOTIPY_CLIENT_SECRET=your_client_secret_here
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=example
ENV POSTGRES_DB=spotify
ENV POSTGRES_HOST=db

COPY ./Pipfile ./
RUN pip install --no-cache-dir pipenv && \
    pipenv install

COPY ./ .

CMD [ "pipenv", "run", "python", "./src/artists.py" ]

# for development, so you can sh into the container
# CMD [ "python", "./tools/sleep.py" ]
