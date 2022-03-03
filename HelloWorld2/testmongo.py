import os
import discord
from discord.ext import commands
import pymongo
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('MONGOTEST')
client = discord.Client()
cluster = MongoClient("mongodb+srv://dmerryman:Chibi!23@cluster0.mt9tp.mongodb.net/test")
db = cluster["UserData"]
collection = db["UserData"]

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.event
async def on_message(ctx):
    # infinite loop prevention
    if ctx.author == bot.user:
        return
    if (str(ctx[0]) != '!'):
        buzzwords = ["python", "discord", "lego", "code"]
        words = str(ctx.content.lower()).split()
        for word in words:
            if word in buzzwords:
                await buzzwordSpotted(ctx, word)
    else:
        await bot.process_commands(ctx) # commands won't process without this, because I overrode on_message
    
                
async def buzzwordSpotted(ctx, word):
    myquery = { "discord_id": ctx.author.id, "word": word }
    if (collection.count_documents(myquery) == 0):
        post = {"discord_id": ctx.author.id, "word": word, "score": 1}
        collection.insert_one(post) 
        await ctx.channel.send(word + " added to database for " + str(ctx.author))
    else:
        query = {"discord_id": ctx.author.id, "word": word}
        user = collection.find(query)
        for result in user:
            score = result["score"]
        score = score + 1;
        collection.update_one({"discord_id":ctx.author.id, "word": word}, {"$set":{"score":score}})
        await ctx.channel.send(word + " score is " + str(score) + " for " + str(ctx.author))
            
@bot.command(name='reset', help='resets your score for a word')
async def resetscore(ctx, word):
    buzzwords = ["python", "discord", "lego", "code"]
    if word not in buzzwords:
        await ctx.channel.send(word + " is not one of the buzzwords.")
        return
    myquery = { "discord_id": ctx.author.id, "word": word}
    if (collection.count_documents(myquery) == 0):
        post = {"discord_id": ctx.author.id, "word": word, "score": 0}
        collection.insert_one(post)
        await ctx.channel.send(str(ctx.author) + " didn't have a score for " + word + " but it's zero now.")
    else:
        collection.update_one({"discord_id":ctx.author.id, "word": word}, {"$set": {"score":0}})
        await ctx.channel.send(word + " score set to zero for " + str(ctx.author))
        
#client.run(TOKEN)
bot.run(TOKEN)
