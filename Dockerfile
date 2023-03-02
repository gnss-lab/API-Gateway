FROM python:3.11

ARG APP_VERSION

WORKDIR /usr/src/app/

COPY . /usr/src/app/

ENV PYTHONPATH=${PYTHONPATH}:${PWD} 
RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-root --no-dev

#ENV FASTAPI_IP=0.0.0.0 \
#    FASTAPI_PORT=7000 \
#    LOGSTASH_HOST=0.0.0.0 \
#    LOGSTASH_PORT=50000

VOLUME ["/usr/src/app/database"]

EXPOSE 7200

LABEL version=${APP_VERSION}

CMD ["python", "app.py"]