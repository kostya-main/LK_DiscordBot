import discord
import minepi
from discord.ext import commands
from discord import app_commands
from PIL import Image
from io import BytesIO
import aiofiles.os

from main import config, db
import scstorage

class Cape(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="cape", description="Поменяйте плащ")
    @app_commands.describe(file = "Файл с новым плащом")
    @app_commands.default_permissions(permissions=0)
    async def cape(self, interaction: discord.Integration, file: discord.Attachment):
        if db.connect():
            try:
                r = db.registered(interaction.user.id)
                if r[0] and r[1]:
                    r_getUser = db.getUsernameByDiscordID(interaction.user.id)
                    if r_getUser[0]:
                        username = r_getUser[1]['username']
                        if await scstorage.savecape(username, file.url):
                            uuid=db.check_uuid(username)[1]["uuid"]
                            if await aiofiles.os.path.exists(f'{config.web.skindir}/{uuid}.png'):
                                raw_skin = Image.open(f'{config.web.skindir}/{uuid}.png')
                            else:
                                raw_skin = Image.open(config.web.defaultSkin)
                            embedVar = discord.Embed(title="Успешно!", description="Ваш плащ стал таким.", color=0x00ff09)
                            #Создание 3D модели
                            s = minepi.Skin(raw_skin=raw_skin, raw_cape=Image.open(f'{config.web.capedir}/{uuid}.png'))
                            io = BytesIO()
                            images = await s.render_skin(hr=180, vrc=0)
                            images.save(io, 'PNG')
                            io.seek(0)
                            im = discord.File(io, 'skin.png')
                            embedVar.set_image(url='attachment://skin.png')
                            await interaction.response.send_message(embed=embedVar, file=im)
                        else:
                            await interaction.response.send_message('**Ошибка:** Неверный файл плаща')
                else:
                    await interaction.response.send_message('**Ошибка:** Сначала необходимо зарегистрироваться') 
            except Exception as ex:
                print(ex)
                await interaction.response.send_message(f'**Ошибка:** Неверный синтаксис\nПравильно: {config.bot.prefix}cape [файл плаща]')
            finally:
                db.close()

async def setup(client):
    await client.add_cog(Cape(client))