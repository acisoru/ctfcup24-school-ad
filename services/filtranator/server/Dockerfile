FROM ubuntu:24.04

RUN apt-get update
RUN apt-get install -y python3 pip libpq-dev iproute2 netcat-traditional
RUN useradd -m ctf
RUN mkdir /app
WORKDIR /app

COPY ./ /app
RUN chmod +x ./server.py
RUN chmod +x ./filterer/filterer
RUN pip3 install -r ./requirements.txt --break-system-packages
RUN chown -R ctf:ctf /app/images
RUN chown -R ctf:ctf /app
USER ctf

EXPOSE 6969
CMD ./server.py
