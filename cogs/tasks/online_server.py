import discord
import mcstatus.server
from discord.ext import commands, tasks
from main import config


class Server(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.update_status.start()

    @tasks.loop(minutes=1)
    async def update_status(self):
        try:
            server = await mcstatus.server.JavaServer.async_lookup(config.server_ping.ipServer)
            status = await server.async_status()
            if status.players.online != 0:
                await self.client.change_presence(
                    activity=discord.Game(f"{status.players.online}/{status.players.max} игроков"),
                    status=discord.Status.online
                )
            else:
                await self.client.change_presence(
                    activity=discord.Game(f"{status.players.online}/{status.players.max} игроков"),
                    status=discord.Status.idle
                )
        except Exception as ex:
            await self.client.change_presence(
                    activity=discord.Game("Offline"),
                    status=discord.Status.dnd
                )
            print(f"Ошибка при обновлении статуса: {ex}")

async def setup(client):
    if (config.server_ping.enabled):
        await client.add_cog(Server(client))