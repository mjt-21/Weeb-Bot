import discord
import os
import requests
import json
from googleapiclient.discovery import build
import random
from discord.ext import commands

############# MYANIMELIST API #############
CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']
 
######### DISCORD API TOKEN #########

discord_token = os.environ['DISCORD_TOKEN']

######## GOOGLE API #########
google_key = os.environ['GOOGLE_KEY']
search_engine_id = os.environ['SEARCH_ENGINE_ID']

##### FUNCTIONS #####

# Test the MAL API by requesting your profile information
def print_user_info(access_token: str):
    url = 'https://api.myanimelist.net/v2/users/@me'
    response = requests.get(url, headers = {
        'Authorization': f'Bearer {access_token}'
        })
    
    response.raise_for_status()
    user = response.json()
    response.close()

    print(f"\n>>> Greetings {user['name']}! <<<")

def getAnimeRankings(access_token: str):
    url = 'https://api.myanimelist.net/v2/anime/ranking'
    response = requests.get(url, headers = {
        'Authorization': f'Bearer {access_token}'
        })
    
    response.raise_for_status()
    rankingsData = response.json()
    response.close()

    return rankingsData

def getQuote():
    response = requests.get("https://animechan.vercel.app/api/random")
    json_data = json.loads(response.text)
    quote = [json_data["quote"], json_data["character"], json_data["anime"]]
    return quote

############# DISCORD COMMANDS #############

# Test access to MAL
print_user_info(discord_token)

# Set up discord commands (bot)
bot = commands.Bot(command_prefix='$')
bot.remove_command('help') # Remove default 'remove' command

@bot.event
async def on_command_error(ctx, error): # To handle errors
    if isinstance(error, commands.CommandNotFound):
        return # Displays no errors (returns); use "raise error" in code to raise certain errors

@bot.event
async def on_ready(): # Test access to Discord
    print("Successfully logged in as {0.user}".format(bot))

@bot.command()
async def hello(ctx):
    await ctx.send(f"Kon'nichiwa {ctx.message.author.mention}!")

@bot.command()
async def quote(ctx):
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
        await ctx.send(embed=embed1)
    except:
        print(f"Image of {search} cannot be sent. (Explicit Content?)")

    await ctx.send(quote)    

@bot.command()
async def animerankings(ctx):
    rankings = getAnimeRankings(discord_token)
    toSend = 'Anime Rankings (full list at <https://myanimelist.net/topanime.php>):\n'

    for anime in rankings['data']:
        toSend += '\n#' + str(anime['ranking']['rank']) + ': ' + anime['node']['title']

    await ctx.send(toSend)

@bot.command()
async def help(ctx):
    toSend = """:robot: Current commands:
\$help -- Get a list of working commands
\$hello  -- Say hello to the bot! What will they reply?
\$quote -- Let the bot tell you a random anime quote!
\$animerankings -- List of current top 10 most popular anime
\$pic [search term(s)] -- Search for pictures from online"""
    await ctx.send(toSend)

@bot.command()
async def pic(ctx, *args):
    search = ' '.join(args)

    ran = random.randint(0, 9)
    resource = build("customsearch", "v1", developerKey = google_key).cse()
    result = resource.list(
        q=f"{search}", cx=search_engine_id, searchType="image", safe="active"
    ).execute()

    try:
        url = result["items"][ran]["link"]
        embed1 = discord.Embed(title=f"Image of {search}")
        embed1.set_image(url=url)
        await ctx.send(embed=embed1)
    except:
        await ctx.send(f":exclamation: WARNING FOR {ctx.message.author.mention} :exclamation:\n\nYou are suspected for breaking server rules. Staff have been notified and will consider your case shortly.")
        print(f"\n----- ALERT! -----\nUser: {ctx.message.author}\nPhoto search request: {search}\n")

bot.run(os.environ['TOKEN'])