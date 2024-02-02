import discord
from datetime import datetime
from discord.ext import commands
from discord import app_commands

from main import db, config

class Ban_list(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def start_message(self, interaction: discord.Integration, wheel:bool, page:int):
        if db.connect():
            try:
                # Без понятия как от них избавиться от инициализации переменных
                name = ''
                operator = ''
                reason = ''
                time = ''
                for banlist in db.check_banlist(page):
                    name += ("\n" f"{banlist['name']}")
                    operator += ("\n" f"{banlist['operator']}")
                    reason += ("\n" f"{banlist['reason']}")
                    if int(banlist['end']) != -1:
                        time += ("\n" f"{str(datetime.fromtimestamp(int(banlist['end']) / 1000) - datetime.today())}")
                    else:
                        time += ("\n" "Навсегда")
                embedVar = discord.Embed(title="Бан лист проекта", description=f"Лист: {page}", color=config.bot.embedColor)
                embedVar.add_field(name=f"Нарушитель:", value=f"{name}", inline=True)
                embedVar.add_field(name=f"Админ:", value=f"{operator}", inline=True)
                embedVar.add_field(name=f"Причина:", value=f"{reason}", inline=True)
                embedVar.add_field(name=f"Свободен через:", value=f"{time}", inline=True)
                if wheel:
                    await interaction.response.edit_message(embed=embedVar, view=Ban_list.Button(self.client, page))
                else:
                    await interaction.response.send_message(embed=embedVar, view=Ban_list.Button(self.client, page))
            except Exception as ex:
                print(ex)
                await interaction.response.send_message(f'**Ошибка:** Обратитесь для решения проблемы администратору.')
            finally:
                db.close()

    @app_commands.command(name="ban-list", description="Список игроков нарушавшие правила")
    @app_commands.default_permissions(permissions=0)
    async def ban_list(self, interaction: discord.Integration):
        await Ban_list.start_message(self, interaction, wheel=False, page=1)
    
    class Button (discord.ui.View):
        def __init__(self, client, page):
            super().__init__(timeout=None)
            self.client = client
            self.page = page
    
        @discord.ui.button(label='', style=discord.ButtonStyle.grey, emoji='⬅️', custom_id='back')
        async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.page -= 1
            await Ban_list.start_message(self, interaction, wheel=True, page=self.page)

        @discord.ui.button(label='', style=discord.ButtonStyle.grey, emoji='➡️', custom_id='next')
        async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.page += 1
            await Ban_list.start_message(self, interaction, wheel=True, page=self.page)



async def setup(client):
    await client.add_cog(Ban_list(client))