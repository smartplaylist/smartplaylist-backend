FROM python:3.8.12-alpine3.14

WORKDIR /usr/src/app

ENV SPOTIPY_CLIENT_ID=<your_apps_client_id>
ENV SPOTIPY_CLIENT_SECRET=<your_apps_client_secret>

COPY src/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src .

CMD [ "python", "./01-artists.py" ]