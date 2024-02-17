import discord
import minepi
from discord.ext import commands
from discord import app_commands
from PIL import Image
from io import BytesIO
import aiofiles.os

from main import db, config
import scstorage

class Skin(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="skin", description="Поменяйте внешний вид персонажа")
    @app_commands.describe(file = "Файл с своим новым скином")
    @app_commands.default_permissions(permissions=0)
    async def skin(self, interaction: discord.Integration, file: discord.Attachment):
        if db.connect():
            try:
                r = db.registered(interaction.user.id)
                if r[0] and r[1]:
                    r_getUser = db.getUsernameByDiscordID(interaction.user.id)
                    if r_getUser[0]:
                        username = r_getUser[1]['username']
                        if await scstorage.saveprofile(username, file.url):
                            uuid=db.check_uuid(username)[1]["uuid"]
                            skinDir = config.web.skindir
                            caprDir = config.web.capedir
                            if await aiofiles.os.path.exists(f'{caprDir}/{uuid}.png'):
                                raw_cape = Image.open(f'{caprDir}/{uuid}.png')
                            else:
                                raw_cape = Image.open(config.web.defaultCape)
                            embedVar = discord.Embed(title="Успешно!", description="Ваш скин стал таким.", color=0x00ff09)
                            #Создание 3D модели
                            s = minepi.Skin(raw_skin=Image.open(f'{skinDir}/{uuid}.png'), raw_cape=raw_cape)
                            io = BytesIO()
                            images = await s.render_skin(aa=True, hr=40, vr=-25, vrla=-40, vrra=40, vrll=40, vrrl=-40)
                            images.save(io, 'PNG')
                            io.seek(0)
                            im = discord.File(io, 'skin.png')
                            embedVar.set_image(url='attachment://skin.png')
                            await interaction.response.send_message(embed=embedVar, file=im)
                        else:
                            await interaction.response.send_message('**Ошибка:** Неверный файл скина')
                else:
                    await interaction.response.send_message('**Ошибка:** Сначала необходимо зарегистрироваться') 
            except Exception as ex:
                print(ex)
                await interaction.response.send_message(f'**Ошибка:** Неверный синтаксис\nПравильно: {config.bot.prefix}skin [файл скина]')
            finally:
                db.close()

async def setup(client):
    await client.add_cog(Skin(client))