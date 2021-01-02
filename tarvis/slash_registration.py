import requests
import configparser


# Get the secrets
config = configparser.ConfigParser()
config.read(['config/secrets.prop', 'config/secrets-dev.prop'])
discord_app_id = config["DISCORD"]['app_id']
discord_guild_id = config["DISCORD"]['guild_id']
discord_bot_token = config["DISCORD"]['bot_token']




def register_command():
    url = f"https://discord.com/api/v8/applications/{discord_app_id}/guilds/{discord_guild_id}/commands"

    json = {
        "name": "tarvis",
        "description": "Factorio Server manager for Terronium's server",
        "options": [
            {
                "name": "status",
                "description": "Return the status of instance",
                "type": 1
            },
            {
                "name": "spinup",
                "description": "Spin Up the instance",
                "type": 1
            },
            {
                "name": "spindown",
                "description": "Spin Down the instance",
                "type": 1
            }
        ]
    }

    # For authorization, you can use either your bot token 
    headers = {
        "Authorization": f"Bot {discord_bot_token}"
    }

    # or a client credentials token for your app with the applications.commmands.update scope
    # headers = {
    #     "Authorization": "Bearer abcdefg"
    # }

    r = requests.post(url, headers=headers, json=json)

    print(r)



def get_guild_commands():

    url = f"https://discord.com/api/v8/applications/{discord_app_id}/guilds/{discord_guild_id}/commands"
    
    headers = {
        "Authorization": f"Bot {discord_bot_token}"
    }
    
    registered_commands = requests.get(url, headers=headers)
    print(registered_commands.json())





# EXEC
# register_command()

get_guild_commands()