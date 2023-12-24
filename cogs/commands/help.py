import discord
from discord.ext import commands
from discord import app_commands

from main import config

class Help(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="help", description="Помощь по командам")
    async def help(self, interaction: discord.Integration):
        embedVar = discord.Embed(title="Справка", description="*Полный список команд*", color=config.bot.embedColor)
        embedVar.add_field(name=f"{config.bot.prefix}reg", value=f"Регистрация: {config.bot.prefix}reg", inline=False)
        embedVar.add_field(name=f"{config.bot.prefix}name", value=f"Сменить псевдоним: {config.bot.prefix}name [новый псевдоним]", inline=False)
        embedVar.add_field(name=f"{config.bot.prefix}password", value=f"Сменить пароль: {config.bot.prefix}password [новый пароль]", inline=False)
        embedVar.add_field(name=f"{config.bot.prefix}skin", value=f"Поставить скин: {config.bot.prefix}skin + [файл скина]", inline=False)
        embedVar.add_field(name=f"{config.bot.prefix}cape", value=f"Поставить плащ: {config.bot.prefix}cape + [файл плаща]", inline=False)
        embedVar.add_field(name=f"{config.bot.prefix}links", value="Ссылки на игровой клиент", inline=False)
        embedVar.add_field(name=f"{config.bot.prefix}store", value="Донатный магазин", inline=False)
        embedVar.add_field(name=f"{config.bot.prefix}balance", value="Пополнение донатной валюты", inline=False)
        #embedVar.add_field(name=f"{config.cPREFIX}help", value="Эта справка", inline=False)
        #embedVar.add_field(name="Как пользоваться?", value="Напиши боту в лс", inline=False)
        await interaction.response.send_message(embed=embedVar)

async def setup(client):
    await client.add_cog(Help(client))