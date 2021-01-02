import boto3
import configparser
import time





def get_client():

    dev_mode = False

    if dev_mode:

        config = configparser.ConfigParser()
        config.read('config/secrets.prop')
        aws_access_key = config["AWS"]["access-key"]
        aws_secret_key = config["AWS"]["secret-key"]

        return boto3.client('ec2', region_name='eu-west-1', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)
    else:
        return boto3.client('ec2', region_name='eu-west-1')




def spin_up_instance():

    client = get_client()
    instance_id, state = get_factorio_instance()

    if state == "stopped":
        resp = client.start_instances(InstanceIds=[instance_id])
        newstate = resp["StartingInstances"][0]["CurrentState"]["Name"]

        if newstate not in ['pending', 'running']:
            return f"Tried to spin up Instance but the state is - {newstate}"
        
        else:
            ip = get_ip()

            return f"Spinned Up Instance. IP - {ip}"
    else:
        return f"Instance NOT stopped. Current state - {state}"
        


def get_ip():
    client = get_client()
    instance_id, state = get_factorio_instance()

    public_ip = "UNKNOWN"

    retryCount = 0
    while retryCount < 12:
        desc_response = client.describe_instances(
            Filters=[
                {
                    'Name': 'instance-id',
                    'Values': [
                        instance_id
                    ]
                }
            ]
        )

        if desc_response['ResponseMetadata']['HTTPStatusCode'] == 200:
            public_ip = desc_response['Reservations'][0]['Instances'][0].get('PublicIpAddress')

            if public_ip == None:
                print(f"IP Not allocated yet. Retry - {retryCount}")
                retryCount += 1
                time.sleep(2)
                continue
            else:
                print(f"IP found - {public_ip}")
                break
        else:
            return "Couldnt retrieve IP"

    return str(public_ip)




def spin_down_instance():
    client = get_client()
    instance_id, state = get_factorio_instance()

    if state == "running":

        resp = client.stop_instances(InstanceIds=[instance_id])
        newstate = resp["StoppingInstances"][0]["CurrentState"]["Name"]

        if newstate not in ['stopping', 'stopped']:
            return f"Tried to spin down Instance but the state is - {newstate}"
        
        else:
            return "Instance is stopping."



def status_check():
    client = get_client()
    instance_id, state = get_factorio_instance()

    ipstr = ""
    if state == "running":
        ipstr = "IP - " + get_ip()

    return f"Instance is in state - {state}. {ipstr}"



def get_factorio_instance():

    client = get_client()
    response = client.describe_instances(
        Filters=[
            {
                'Name': 'tag:Name',
                'Values': [
                    'factorio'
                ]
            }
        ]
    )

    print(response)
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        instance_id = response['Reservations'][0]['Instances'][0]['InstanceId']
        instance_state = response['Reservations'][0]['Instances'][0]['State']['Name']
        return instance_id, instance_state

    else:
        return None, None
