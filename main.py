import discord
import os
import requests
import json

############# MYANIMELIST API #############
CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']

# 4. Test the API by requesting your profile information
def print_user_info(access_token: str):
    url = 'https://api.myanimelist.net/v2/users/@me'
    response = requests.get(url, headers = {
        'Authorization': f'Bearer {access_token}'
        })
    
    response.raise_for_status()
    user = response.json()
    response.close()

    print(f"\n>>> Greetings {user['name']}! <<<")
 
discord_token = os.environ['DISCORD_TOKEN']
print_user_info(discord_token)

def animeRankings(access_token: str):
    url = 'https://api.myanimelist.net/v2/anime/ranking'
    response = requests.get(url, headers = {
        'Authorization': f'Bearer {access_token}'
        })
    
    response.raise_for_status()
    rankingsData = response.json()
    response.close()

    return rankingsData

############# DISCORD #############

client = discord.Client()

def getQuote():
    response = requests.get("https://animechan.vercel.app/api/random")
    json_data = json.loads(response.text)
    quote = "\"" + json_data["quote"] + "\"" + " - " + json_data["character"] + " from " + json_data["anime"]
    return quote

@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("$hello"):
        await message.channel.send("Kon'nichiwa")

    if message.content.startswith("$quote"):
        quote = getQuote()
        await message.channel.send(quote)

    if message.content.startswith("$animerankings"):
        rankings = animeRankings(discord_token)
        toSend = 'Anime Rankings (full list at <https://myanimelist.net/topanime.php>):\n'

        for anime in rankings['data']:
            toSend += '\n#' + str(anime['ranking']['rank']) + ': ' + anime['node']['title']
        
        await message.channel.send(toSend)

client.run(os.environ['TOKEN'])