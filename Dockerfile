FROM alpine:3.17.2

ENV PYTHONUNBUFFERED=1
RUN pip3 install
RUN pip install tabcmd

COPY entrypoint.sh /entrypoint.sh
COPY workbooks/yelp_analyses.twb yelp_analyses.twb

ENTRYPOINT ["/entrypoint.sh"]
