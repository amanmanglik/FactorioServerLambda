import json
import boto3

from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError



# API Gateway expects an Object with following potential attributes
# {
#     "cookies" : ["cookie1", "cookie2"],
#     "isBase64Encoded": true|false,
#     "statusCode": httpStatusCode,
#     "headers": { "headerName": "headerValue", ... },
#     "body": "Hello from Lambda!"
# }      



def triage_event(event, context):

    print(json.dumps(event))

    print("BODY DUMP PRETTY")
    print(json.dumps(json.loads(event["body"])))

    headers = event["headers"]
    
    sig = headers["x-signature-ed25519"]
    sig_timestamp = headers["x-signature-timestamp"]
    body = event["body"]
    body_json = json.loads(body)

    if body_json["type"] == 1:
        return handle_ping(sig, sig_timestamp, body)

    elif body_json["type"] == 2:
        return handle_app_command(sig, sig_timestamp, body, body_json)

    else:
        return send_raw_response(401, "Unknown Interaction Type")




def handle_ping(sig, sig_timestamp, body):
    print("Got PING Interaction")

    validation_result = validate_request(sig, sig_timestamp, body)
    if validation_result:
        body = { "type": 1}
        print("Sending PONG 200")
        return send_raw_response(200, json.dumps(body))
    else:
        print("Sending 401 Bad Signature")
        return send_raw_response(401, "Bad Request Signature")




def handle_app_command(sig, sig_timestamp, body, body_json):
    print("Got APPCOMMAND Interaction")
    validation_result = validate_request(sig, sig_timestamp, body)

    if not validation_result:
        return send_raw_response(401, "Bad Request Signature")

    else:
        command = body_json["data"]["options"][0]['name']

        # call async lambda
        print("Calling second lambda")

        payload = {
            'token': body_json['token'],
            'command' : command
        }


        client = boto3.client('lambda', region_name='eu-west-1')
        async_call_resp = client.invoke(
            FunctionName = "tarvis-factorio-server-manager-discord-core",
            InvocationType = "Event", 
            Payload = json.dumps(payload)
        )

        if (async_call_resp['StatusCode'] == 202):
            return send_discord_response(f"Looking into it ... {command}")

        else:
            return send_discord_response(f"Error while calling core lambda for command {command}")

        


def send_raw_response(httpStatus, body):
    response = {}
    response["statusCode"] = httpStatus
    response["body"] = body
    response["isBase64Encoded"] = False
    print("=== RESPONSE ===")
    print(response)
    return response



def send_discord_response(msg, type = 4):
    """send message back to discord as a bot response"""
    resp_body = {}
    resp_body["type"] = type
    resp_body["data"] = {
        "content" : msg
    }
    return send_raw_response(200, json.dumps(resp_body))




def validate_request(sig, sig_timestamp, body):
    """Validates the signature sent by discord in headers"""

    # Your public key can be found on your application in the Developer Portal
    PUBLIC_KEY = '96afe40bcb38da5ad1e52a0d8ab2235d6469362d4e70b94aa5c01a38b8d69b87'

    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))

    # signature = request.headers["x-signature-ed25519"]
    # timestamp = request.headers["x-signature-timestamp"]
    # body = request.data

    try:
        verify_key.verify(f'{sig_timestamp}{body}'.encode(), bytes.fromhex(sig))
        print("Signature Verification SUCCEEDED")
        return True
    except BadSignatureError:
        print("Signature Verification FAILED")
        return False
        
        
        
