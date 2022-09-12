FROM python:3.10-slim-buster
WORKDIR /bot
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
RUN pip install --upgrade pip
COPY . .
RUN pip install -r requirements.txt
RUN python -m venv venv
RUN 
RUN echo successfuly installed deps
RUN pip freeze