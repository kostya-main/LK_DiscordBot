import discord
import datetime
from discord.ext import commands, tasks

from main import db, config

class Birthday(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.birthday.start()

    time = datetime.time(hour=1, minute=5, tzinfo=datetime.timezone.utc)
    @tasks.loop(time=time)
    async def birthday(self):
        if db.connect():
            try:
                for Did in db.check_birthday(datetime.date.today().strftime('%m%d')):
                    user = await self.client.fetch_user(Did['id'])
                    embedVar = discord.Embed(title=f"С праздником вас {user.name}!!!", description="Мы рады что вы вместе с нами будем праздновать такой великолепный день. В честь этого мы дарим на ваш баланс 100$ надеемся вас это сильно парадует и вы дальше будем радовать вас удивительными мирами.", color=config.bot.embedColor)
                    db.add_money(Did['id'], 100)
                    await user.send(embed=embedVar)
            except Exception as ex:
                print(ex)
            finally:
                db.close()

async def setup(client):
    if config.bot.event_birthday:
        await client.add_cog(Birthday(client))