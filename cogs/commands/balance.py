import discord
from yookassa import Configuration, Payment
from discord.ext import commands
from discord import app_commands
import json

from main import config, shop
from main import db

Configuration.account_id = shop.id_shop
Configuration.secret_key = shop.token

class Balance(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name="balance", description="Пополнение баланса.")
    @app_commands.default_permissions(permissions=0)
    async def balance(self, interaction: discord.Integration):
        if db.connect():
            try:
                r = db.registered(interaction.user.id)
                if r[0] and r[1]:
                    embedVar = discord.Embed(title="Банк", description="Здесь ты можешь узнать остаток на счёте и пополнить его", color=config.bot.embedColor)
                    await interaction.response.send_message(embed=embedVar, view=Balance.Bank())
                else:
                    await interaction.response.send_message('**Ошибка:** Сначала необходимо зарегистрироваться')
            except Exception as ex:
                print(ex)
                await interaction.response.send_message(f'**Ошибка:** Неверный синтаксис\nПравильно: {config.bot.prefix}balance')
            finally:
                db.close()

    class Bank(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)

        @discord.ui.button(label='Узнать баланс', style=discord.ButtonStyle.grey, custom_id='balans')
        async def balans(self, interaction: discord.Interaction, button: discord.ui.Button):
            if db.connect():
                try:
                    p = db.check_money(interaction.user.id)
                    if p[0]:
                        embedVar = discord.Embed(title="Баланс:", description=f"{p[1]['money']} рублей", color=0x00ff09)
                        await interaction.response.edit_message(embed=embedVar, view=None)
                except Exception as ex:
                    print(ex)
                    await interaction.response.send_message('**Ошибка:** Неверный синтаксис')
                finally:
                    db.close()

        @discord.ui.button(label='Пополнить', style=discord.ButtonStyle.green, custom_id='pay_balans', emoji="🪙")
        async def pay_balans(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.send_modal(Balance.Money())

    class Money (discord.ui.Modal, title="Пополнение счёта"):
        pay_money:int = discord.ui.TextInput(label="Cумма:",placeholder="100", style=discord.TextStyle.short, required=True, min_length=2)

        async def on_submit(self, interaction: discord.Integration):
            if db.connect():
                try:
                    c = db.check_pay(interaction.user.id)
                    money = self.pay_money.value
                    if c[1]['invoice_id'] == None:
                        payment = Payment.create({
                            "amount": {
                            "value": f"{money}",
                            "currency": "RUB"
                            },
                            "confirmation": {
                                "type": "redirect",
                                "return_url": "https://discord.gg/nvAnn6GVs4"
                            },
                            "capture": True,
                            "description": f"Пополнение баланса на {money} рублей",
                            "merchant_customer_id": f"{interaction.user.id}"
                        })
                        payment_data = json.loads(payment.json())
                        p = db.save_pay(interaction.user.id, payment_data['id'])
                        if p[0]:
                            embedVar = discord.Embed(title="Счёт сформирован", description="Перейдите по ссылке ниже для оплаты.", color=config.bot.embedColor)
                            embedVar.add_field(name="Ссылка:", value=f"[Оплатить]({(payment_data['confirmation'])['confirmation_url']})", inline=False)
                            await interaction.response.edit_message(embed=embedVar, view=None)
                        elif (not p[0]):
                            await interaction.response.send_message('**Ошибка:** Неполадки в платёжной системе.')
                    else:
                        print(f"BAD RETURN {interaction.user.name}")
                        embedVar = discord.Embed(title="Счёт не оплачен", description="Пожалуста, оплатите счёт, выставленный ранее.", color=0xf44336)
                        await interaction.response.send_message(embed=embedVar)
                except Exception as ex:
                    print(ex)
                    await interaction.response.send_message('**Ошибка:** Необходимо указать сумму цифрами')
                finally:
                    db.close()

async def setup(client):
    if shop.enabled:
        await client.add_cog(Balance(client))