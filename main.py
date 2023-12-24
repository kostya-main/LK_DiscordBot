import discord
from discord.ext import commands
import signal
import os
import sys
import multiprocessing
from dynaconf import Dynaconf

import dbmanager


config = Dynaconf(settings_files='conf/settings.yaml',apply_default_on_none=True, secrets='.secrets.yaml')
shop = Dynaconf(settings_files='conf/shop.yaml', apply_default_on_none=True, secrets='.secrets.yaml')
client = commands.Bot(command_prefix=config.bot.prefix, intents=discord.Intents.all(), help_command=None)
db = dbmanager.dbm(config.db.login, config.db.password, config.db.host, config.db.database)


@client.event
async def on_ready():
    try:
        #Загрузка папки cogs
        for dir_cogs in os.listdir('./cogs'):
            for filename in os.listdir(f'./cogs/{dir_cogs}'):
                if filename.endswith('.py'):
                    await client.load_extension(f'cogs.{dir_cogs}.{filename[:-3]}')
                else:
                    print(f'Не является Cogs {filename}')
        #Удаление всех команд из подсказок в Discord
        #for ext in cogs:
        #    await client.load_extension(ext)
        #client.tree.clear_commands(guild=None)
        print(f"Команд найдено {len(await client.tree.sync())}")
    except Exception as ex:
        print(ex)



def signal_handler(signal, frame):
    print('\nStopping!')
    scs_thread.terminate()
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    from scstorage import scstorage
    scs_thread = multiprocessing.Process(target=scstorage.server)
    scs_thread.start()
    client.run(config.bot.token)