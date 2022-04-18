import os, datetime, uuid, json
import boto3

from botocore.exceptions import ClientError
from aws_lambda_powertools.event_handler.api_gateway import APIGatewayRestResolver, CORSConfig, Response

if os.environ.get('AWS_SAM_LOCAL'):
    dynamodb = boto3.resource('dynamodb', endpoint_url='http://dynamodb-local:8000')
    table = dynamodb.Table("Tasks")
else:
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.getenv('TABLE_NAME'))

cors_config = CORSConfig(allow_origin="*", allow_headers=['*'], max_age=300)
app = APIGatewayRestResolver(cors=cors_config)

@app.get("/tasks")
def get_tasks():
    response = table.scan()
    tasks = [{"id": item['id'], "name": item['name'], "last_time": item['done_dates'][-1]} for item in response['Items']] 
    return {"tasks": tasks}

@app.post("/tasks")
def post_tasks():
    json_payload = app.current_event.json_body
    print(json_payload['name'])
    new_task = {
        'id': str(uuid.uuid4()),
        'name': json_payload['name'],
        'done_dates': [datetime.datetime.now().isoformat()]
    }
    response = table.put_item(
       Item={
            'id': new_task['id'],
            'name': new_task['name'],
            'done_dates': new_task['done_dates']
        },
    )
    return Response(
        status_code=201,
        content_type="application/json",
        body=json.dumps({"task": new_task}),
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
            "Access-Control-Allow-Methods": "*T",
            "Access-Control-Allow-Headers": "*",
        },
    )

@app.get("/tasks/<id>")
def get_task(id):
    try:
        response = table.get_item(Key={'id': id})
        print(response)
    except ClientError as e:
        return e.response['Error']
    
    if not 'Item' in response:
        return {"task": {}}

    return {'task': response['Item']}

@app.put("/tasks/<id>/done")
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

@app.delete("/tasks/<id>")
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

def lambda_handler(event, context):
    return app.resolve(event, context)