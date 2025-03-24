import json
import boto3

def lambda_handler(event, context):
    data = event['body']
    client = boto3.client('bedrock-agent-runtime')

    data_dict = json.loads(data)
    input_text = data_dict['text']
    session_id = data_dict['sessionId']

    try:
        response = client.invoke_agent(
            agentId='',
            agentAliasId='',
            sessionId=session_id,
            inputText=input_text,
            endSession = False
        )

        reponse_text = ""

        for event in response.get('completion', []):
            if "chunk" in event and "bytes" in event["chunk"]:
                reponse_text += event['chunk']['bytes'].decode('utf8')
        print(reponse_text)


        return {
            'statusCode': 200,
            'body': json.dumps({
                "response":reponse_text
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
