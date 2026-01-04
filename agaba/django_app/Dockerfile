# pull official base image
# FROM python:3.11.8-slim-bookworm
FROM python:3.11.9-alpine

# set work directory
WORKDIR /usr/src/django_app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN chmod +x /usr/src/django_app/entrypoint.sh
ENTRYPOINT ["/usr/src/django_app/entrypoint.sh"]
