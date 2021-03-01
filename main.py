import os
import discord
import random
import asyncio
import json
# import traceback
from dotenv import load_dotenv
from discord.ext import commands

# Load bot token
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


def create_old_file(filename):
    '''
    Renames filename to filename_old. Appends numbers if filename_old exists
    :param filename: Name of the file (without extension) to process
    :return: None
    '''
    newname = filename+"_old.json"
    num = 1
    while os.path.exists(newname):
        newname = filename+"_old"+str(num)+".json"
        num += 1
    os.rename(filename+".json", newname)



try:
    opt_out_file = open("opt_out.json", "r")
    opt_out_list = json.load(opt_out_file)
    opt_out_file.close()
except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
    # print(e)
    if isinstance(e, FileNotFoundError):
        print("File opt_out.json not found, creating it...")
    elif isinstance(e, json.decoder.JSONDecodeError):
        print("WARNING: Json file corrupted, re-creating it...")
        opt_out_file.close()
        create_old_file("opt_out")

    opt_out_file = open("opt_out.json", "w")
    json.dump([], opt_out_file)
    opt_out_file.close()
    opt_out_list = []

# client = discord.Client()
bot = commands.Bot(command_prefix='!')
cooldown = []
globalCooldown = False
USE_GLOBAL_COOLDOWN = True
COOLDOWN_TIME = 3

@bot.event
async def on_ready():
    '''
    Simply displays a connection message.
    :return: None
    '''
    print(f'{bot.user} has connected to Discord!')

@bot.event
async def on_message(message):
    '''
    Does the role rave shenanigans.
    :param message: message
    :return: None
    '''

    global cooldown
    global globalCooldown
    global opt_out
    member = message.author
    server = member.guild
    isCommand = False           # Set to true if message is a command
    isCooldownActive = False    # Set to true if the cooldown is active

    # Don't process the bot's own messages
    if member == bot.user:
        return

    # Check if the message is a command
    try:
        if message.content[0] == '!':
            isCommand = True
    except:
        pass

    # Check if the cooldown is active
    if USE_GLOBAL_COOLDOWN:
        isCooldownActive = globalCooldown
    else:
        if member.id in cooldown:
            isCooldownActive = True

    # Process color change
    if not isCommand and not isCooldownActive and not member.id in opt_out_list:

        if USE_GLOBAL_COOLDOWN:
            globalCooldown = True
        else:
            cooldown.append(member.id)

        color_r = int(random.random()*256)
        color_g = int(random.random()*256)
        color_b = int(random.random()*256)

        color = color_r*65536+color_g*256+color_b

        if not discord.utils.get(server.roles, name=member.name):
            await server.create_role(name=member.name, colour=discord.Colour(color))
            role = discord.utils.get(server.roles, name=member.name)
        else:
            role = discord.utils.get(server.roles, name=member.name)
            await role.edit(colour=discord.Colour(color))

        await member.add_roles(role)
        
        await asyncio.sleep(COOLDOWN_TIME)

        if USE_GLOBAL_COOLDOWN:
            globalCooldown = False
        else:
            cooldown.remove(member.id)

    await bot.process_commands(message)

@bot.command()
async def opt_out(ctx):
    '''
    Allows a user to opt out of the rolerave.
    :param ctx: ctx
    :return: None
    '''
    if not ctx.author.id in opt_out_list:
        opt_out_list.append(ctx.author.id)
        await ctx.send(f"Added {ctx.author.name} to the opt-out list!")
    else:
        opt_out_list.remove(ctx.author.id)
        await ctx.send(f"Removed {ctx.author.name} from the opt-out list!")

    opt_out_file = open("opt_out.json", "w")
    json.dump(opt_out_list, opt_out_file)
    opt_out_file.close()

@bot.command()
async def opt_in(ctx):
    '''
    Intended to alias opt_out. There might be a better way to do this?
    :param ctx: ctx
    :return: None
    '''
    await opt_out(ctx)

# print(TOKEN)
bot.run(TOKEN)
