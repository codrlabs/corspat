FROM python:3.9.12-bullseye

RUN apt-get update -y && \
   apt-get install -y python3-pip python3-dev

# We copy just the requirements.txt first to leverage Docker cache
COPY /app/requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt

COPY ./app /app

# Run the application with Gunicorn
CMD [ "gunicorn", "-b", "0.0.0.0:5000", "app:app" ]