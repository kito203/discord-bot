import discord
from discord.ext import commands
import asyncio
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

channel_id = 1377662825580859492  # ← sem daj ID kanála

wins = 0
losses = 0
status_message = None

win_commands = ['!win', '!výhra', '!vyhra']
lose_commands = ['!lose', '!prehra']
winmin_commands = ['!winmin', '!výhramin', '!vyhramin']
losemin_commands = ['!losemin', '!prehramin']

async def update_status():
    global status_message
    content = f"**Výhry:** {wins}\n**Prehry:** {losses}"
    try:
        await status_message.edit(content=content)
    except:
        pass

@bot.event
async def on_ready():
    global status_message
    print(f"Bot prihlásený ako {bot.user}")
    channel = bot.get_channel(channel_id)
    if channel is None:
        print("Neplatný kanál.")
        return

    messages = [msg async for msg in channel.history(limit=100)]
    for msg in messages:
        if msg.author == bot.user:
            status_message = msg
        else:
            await msg.delete()

    if not status_message:
        status_message = await channel.send("**Výhry:** 0\n**Prehry:** 0")

@bot.event
async def on_message(message):
    global wins, losses, status_message

    if message.author == bot.user:
        return

    if message.channel.id != channel_id:
        return

    content = message.content.lower()
    await message.delete()

    if content in win_commands:
        wins += 1
    elif content in lose_commands:
        losses += 1
    elif content in winmin_commands:
        wins = max(0, wins - 1)
    elif content in losemin_commands:
        losses = max(0, losses - 1)
    else:
        return

    await update_status()

bot.run(os.getenv("BOT_TOKEN"))
