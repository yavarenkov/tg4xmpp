FROM ubuntu:18.04
RUN mkdir /app
WORKDIR /app
RUN apt-get update && apt-get install --yes python3-pip

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY xmpp_tg/ xmpp_tg
COPY config_docker.py config.py
VOLUME /app/data

COPY start.py start.py
CMD PYTHONPATH=. python3 /app/start.py
