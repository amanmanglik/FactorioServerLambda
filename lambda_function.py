import json

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




def lambda_handler(event, context):

    print("EVENT DUMP")
    print(type(event))
    print(repr(event))

    headers = event["headers"]
    print("HEADER DUMP")
    print(type(headers))
    print(repr(headers))


    sig = headers["x-signature-ed25519"]
    sig_timestamp = headers["x-signature-timestamp"]

    body = event["body"]
    body_json = json.loads(body)

    response = {}
    response["statusCode"] = 200
    response["body"] = json.dumps(json.loads('{"type": 1}'))
    response["isBase64Encoded"] = False


    if body_json["type"] == 1:
        print("detected type 1")
        validation_result = validate_request(sig, sig_timestamp, body)
        if validation_result:
            print("validation success")

            print(repr(response))
            return response
        else:
            print("validation failedd")
            response["statusCode"] = 401
            response["body"] = "Bad Request Signature"
            print(repr(response))
            return response
    else:
        print("didnt detect type 1")
        return "didnt detect type"





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
        return True
    except BadSignatureError:
        return False
        # abort(401, 'invalid request signature')
        
        
