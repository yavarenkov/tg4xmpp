FROM ubuntu:18.04
RUN mkdir /app
WORKDIR /app
RUN apt-get update && apt-get install --yes python3-pip

COPY . .
RUN pip3 install -e .

VOLUME /app/data
CMD PYTHONPATH=. tg4xmpp config_example
