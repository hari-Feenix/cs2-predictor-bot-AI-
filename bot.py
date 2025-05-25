import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv
from match_manager import get_upcoming_matches, resolve_matches
from prediction_manager import add_prediction
from leaderboard_manager import get_leaderboard

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    check_results.start()

@bot.command()
async def matches(ctx):
    matches = get_upcoming_matches()
    response = "**Upcoming Matches:**\n"
    for m in matches:
        response += f"**ID:** {m['match_id']} | {m['team1']} vs {m['team2']} | {m['time']}\n"
    await ctx.send(response)

@bot.command()
async def predict(ctx, match_id, team_name):
    msg = add_prediction(ctx.author.id, match_id, team_name)
    await ctx.send(msg)

@bot.command()
async def leaderboard(ctx):
    lb = await get_leaderboard(bot)
    await ctx.send(lb)

@tasks.loop(hours=1)
async def check_results():
    channel = discord.utils.get(bot.get_all_channels(), name="general")
    resolved_msgs = resolve_matches()
    if channel:
        for msg in resolved_msgs:
            await channel.send(msg)

bot.run(DISCORD_TOKEN)
