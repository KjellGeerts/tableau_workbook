FROM alpine:3.17.2

ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install --no-cache --upgrade pip setuptools
RUN pip install tabcmd

COPY entrypoint.sh /entrypoint.sh
COPY workbooks/yelp_analyses.twb /yelp_analyses.twb

ENTRYPOINT ["/entrypoint.sh"]
