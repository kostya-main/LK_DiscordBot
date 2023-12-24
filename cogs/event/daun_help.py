import discord
from discord.ext import commands


class Daun_help(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot == False and not message.guild:
            await message.reply('Я не умею общаться с людьми в свободной форме. Все мои возможности описаны в /help')

async def setup(client):
    await client.add_cog(Daun_help(client))