import discord
from discord.ext import commands
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

async def create_status_message(channel):
    global status_message, wins, losses
    status_message = await channel.send(f"**Štatistiky:**\nVýhry: {wins}\nPrehry: {losses}")

async def update_status(channel):
    global status_message, wins, losses
    content = f"**Štatistiky:**\nVýhry: {wins}\nPrehry: {losses}"
    try:
        await status_message.edit(content=content)
    except (discord.NotFound, AttributeError):
        await create_status_message(channel)

@bot.event
async def on_ready():
    global status_message, wins, losses
    print(f"Bot prihlásený ako {bot.user}")
    channel = bot.get_channel(channel_id)
    if channel is None:
        print("Neplatný kanál.")
        return

    bot_messages = []
    async for msg in channel.history(limit=100):
        if msg.author == bot.user:
            bot_messages.append(msg)

    # Vymažeme všetky staré správy bota okrem najnovšej
    for msg in bot_messages[1:]:
        try:
            await msg.delete()
        except:
            pass

    if bot_messages:
        status_message = bot_messages[0]
        # Pokúsime sa načítať hodnoty zo správy, ak chceš zachovať stav
        try:
            lines = status_message.content.split('\n')
            wins = int(lines[1].split(':')[1].strip())
            losses = int(lines[2].split(':')[1].strip())
        except:
            wins = 0
            losses = 0
            await status_message.edit(content=f"**Štatistiky:**\nVýhry: {wins}\nPrehry: {losses}")
    else:
        await create_status_message(channel)

@bot.event
async def on_message(message):
    global wins, losses, status_message

    if message.author == bot.user:
        return

    if message.channel.id != channel_id:
        return

    content = message.content.lower()

    if content in win_commands:
        wins += 1
    elif content in lose_commands:
        losses += 1
    elif content in winmin_commands:
        wins = max(0, wins - 1)
    elif content in losemin_commands:
        losses = max(0, losses - 1)
    else:
        # Nepríkazová správa - vymaž ju a skonči
        try:
            await message.delete()
        except:
            pass
        return

    # Ak správa je príkaz, tak vymaž pôvodnú správu používateľa
    try:
        await message.delete()
    except:
        pass

    # Aktualizuj štatistiky
    await update_status(message.channel)

bot.run(os.getenv("BOT_TOKEN"))

