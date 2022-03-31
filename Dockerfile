FROM python:3.9.12-bullseye

MAINTAINER inidal "hello@inidal.dev"

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev

# We copy just the requirements.txt first to leverage Docker cache
COPY /app/requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt

COPY ./app /app

ENTRYPOINT [ "python3" ]

CMD [ "app.py" ]

RUN flask run --host=0.0.0.0
