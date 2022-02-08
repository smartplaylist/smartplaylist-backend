FROM python:3.10.2-alpine3.15

WORKDIR /usr/src/app

ENV SPOTIPY_CLIENT_ID: <your_apps_client_id>
ENV SPOTIPY_CLIENT_SECRET: <your_apps_client_secret>

COPY app/requirements.txt ./
RUN pip install --no-cache-dir pipenv && \
    pipenv install


COPY ./app .

CMD [ "pipenv", "run", "python", "./artists.py" ]

# for development, so you can sh into the container
# CMD [ "python", "./tools/sleep.py" ]
