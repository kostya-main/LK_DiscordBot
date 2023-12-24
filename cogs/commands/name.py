import discord
from discord.ext import commands
from discord import app_commands

from main import db, config

class Name(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="name", description="Изменить псевдоним")
    @app_commands.describe(nickname = "Введите новый псевдоним")
    @app_commands.default_permissions(permissions=0)
    async def name(self, interaction: discord.Integration, nickname:app_commands.Range[str, 5, None]):
        if db.connect():
            try:
                r = db.registered(interaction.user.id)
                if r[0] and r[1]:
                    r_chpass = db.changeUsername(interaction.user.id, nickname)
                    if r_chpass[0]:
                        await interaction.response.send_message('Псевдоним успешно изменён')
                    elif (not r_chpass[0]) and (r_chpass[1] == '1062'):
                        await interaction.response.send_message('Ник или пароль уже занят')
                else:
                    await interaction.response.send_message('**Ошибка:** Сначала необходимо зарегистрироваться')
            except Exception as ex:
                print(ex)
                await interaction.response.send_message(f'**Ошибка:** Неверный синтаксис\nПравильно: {config.bot.prefix}name [новый псевдоним]')
            finally:
                db.close()

async def setup(client):
    await client.add_cog(Name(client))