FROM python:3.7
RUN apt-get update && apt-get install

RUN python -m pip install --upgrade pip

ENV PYTHONUNBUFFERED=1
RUN mkdir /NewsArticle
WORKDIR /NewsArticle/
COPY . /requirements.txt/
RUN pip install -r requirements.txt
COPY . /NewsArticle/