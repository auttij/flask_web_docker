# syntax=docker/dockerfile:1
FROM python:3.8.5-alpine3.12
WORKDIR /usr/app
RUN apk add gcc libc-dev linux-headers zlib-dev jpeg-dev libjpeg
COPY ./requirements.txt ./
RUN pip install -r requirements.txt
COPY ./app.py ./
COPY ./database ./database/
EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0"]