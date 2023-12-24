import discord
from discord.ext import commands
from discord import app_commands

from main import db, config

class Password(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="password", description="Поменять пароль")
    @app_commands.describe(new_pass = "Введите новый пароль")
    @app_commands.default_permissions(permissions=0)
    async def password(self, interaction: discord.Integration, new_pass: app_commands.Range[str, 5, None]):
        if db.connect():
            try:
                r = db.registered(interaction.user.id)
                if r[0] and r[1]:
                    r_chpass = db.changePassword(interaction.user.id, new_pass)
                    if r_chpass[0]:
                        await interaction.response.send_message('Вы успешно изменили пароль')
                    elif (not r_chpass[0]) and (r_chpass[1] == '1062'):
                        await interaction.response.send_message('Пароль уже используется')
                else:
                    await interaction.response.send_message('**Ошибка:** Сначала необходимо зарегистрироваться')
            except Exception as ex:
                print(ex)
                await interaction.response.send_message(f'**Ошибка:** Неверный синтаксис\nПравильно: {config.bot.prefix}password [новый пароль]')
            finally:
                db.close()

async def setup(client):
    await client.add_cog(Password(client))