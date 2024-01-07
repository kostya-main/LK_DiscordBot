import discord
import aiomcrcon
import datetime
from discord.ext import commands, tasks
from aiomcrcon import Client

from main import db, config, shop

class Check(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.check.start()

    time = datetime.time(hour=1, minute=0, tzinfo=datetime.timezone.utc)
    @tasks.loop(time=time)
    async def check(self):
        if db.connect():
            try:
                #Проверка кого банить
                check_data = db.check_date(datetime.date.today())
                for Did in check_data:
                    #Баним игрока на сервере
                    user = db.getUsernameByDiscordID(Did['id'])[1]['username']
                    try:
                        async with Client(config.rcon.host, config.rcon.port, config.rcon.password) as client:
                            response = await client.send_cmd(f'ban {user} Ваша подписка истекла. Пожалуйста оплатите её для продолжение игры.')
                            print(response)
                    except aiomcrcon.RCONConnectionError:
                        with open('temp.txt', 'a') as file:
                            file.write(f'error ban {user} \n')
                    #Удаляем роль
                    guild = discord.utils.get(self.client.guilds, id = config.bot.guild)
                    member = guild.get_member(int(Did['id']))
                    remove_role = guild.get_role(shop.trealRole)
                    await member.remove_roles(remove_role)
                    #Удаляем время
                    db.remove_data(Did['id'])
                    #Вывод
                    user = await self.client.fetch_user(Did['id'])
                    await user.send('Ваш пробный период кончился!!! Пожалуйста купите подписку.')
                #Проверка 3 дня до бана
                check_notification = db.check_date_all()
                data_check = datetime.date.today() + datetime.timedelta(days=3)
                for Noti in check_notification:
                    if Noti['data_trial'] == data_check:
                        user = await client.fetch_user(Noti['id'])
                        await user.send('Через 3 дня у вас кончится подписка. Продлите её в ближайшее время!')
            except Exception as ex:
                print(ex)
            finally:
                db.close()

async def setup(client):
    if shop.enabled:
        await client.add_cog(Check(client))