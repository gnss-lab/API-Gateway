FROM python:3.11

WORKDIR /usr/src/app/

COPY . /usr/src/app/

ENV PYTHONPATH=${PYTHONPATH}:${PWD} 
RUN pip3 install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-root --no-dev

ENV IP_SERVER=0.0.0.0 \
    PORT_SERVER=8000

VOLUME ["/usr/src/app/database"]

EXPOSE 20722

CMD ["python", "app.py"]