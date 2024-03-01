import discord
import aiomcrcon
from discord.ext import commands
from discord import app_commands
from aiomcrcon import Client
from dateutil.parser import parse

from main import db, config

class Reg(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="reg", description="Регистрация")
    @app_commands.default_permissions(permissions=0)
    async def reg(self, interaction: discord.Integration):
        if db.connect():
            r = db.getUsernameByDiscordID(interaction.user.id)
            if r[0] and r[1] is None:
                await interaction.response.send_modal(Reg.Registar())
            else:
                await interaction.response.send_message('Ты уже зарегистрирован')
        db.close()


    class Registar(discord.ui.Modal, title="Регистрация нового аккаунта"):
        def __init__(self):
            super().__init__(timeout=None)
            
        login = discord.ui.TextInput(label="Игровой логин",placeholder="Логин", style=discord.TextStyle.short, required=True, min_length=5, max_length=20)
        password = discord.ui.TextInput(label="Уникальный пароль",placeholder="Пароль", style=discord.TextStyle.short, required=True, min_length=5, max_length=20)
        if config.bot.event_birthday==True:
            birthday = discord.ui.TextInput(label="Дата твоего рождения",placeholder="2015-12-31", style=discord.TextStyle.short, required=True, min_length=8, max_length=10)
        promoCode = discord.ui.TextInput(label="Код из проморолика",placeholder="Промокод", style=discord.TextStyle.short, required=False, max_length=20)

        async def on_submit(self, interaction: discord.Interaction):
            if db.connect():
                try:
                    r = db.getUsernameByDiscordID(interaction.user.id)
                    login = self.login.value
                    password = self.password.value
                    promoCode = self.promoCode.value
                    if config.bot.event_birthday==True:
                        try:
                            birthday = parse(self.birthday.value)
                        except Exception:
                            await interaction.response.send_message('Вы указали дату не в том формате.')
                            return
                    else:
                        birthday = None
                    r_reg = db.register(interaction.user.id, login, password, birthday)
                    r_promo = db.check_promo(promoCode)
                    command = f"scoreboard players set {login} promo {r_promo[1]['id']}"
                    if r_promo[1]['enabled'] == 1:
                        try:
                            async with Client(config.rcon.host, config.rcon.port, config.rcon.password) as client:
                                response = await client.send_cmd(command)
                                print(response)
                        except aiomcrcon.RCONConnectionError:
                            with open('temp.txt', 'a') as file:
                                file.write(f'{command} \n')
                        db.add_money(interaction.user.id, r_promo[1]['value'])
                        db.add_use_promo(promoCode)
                    if r_reg[0]:
                        embedVar = discord.Embed(title="Вы успешно зарегистрированы!", description="Вам предоставлен доступ на пробный период в 7 дней. Этого времени должно хватить, чтобы вы смогли составить мнение о проекте. По истечении срока мы предложим вам оформить подписку за символическую плату 100 рублей/месяц. Доступ по подписке помогает нам обеспечить адекватную аудиторию на сервере и больше времени уделять его развитию. Надеемся на ваше понимание и желаем вам приятной игры!", color=config.bot.embedColor)
                        embedVar.add_field(name="Ссылки на игровой клиент", value="Он необходим для входа на сервер", inline=False)
                        embedVar.add_field(name="Windows", value=f"[Скачать]({config.web.url_launcher_exe})", inline=True)
                        embedVar.add_field(name="Linux/MacOS", value=f"[Скачать]({config.web.url_launcher_jar})", inline=True)
                        await interaction.response.send_message(embed=embedVar)
                    elif (not r[0]) and (r[1] == '1062'):
                        await interaction.response.send_message('Ник или пароль уже занят')
                except Exception as ex:
                    print(ex)
                    await interaction.response.send_message(f'**Ошибка:** Неверный синтаксис\nПравильно: {config.bot.prefix}reg')
                finally:
                    db.close()


async def setup(client):
    await client.add_cog(Reg(client))