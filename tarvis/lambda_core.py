from tarvis import aws_link
import requests
import configparser


def process_command(event, context):

    print("EVENT DUMP")
    print(event)
    token = event['token']
    command = event['command']

    handle_app_command(command, token)



def handle_app_command(command, token):
    print(f"Received Command - {command}")
    msg = "Blackhole!"
    try:   
        if command == "status":
            msg = aws_link.status_check()

        elif command == "spinup":
            msg = aws_link.spin_up_instance()

        elif command == "spindown":
            msg = aws_link.spin_down_instance()

        followup_edit_msg(msg, token)

    except Exception as e:
        print(e)
        followup_edit_msg(f"Something went wrong - {e}", token)

    


def followup_edit_msg(msg, token):

    config = configparser.ConfigParser()
    config.read('config/secrets.prop')
    discord_app_id = config["DISCORD"]['app_id']

    url = f"https://discord.com/api/v8/webhooks/{discord_app_id}/{token}/messages/@original"
    print(f"URL -> {url}")

    json = {
        "content": msg
    }

    print(json)
    result = requests.patch(url, json=json)
    print("discord call complete")
    print(result)

        
