import discord
import aiomcrcon
from discord.ext import commands
from discord import app_commands
from aiomcrcon import Client

from main import db, config, shop

class Prefix(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="prefix", description="Установить префикс")
    @app_commands.describe(prefix = "Ваш новый Префикс")
    @app_commands.default_permissions(permissions=0)
    async def prefix(self, interaction: discord.Integration, prefix:app_commands.Range[str, 5, 10]):
        guild = discord.utils.get(self.client.guilds, id = config.guild)
        member = guild.get_member(interaction.user.id)
        if db.connect():
            try:
                print(member.roles)
                role = member.roles[-1]
                if role.id == shop.trealRole:
                    user = db.getUsernameByDiscordID(interaction.user.id)[1]['username']
                    try:
                        async with Client(config.rcon.host, config.rcon.port, config.rcon.password) as client:
                            response = await client.send_cmd(f'lp user {user} meta setprefix {prefix}')
                            print(response)
                    except aiomcrcon.RCONConnectionError:
                        with open('temp.txt', 'a') as file:
                            file.write(f'error add role {user} \n')
                    await interaction.response.send_message('Префикс успешно изменён')
                else:
                    await interaction.response.send_message('**Ошибка:** Вы не приобрели Подписку. Приобрести её можно в /store')
            except Exception as ex:
                print(ex)
                await interaction.response.send_message('**Ошибка:** Что-то сломалось')
            finally:
                db.close()


async def setup(client):
    if shop.enabled:
        await client.add_cog(Prefix(client))