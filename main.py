import discord
import os
import requests
import json
from googleapiclient.discovery import build
import random

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

######## GOOGLE API #########
google_key = os.environ['GOOGLE_KEY']
search_engine_id = os.environ['SEARCH_ENGINE_ID']

############# DISCORD #############

client = discord.Client()

def getQuote():
    response = requests.get("https://animechan.vercel.app/api/random")
    json_data = json.loads(response.text)
    quote = [json_data["quote"], json_data["character"], json_data["anime"]]
    return quote

@client.event
async def on_ready():
    print("Successfully logged in as {0.user}".format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("$hello"):
        await message.channel.send("Kon'nichiwa")

    if message.content.startswith("$quote"):
        quoteData = getQuote()
        quote = "\"" + quoteData[0] + "\"" + " - " + quoteData[1] + " from " + quoteData[2]

        ### Picture ###
        search = quoteData[1] + " from " + quoteData[2]
        ran = random.randint(0, 9)
        resource = build("customsearch", "v1", developerKey = google_key).cse()
        result = resource.list(
            q=f"{search}", cx=search_engine_id, searchType="image", safe="active"
        ).execute()
 
        try:
            url = result["items"][ran]["link"]
            embed1 = discord.Embed(title=f"Image of {search}")
            embed1.set_image(url=url)
            await message.channel.send(embed=embed1)
        except:
            print(f"Image of {search} cannot be sent. (Explicit Content?)")

        await message.channel.send(quote)

    if message.content.startswith("$animerankings"):
        rankings = animeRankings(discord_token)
        toSend = 'Anime Rankings (full list at <https://myanimelist.net/topanime.php>):\n'

        for anime in rankings['data']:
            toSend += '\n#' + str(anime['ranking']['rank']) + ': ' + anime['node']['title']
        
        await message.channel.send(toSend)

    if message.content.startswith("$help"):
        toSend = """:robot: Current commands:
\$help -- Get a list of working commands
\$hello  -- Say hello to the bot! What will they reply?
\$quote -- Let the bot tell you a random anime quote!
\$animerankings -- List of current top 10 most popular anime"""
        await message.channel.send(toSend)

client.run(os.environ['TOKEN'])