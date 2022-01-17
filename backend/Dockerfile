FROM python:3.8

RUN pip install \
        boto3 \
        fastapi \
        uvicorn

COPY ./create-tasks-table.py ./
COPY ./app.py ./

CMD uvicorn --host 0.0.0.0 --port 8080 app:app --reload