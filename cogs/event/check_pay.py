import discord
from discord.ext import commands

from main import db

class Check_pay(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def check_pay(status, id, value):
        if db.connect():
            try:
                if status:
                    discord = db.check_discordID_toInvoice_id(id)[1]['id']
                    #user = await client.fetch_user(discord)
                    #print(user)
                    #await user.send('Спс за джоин на сервер!')
                    db.add_money(discord, value)
                    db.delete_pay(discord)
                else:
                    discord = db.check_discordID_toInvoice_id(id)[1]['id']
                    #await client.fetch_user(discord).send('Спс за джоин на сервер!')
                    db.delete_pay(discord)
            except Exception as ex:
                print(ex)
            finally:
                db.close()

async def setup(client):
    await client.add_cog(Check_pay(client))