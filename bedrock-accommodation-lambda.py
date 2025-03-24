
import json
import boto3
import pandas as pd
import json
from io import StringIO

S3_BUCKET = 'ADD-YOUR-BUCKET-NAME'
HOTEL_CSV_KEY = 'hotel.csv'
AIRBNB_CSV_KEY ='airbnb.csv'

def lambda_handler(event, context):
    print('Lambda function started')
    try:
        agent = event.get('agent', '')
        actionGroup = event.get('actionGroup', '')
        function = event.get('function', '')

        parameters = event.get('parameters', [])

        param_dict = {param['name']: param['value'] for param in parameters}

        if function == "list-hotels":
            location = param_dict.get('location', None)
            print(location)
            s3_key = HOTEL_CSV_KEY
            filter_column = 'Location'
            filters = {filter_column: location}

        elif function == "list-airbnbs":
            location = param_dict.get('location', None)
            pets = param_dict.get('pets', None)
            pool = param_dict.get('pool', None)
            sauna = param_dict.get('sauna', None)
            print(location,pets,pool,sauna)
            s3_key = AIRBNB_CSV_KEY
            filters = {'Location':location, 'Pets':pets, 'Pool':pool, 'Sauna':sauna}
        else:
            return {"error": "Invalid function name."}


        s3_client = boto3.client('s3')
        response = s3_client.get_object(Bucket=S3_BUCKET, Key=s3_key)

        csv_data = response['Body'].read().decode('utf-8')

        df = pd.read_csv(StringIO(csv_data))

        df = df.applymap(lambda x: x.strip().lower() if isinstance(x, str) else x)

        for col, val in filters.items():
            if val is not None:
                df = df[df[col].astype(str).str.lower() == str(val).lower()]

        filtered_data = json.dumps(df.to_dict(orient='records'), default = str)

        print(filtered_data)


        responseBody =  {
            "TEXT": {
                "body": filtered_data,
            }
        }

        action_response = {
            'agent':agent,
            'actionGroup': actionGroup,
            'function': function,
            'functionResponse': {
                'responseBody': responseBody
            }

        }

        dummy_function_response = {'response': action_response, 'messageVersion': event['messageVersion']}
        print("Response: {}".format(dummy_function_response))

        return dummy_function_response

    except Exception as e:
        print("Error: {}".format(e))
        return {"error": str(e)}
