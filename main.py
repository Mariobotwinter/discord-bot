
import discord
from discord.ext import commands
import os
import asyncio
from googletrans import Translator

intents = discord.Intents.default()
intents.message_content = True
intents.dm_messages = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

LOG_CHANNEL_ID = 1367958714379927693
SERVER_ID = 1324363465745240118
ROL_ID = 1327354131181994004
translator = Translator()
pending_users = {}

class AjutorButtons(discord.ui.View):
    @discord.ui.button(label="Metode de plată", style=discord.ButtonStyle.primary)
    async def metode(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Poți plăti prin Revolut (https://revolut.me/liliancj2v), PayPal (https://www.paypal.me/RomaniaQuiz) sau transfer bancar (IBAN: RO56BTRLRONCRT0CQ2528301)", ephemeral=True)

    @discord.ui.button(label="Cum primesc accesul", style=discord.ButtonStyle.primary)
    async def livrare(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("După confirmarea plății, primești automat accesul pe server.", ephemeral=True)

    @discord.ui.button(label="Întâmpin dificultăți", style=discord.ButtonStyle.danger)
    async def dificultati(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Owner-ul serverului va fi anunțat și te va contacta.", ephemeral=True)
        canal_log = bot.get_channel(LOG_CHANNEL_ID)
        if canal_log:
            await canal_log.send(f"**[Problema semnalată]** {interaction.user.mention} a apăsat pe butonul „Întâmpin dificultăți”")

@bot.event
async def on_ready():
    print(f"Botul este online ca {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    user_id = message.author.id

    if isinstance(message.channel, discord.DMChannel) and message.attachments:
        for attachment in message.attachments:
            if attachment.content_type and attachment.content_type.startswith("image/"):
                log_channel = bot.get_channel(LOG_CHANNEL_ID)
                if log_channel:
                    await log_channel.send(f"**Dovadă de plată de la {message.author.mention}:**")
                    await log_channel.send(attachment.url)

                guild = bot.get_guild(SERVER_ID)
                if guild:
                    member = guild.get_member(user_id)
                    if member:
                        role = guild.get_role(ROL_ID)
                        if role:
                            await asyncio.sleep(1)
                            await member.add_roles(role)
                            await message.channel.send("Mulțumesc! Ți-am acordat accesul.")
                        else:
                            await message.channel.send("Rolul nu a fost găsit.")
                    else:
                        await message.channel.send("Te rog să fii pe server pentru a-ți oferi accesul.")
                return

    if isinstance(message.channel, discord.DMChannel):
        mesaj = message.content.lower()
        răspuns = None

        if any(cuv in mesaj for cuv in ["am plătit", "gata", "am trimis", "am dat"]):
            await message.channel.send("Trimite-mi te rog o dovadă de plată (un screenshot).")
            return

        if any(cuv in mesaj for cuv in ["salut", "hei", "hello", "buna", "sall"]):
            răspuns = "Salut! Cu ce te pot ajuta? Ești interesat de achiziționarea full accesului?"

        elif any(cuv in mesaj for cuv in ["da", "ok", "sunt", "sigur", "vreau", "cumpăr", "interesat"]):
            răspuns = "Accesul costă 70 RON. Poți plăti prin Revolut, PayPal sau transfer cu cardul."
            await start_follow_up_timer(message)

        elif any(cuv in mesaj for cuv in ["revolut", "paypal", "card", "transfer", "iban"]):
            răspuns = (
                "Poți plăti prin Revolut aici: https://revolut.me/liliancj2v"
"
                "PayPal: https://www.paypal.me/RomaniaQuiz
"
                "IBAN: RO56BTRLRONCRT0CQ2528301 - Titular: Nume la alegere"
            )

        elif any(cuv in mesaj for cuv in ["preț", "pret", "cât costă", "cost", "prez"]):
            răspuns = "Prețul este 70 RON."
            await start_follow_up_timer(message)

        else:
            răspuns = (
                "Nu există răspuns pentru ce mi-ai scris (facem îmbunătățiri zilnice).
"
                "Dacă întâmpini probleme, contactează Owner-ul serverului.

"
                "Până atunci te pot ajuta cu:"
            )
            await message.channel.send(răspuns, view=AjutorButtons())
            return

        await asyncio.sleep(1)
        await message.channel.send(răspuns)

        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(f"**[DM de la {message.author}]**
**Mesaj:** {message.content}
**Răspuns:** {răspuns}")

        if user_id in pending_users:
            pending_users[user_id]['task'].cancel()
            del pending_users[user_id]

    await bot.process_commands(message)

async def start_follow_up_timer(message):
    user_id = message.author.id

    if user_id in pending_users:
        pending_users[user_id]['task'].cancel()

    async def timer():
        try:
            await asyncio.sleep(600)
            await message.channel.send("Mai ești aici? Pot să te ajut cu altceva?")
        except asyncio.CancelledError:
            pass

    task = asyncio.create_task(timer())
    pending_users[user_id] = {"task": task}

bot.run(os.getenv("TOKEN"))
