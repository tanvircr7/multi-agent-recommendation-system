
import json
import boto3
import pandas as pd
from io import StringIO

S3_BUCKET = "ADD-YOUR-BUCKET-NAME"
S3_KEY = "restaurant.csv"


def lambda_handler(event, context):
    print("Lambda function started")

    try:
        agent = event.get('agent', '')
        actionGroup = event.get('actionGroup', '')
        function = event.get('function', '')
        parameters = event.get('parameters', [])

        param_dict = {param['name']: param['value'] for param in parameters}

        city = param_dict.get('city', None)
        fine_dine = param_dict.get('fine_dine', None)

        print(city, fine_dine)

        s3_client = boto3.client('s3')
        response = s3_client.get_object(Bucket=S3_BUCKET, Key=S3_KEY)

        csv_data = response['Body'].read().decode('utf-8')
        df = pd.read_csv(StringIO(csv_data))

        df['Fine Dining'] = df['Fine Dining'].str.strip().str.lower()
        df['City'] = df['City'].str.strip().str.lower()

        if city:
            df = df[df['City'] == city.strip().lower()]
        if fine_dine:
            df = df[df['Fine Dining'] == fine_dine.strip().lower()]

        filtered_data = json.dumps(df.to_dict(orient='records'),default = str)

        responseBody = {
            "TEXT": {
                "body": filtered_data,
            }
        }

        action_response = {
            'actionGroup':actionGroup,
            'function': function,
            'functionResponse': {
                'responseBody': responseBody
            }
        }


        dummy_function_response = {'response':action_response, 'messageVersion': event['messageVersion']}

        return dummy_function_response

    except Exception as e:
        print(e)
        return {
            'statusCode': 400,
            'body': json.dumps(f'Error processing the request, error: {e}]')
        }
