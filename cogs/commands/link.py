import discord
from discord.ext import commands
from discord import app_commands

from main import config

class Link(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="links", description="Ссылки на скачку игрового клиента")
    @app_commands.default_permissions(permissions=0)
    async def links(self, interaction: discord.Integration):
        embedVar = discord.Embed(title="Лаунчер", description="Выберите свою операционную систему", color=config.bot.embedColor)
        embedVar.add_field(name="Windows",
                       value=f"[Скачать]({config.web.url_launcher_exe})",
                       inline=True)
        embedVar.add_field(name="Linux/MacOS",
                       value=f"[Скачать]({config.web.url_launcher_jar})",
                       inline=True)
        await interaction.response.send_message(embed=embedVar)

async def setup(client):
    await client.add_cog(Link(client))