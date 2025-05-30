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

lock = asyncio.Lock()

def create_embed(wins, losses):
    total = wins + losses
    winrate = (wins / total * 100) if total > 0 else 0.0
    embed = discord.Embed(title="📊 Štatistiky 📊", color=0x00ff00)
    embed.add_field(name="✅ Výhry", value=str(wins), inline=True)
    embed.add_field(name="❌ Prehry", value=str(losses), inline=True)
    embed.add_field(name="📈 Winrate", value=f"{winrate:.2f} %", inline=False)
    return embed

async def clear_channel(channel):
    async for msg in channel.history(limit=100):
        try:
            await msg.delete()
        except:
            pass

async def create_status_message(channel):
    global status_message, wins, losses
    embed = create_embed(wins, losses)
    status_message = await channel.send(embed=embed)

async def update_status():
    global status_message, wins, losses
    embed = create_embed(wins, losses)
    try:
        await status_message.edit(embed=embed)
    except (discord.NotFound, AttributeError):
        # Ak správa zmizla, vytvoríme novú
        channel = bot.get_channel(channel_id)
        if channel:
            await clear_channel(channel)
            await create_status_message(channel)

@bot.event
async def on_ready():
    global status_message, wins, losses
    print(f"Bot prihlásený ako {bot.user}")
    channel = bot.get_channel(channel_id)
    if channel is None:
        print("Neplatný kanál.")
        return

    async with lock:
        await clear_channel(channel)
        await create_status_message(channel)

@bot.event
async def on_message(message):
    global wins, losses, status_message

    if message.author == bot.user:
        return

    if message.channel.id != channel_id:
        return

    content = message.content.lower()

    async with lock:
        if content in win_commands:
            wins += 1
        elif content in lose_commands:
            losses += 1
        elif content in winmin_commands:
            wins = max(0, wins - 1)
        elif content in losemin_commands:
            losses = max(0, losses - 1)
        else:
            try:
                await message.delete()
            except:
                pass
            return

        try:
            await message.delete()
        except:
            pass

        await update_status()

bot.run(os.getenv("BOT_TOKEN"))
