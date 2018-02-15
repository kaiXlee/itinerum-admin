FROM alpine:3.7
MAINTAINER Kyle Fitzsimmons "kfitzsimmons@gmail.com"
RUN apk add gcc musl-dev python python-dev py-pip postgresql-dev --no-cache
WORKDIR /app
ADD requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY . /app
ENTRYPOINT ["python", "wsgi_admin.py"]
