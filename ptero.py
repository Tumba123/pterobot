import discord
from discord.ext import commands
from pterodactyl import PterodactylClient

bot = commands.Bot(command_prefix='!')
pterodactyl_client = PterodactylClient('https://your.pterodactyl.panel', 'your api key')

@bot.command()
async def listservers(ctx):
    servers = pterodactyl_client.get_servers()
    response = "\n".join([server.name for server in servers])
    await ctx.send(response)

bot.run('your bot token')