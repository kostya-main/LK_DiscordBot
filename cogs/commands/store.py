import discord
import aiomcrcon
import datetime
from discord.ext import commands
from discord import app_commands
from aiomcrcon import Client

from main import db, config, shop

class Store(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="store", description="Магазин")
    @app_commands.default_permissions(permissions=0)
    async def store(self, interaction: discord.Integration):
        if db.connect():
            try:
                r = db.registered(interaction.user.id)
                if r[0] and r[1]:
                    embedVar = discord.Embed(title="Магазин", description="Здесь ты можешь приобрести различные привелегии.", color=config.bot.embedColor)
                    embedVar.add_field(name="Подписка 📜", value="Приобретение доступа к серверу.", inline=False)
                    await interaction.response.send_message(embed=embedVar, view=Store.Rules(client=self.client))
                else:
                    await interaction.response.send_message('**Ошибка:** Сначала необходимо зарегистрироваться')
            except Exception as ex:
                print(ex)
                await interaction.response.send_message(f'**Ошибка:** Неверный синтаксис\nПравильно: {config.bot.prefix}store')
            finally:
                db.close()

    class Rules(discord.ui.View):
        def __init__(self, client):
            super().__init__(timeout=None)
            self.client = client

        @discord.ui.button(label="Подписка", style=discord.ButtonStyle.green, custom_id="rule", emoji="📜")
        async def rule(self, interaction: discord.Interaction, button: discord.ui.Button):
            embedVar = discord.Embed(title="Условия приобретения подписки.", description='>>> Я, нижеподписавшийся (далее «Пользователь»), подтверждаю свое согласие с условиями подписки (далее «Подписка»).\n \n Я понимаю и соглашаюсь с тем, что при покупке Подписки я получаю доступ к определенным услугам, продуктам или функциям, которые могут быть изменены или прекращены по решению администрации сервера.\n \n Я понимаю, что цена Подписки может изменяться по решению администрации сервера и что предоставление доступа к услугам, продуктам или функциям может быть прекращено в любое время по решению администрации сервера. \n \n Я понимаю и соглашаюсь с тем, что Подписка не может быть прекращена до истечения текущего периода оплаты. \n \n Я понимаю и соглашаюсь с тем, что все платежи за Подписку не возвращаются.\n \n Я понимаю и соглашаюсь с тем, что все права и обязанности, определенные в этом соглашении, могут быть изменены по решению администрации сервера. \n \n Я понимаю и соглашаюсь с тем, что при покупке Подписки я принимаю настоящее пользовательское соглашение и принимаю все условия и положения, изложенные в настоящем соглашении.', color=0xf44336)
            embedVar.add_field(name="Укажите что согласны с условиями приобретения", value="", inline=False)
            await interaction.response.edit_message(embed=embedVar, view=Store.ButtonView(client=self.client))

    class ButtonView(discord.ui.View):
        def __init__(self, client):
            super().__init__(timeout=None)
            self.client = client

        @discord.ui.button(label="Я согласен", style=discord.ButtonStyle.green, custom_id="yes", emoji="✅")
        async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
            embedVar = discord.Embed(title="Подписка", description="Проходка на проект!", color=config.bot.embedColor)
            embedVar.add_field(name="Описание", value="Инфо про роль.", inline=False)
            await interaction.response.edit_message(embed=embedVar, view=Store.Pay(client=self.client))
    
        @discord.ui.button(label="Я не согласен", style=discord.ButtonStyle.red, custom_id="no", emoji='✖️')
        async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.edit_message(content='Без соглашения мы в праве отказать в вам в обслуживании.', embed=None, view=None)

    class Pay(discord.ui.View):
        def __init__(self, client):
            super().__init__(timeout=None)
            self.client = client

        @discord.ui.button(label="Приобрести", style=discord.ButtonStyle.green, custom_id="pay", emoji="⚡")
        async def pay(self, interaction: discord.Interaction, button: discord.ui.Button):
            if db.connect():
                try:
                    coin = db.check_money(interaction.user.id)
                    guild = discord.utils.get(self.client.guilds, id = config.bot.guild)
                    member = guild.get_member(interaction.user.id)
                    for list_role in member.roles:
                        if list_role.id == shop.trealRole:
                            embedVar = discord.Embed(title="Вы уже приобрели данную привелегию.", description="Ознакомьтесь с другими возможностями.", color=0xf44336)
                            await interaction.response.edit_message(embed=embedVar)
                            return
                    if coin[1]['money'] >= 100:
                        # разбанить на сервере
                        user = db.getUsernameByDiscordID(interaction.user.id)[1]['username']
                        try:
                            async with Client(config.rcon.host, config.rcon.port, config.rcon.password) as client:
                                response = await client.send_cmd(f'pardon {user}', 20)
                                print(response)
                        except aiomcrcon.RCONConnectionError:
                            with open('temp.txt', 'a') as file:
                                file.write(f'error pay subscriber {user} \n')
                        # выдаём роль
                        await member.add_roles(guild.get_role(shop.trealRole))
                        # удалёем рубли и выдаём дату
                        data = datetime.date.today() + datetime.timedelta(days=30)
                        db.add_data(data, interaction.user.id)
                        db.remove_money(interaction.user.id, 100)
                        # Выыод
                        embedVar = discord.Embed(title="Благодарим за поддержку!", description="Мы ценим ваш выбор.", color=0x00ff09)
                        await interaction.response.edit_message(embed=embedVar,view=None)
                    else:
                        embedVar = discord.Embed(title="Недостаточно средств!", description="Пожалуиста пополните свой счёт!", color=0xf44336)
                        await interaction.response.edit_message(embed=embedVar)
                except Exception as ex:
                    print(ex)
                    await interaction.response.send_message('**Ошибка:** Неверный синтаксис выдачи')
                finally:
                    db.close()

        @discord.ui.button(label='Назад', style=discord.ButtonStyle.red, custom_id='cancel', emoji='⏪')
        async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
            embedVar = discord.Embed(title="Магазин", description="Здесь ты можешь приобрести различные привилегии.", color=config.bot.embedColor)
            embedVar.add_field(name="Подписка 📜", value="Приобретение доступа к серверу.", inline=False)
            await interaction.response.edit_message(embed=embedVar, view=Store.Rules(client=self.client))

async def setup(client):
    if shop.enabled:
        await client.add_cog(Store(client))