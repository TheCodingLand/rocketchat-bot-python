FROM python:slim-stretch

RUN apt-get update && apt-get install -y \
        build-essential \
        wget \
        git \
        python3-dev

COPY ./requirements.txt /requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt


RUN mkdir -p /data/logs/
RUN mkdir -p /data/models/

WORKDIR /bot/

ADD ./dl_models.py /bot
RUN python dl_models.py

ADD . .

CMD python3 main.py
