import os, datetime, uuid

import boto3

from botocore.exceptions import ClientError
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

dynamodb = boto3.resource('dynamodb', endpoint_url=os.getenv('AWS_ENDPOINT_URL'))
table = dynamodb.Table(os.getenv('TABLE_NAME'))

app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Task(BaseModel):
    name: str

@app.get("/tasks")
def get_tasks():
    response = table.scan()
    tasks = [{"id": item['id'], "name": item['name'], "last_time": item['done_dates'][-1]} for item in response['Items']] 
    return {"tasks": tasks}

@app.post("/tasks")
def post_tasks(task: Task):
    new_task = {
        'id': str(uuid.uuid4()),
        'name': task.name,
        'done_dates': [datetime.datetime.now().isoformat()]
    }
    response = table.put_item(
       Item={
            'id': new_task['id'],
            'name': new_task['name'],
            'done_dates': new_task['done_dates']
        },
    )
    return {"task": new_task}

@app.get("/tasks/{id}")
def get_task(id):
    try:
        response = table.get_item(Key={'id': id})
        print(response)
    except ClientError as e:
        return e.response['Error']
    
    if not 'Item' in response:
        return {"task": {}}

    return {'task': response['Item']}

@app.put("/tasks/{id}/done")
def put_task(id):
    try:
        response = table.get_item(Key={'id': id})
        print(response)
    except ClientError as e:
        return e.response['Error']
    
    if not 'Item' in response:
        return {"task": {}}

    task = response['Item']
    task['done_dates'].append(datetime.datetime.now().isoformat())

    print(task)

    response = table.update_item(
        Key={
            'id': task['id'],
        },
        UpdateExpression="set done_dates=:d",
        ExpressionAttributeValues={
            ':d': task['done_dates']
        },
        ReturnValues="ALL_NEW"
    )
    task = response['Attributes']
    return {'task': task}

@app.delete("/tasks/{id}")
def delete_task(id):
    try:
        response = table.delete_item(
            Key={
                'id': id
            }
        )
    except ClientError as e:
        raise

    return {}