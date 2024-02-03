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

    async def start_message(self, interaction: discord.Integration, wheel: bool):
        embedVar = discord.Embed(title="Магазин", description="Здесь ты можешь приобрести различные привелегии.", color=config.bot.embedColor)
        embedVar.add_field(name="В состоянии по умолчанию магазин может не работать.", value="Загляни в файл команды и подправь товары.", inline=False)
        if wheel:
            await interaction.response.edit_message(embed=embedVar, view=Store.Select(client=self.client))
        else:
            await interaction.response.send_message(embed=embedVar, view=Store.Select(client=self.client))

    @app_commands.command(name="store", description="Магазин")
    @app_commands.default_permissions(permissions=0)
    async def store(self, interaction: discord.Integration):
        if db.connect():
            try:
                r = db.registered(interaction.user.id)
                if r[0] and r[1]:
                    await Store.start_message(self, interaction, wheel=False)
                else:
                    await interaction.response.send_message('**Ошибка:** Сначала необходимо зарегистрироваться')
            except Exception as ex:
                print(ex)
                await interaction.response.send_message(f'**Ошибка:** Неверный синтаксис\nПравильно: {config.bot.prefix}store')
            finally:
                db.close()

    class Select(discord.ui.View):
        def __init__(self, client):
            super().__init__(timeout=None)
            self.client = client

        @discord.ui.select(placeholder="Выберете интересующий товар", options=[
            discord.SelectOption(label="Подписка", description="Приобретение доступа к серверу.", emoji="📜", value='subscription'),
            discord.SelectOption(label="Роль VIP", description="Приобретение роль власти.", emoji="💎", value='vip'),
            discord.SelectOption(label="Роль Admin", description="Приобретение роль власти.", emoji="⚖️", value='admin'),
            discord.SelectOption(label="Яйцо Дракона", description="Приобретение предмет 'Яйцо Дракона.'", emoji="🦇", value='item')
        ])
        async def callback(self, interaction:discord.Interaction, select: discord.ui.Select):
            if select.values[0] == 'subscription':
                embedVar = discord.Embed(title="Подписка", description="Проходка на проект!", color=config.bot.embedColor)
                embedVar.add_field(name="Описание", value="Инфо про роль.", inline=True)
                embedVar.add_field(name="Цена", value="100 $", inline=True)
                await interaction.response.edit_message(embed=embedVar, view=Store.Pay(client=self.client, money=100, type='subscription'))
            elif select.values[0] == 'vip':
                embedVar = discord.Embed(title="Роль VIP", description="Роль всевластие", color=config.bot.embedColor)
                embedVar.add_field(name="Описание", value="Инфо про роль.", inline=True)
                embedVar.add_field(name="Цена", value="50 $", inline=True)
                await interaction.response.edit_message(embed=embedVar, view=Store.Pay(client=self.client, money=50, type='game role', arg='vip'))
            elif select.values[0] == 'admin':
                embedVar = discord.Embed(title="Роль Admin", description="Роль admin discord", color=config.bot.embedColor)
                embedVar.add_field(name="Описание", value="Инфо про роль.", inline=True)
                embedVar.add_field(name="Цена", value="50 $", inline=True)
                await interaction.response.edit_message(embed=embedVar, view=Store.Pay(client=self.client, money=50, type='discord role', arg=719317524994326649))
            elif select.values[0] == 'item':
                embedVar = discord.Embed(title="Яйцо Дракона", description="Кто из него вылупится?", color=config.bot.embedColor)
                embedVar.add_field(name="Описание", value="Инфо про предмет.", inline=True)
                embedVar.add_field(name="Цена", value="20 $", inline=True)
                await interaction.response.edit_message(embed=embedVar, view=Store.Pay(client=self.client, money=20, type='item', arg='minecraft:dragon_egg'))
    
    class Pay(discord.ui.View):
        def __init__(self, client, money:int, type, arg = None):
            super().__init__(timeout=None)
            self.client = client
            self.money = money
            self.type = type
            self.arg = arg

        @discord.ui.button(label="Приобрести", style=discord.ButtonStyle.green, custom_id="pay", emoji="⚡")
        async def pay(self, interaction: discord.Interaction, button: discord.ui.Button):
            if db.connect():
                try:
                    coin = db.check_money(interaction.user.id)
                    user = db.getUsernameByDiscordID(interaction.user.id)[1]['username']


                    if self.type == 'subscription':
                        guild = discord.utils.get(self.client.guilds, id = config.bot.guild)
                        member = guild.get_member(interaction.user.id)
                        # проверка наличии роли
                        for list_role in member.roles:
                            if list_role.id == shop.trealRole:
                                embedVar = discord.Embed(title="Вы уже приобрели данную привелегию.", description="Ознакомьтесь с другими возможностями.", color=0xf44336)
                                await interaction.response.edit_message(embed=embedVar)
                                return
                        if coin[1]['money'] >= self.money:
                            # разбанить на сервере
                            command = f'pardon {user}'
                            try:
                                async with Client(config.rcon.host, config.rcon.port, config.rcon.password) as client:
                                    response = await client.send_cmd(command)
                                    print(response)
                            except aiomcrcon.RCONConnectionError:
                                with open('temp.txt', 'a') as file:
                                    file.write(f'{command} \n')
                            # выдаём роль
                            await member.add_roles(guild.get_role(shop.trealRole))
                            # удаляем рубли и выдаём дату
                            data = datetime.date.today() + datetime.timedelta(days=30)
                            db.add_data(data, interaction.user.id)
                            db.remove_money(interaction.user.id, self.money)
                            # Вывод
                            embedVar = discord.Embed(title="Благодарим за поддержку!", description="Мы ценим ваш выбор.", color=0x00ff09)
                            await interaction.response.edit_message(embed=embedVar,view=None)
                        else:
                            embedVar = discord.Embed(title="Недостаточно средств!", description="Пожалуиста пополните свой счёт!", color=0xf44336)
                            await interaction.response.edit_message(embed=embedVar)


                    elif self.type == 'game role':
                        # проверка наличии роли
                        if db.check_game_role(db.check_uuid(user)[1]['uuid'])[1]['permission'] == f'group.{self.arg}':
                            embedVar = discord.Embed(title="Вы уже приобрели данную привелегию.", description="Ознакомьтесь с другими возможностями.", color=0xf44336)
                            await interaction.response.edit_message(embed=embedVar)
                            return
                        if coin[1]['money'] >= self.money:
                            # выдаём роль
                            command = f'lp user {user} parent set {self.arg}'
                            try:
                                async with Client(config.rcon.host, config.rcon.port, config.rcon.password) as client:
                                    response = await client.send_cmd(command)
                                    print(response)
                            except aiomcrcon.RCONConnectionError:
                                with open('temp.txt', 'a') as file:
                                    file.write(f'{command} \n')
                            # Вывод
                            db.remove_money(interaction.user.id, self.money)
                            embedVar = discord.Embed(title="Благодарим за поддержку!", description="Мы ценим ваш выбор.", color=0x00ff09)
                            await interaction.response.edit_message(embed=embedVar,view=None)
                        else:
                            embedVar = discord.Embed(title="Недостаточно средств!", description="Пожалуиста пополните свой счёт!", color=0xf44336)
                            await interaction.response.edit_message(embed=embedVar)


                    elif self.type == 'discord role':
                        guild = discord.utils.get(self.client.guilds, id = config.bot.guild)
                        member = guild.get_member(interaction.user.id)
                        # проверка наличии роли
                        for list_role in member.roles:
                            if list_role.id == self.arg:
                                embedVar = discord.Embed(title="Вы уже приобрели данную привелегию.", description="Ознакомьтесь с другими возможностями.", color=0xf44336)
                                await interaction.response.edit_message(embed=embedVar)
                                return
                        if coin[1]['money'] >= self.money:
                            # выдаём роль
                            await member.add_roles(guild.get_role(self.arg))
                            # удаляем рубли и выдаём дату
                            db.remove_money(interaction.user.id, self.money)
                            # Вывод
                            embedVar = discord.Embed(title="Благодарим за поддержку!", description="Мы ценим ваш выбор.", color=0x00ff09)
                            await interaction.response.edit_message(embed=embedVar,view=None)
                        else:
                            embedVar = discord.Embed(title="Недостаточно средств!", description="Пожалуиста пополните свой счёт!", color=0xf44336)
                            await interaction.response.edit_message(embed=embedVar)
                            

                    elif self.type == 'item':
                        if coin[1]['money'] >= self.money:
                            # выдаём предмет
                            command = f'give {user} {self.arg}'
                            try:
                                async with Client(config.rcon.host, config.rcon.port, config.rcon.password) as client:
                                    response = await client.send_cmd(command)
                                    print(response)
                            except aiomcrcon.RCONConnectionError:
                                with open('temp.txt', 'a') as file:
                                    file.write(f'{command} \n')
                            # Вывод
                            db.remove_money(interaction.user.id, self.money)
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
            await Store.start_message(self, interaction, wheel=True)

async def setup(client):
    if shop.enabled:
        await client.add_cog(Store(client))