FROM python:3.10.2-alpine3.15

WORKDIR /usr/src/app

ENV SPOTIPY_CLIENT_ID=4ec802ba01c14398b824d7f6b491bc0b
ENV SPOTIPY_CLIENT_SECRET=a3340648be624110be0a8f6ffc027297

COPY src/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY ./src .

CMD [ "python", "./sleep.py" ]
