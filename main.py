import discord
from discord.ext import commands
from discord.ui import Button, View
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

class HelpButtons(View):
    def __init__(self, user):
        super().__init__(timeout=None)
        self.user = user

    @discord.ui.button(label="Metode de plată", style=discord.ButtonStyle.primary)
    async def plata(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            return await interaction.response.send_message("Acest meniu nu este pentru tine.", ephemeral=True)
        await interaction.response.send_message(
            "Poți plăti prin:\n- Revolut: https://revolut.me/liliancj2v\n- PayPal: https://www.paypal.me/RomaniaQuiz\n- Card/IBAN: RO56BTRLRONCRT0CQ2528301", ephemeral=True)

    @discord.ui.button(label="Cum primesc accesul", style=discord.ButtonStyle.primary)
    async def acces(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            return await interaction.response.send_message("Acest meniu nu este pentru tine.", ephemeral=True)
        await interaction.response.send_message(
            "După plată, trimite dovada printr-un screenshot aici. Botul îți oferă automat rolul pe server.", ephemeral=True)

    @discord.ui.button(label="Întâmpin dificultăți", style=discord.ButtonStyle.danger)
    async def dificultati(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            return await interaction.response.send_message("Acest meniu nu este pentru tine.", ephemeral=True)
        log = bot.get_channel(LOG_CHANNEL_ID)
        await interaction.response.send_message("Owner-ul a fost notificat și te va contacta!", ephemeral=True)
        if log:
            await log.send(f"**[ALERTĂ]** {interaction.user.mention} a apăsat pe „Întâmpin dificultăți”.")

@bot.event
async def on_ready():
    print(f"Botul este online ca {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    user_id = message.author.id

    # dacă trimite poză cu dovada direct
    if isinstance(message.channel, discord.DMChannel) and message.attachments:
        for attachment in message.attachments:
            if attachment.content_type and attachment.content_type.startswith("image/"):
                log = bot.get_channel(LOG_CHANNEL_ID)
                if log:
                    await log.send(f"**Dovadă de plată de la {message.author}:**")
                    await log.send(attachment.url)

                guild = bot.get_guild(SERVER_ID)
                if guild:
                    member = guild.get_member(user_id)
                    if member:
                        rol = guild.get_role(ROL_ID)
                        if rol:
                            await member.add_roles(rol)
                            await message.channel.send("Mulțumesc! Ți-am acordat accesul.")
                        else:
                            await message.channel.send("Rolul nu a fost găsit.")
                    else:
                        await message.channel.send("Te rog să fii pe server pentru a-ți oferi accesul.")
                return

    if isinstance(message.channel, discord.DMChannel):
        mesaj = message.content.lower()
        răspuns = None

        if any(x in mesaj for x in ["am plătit", "am platit", "gata", "am trimis", "am dat"]):
            await message.channel.send("Trimite-mi te rog o dovadă de plată (un screenshot).")
            return

        elif any(x in mesaj for x in ["salut", "sall", "bună", "buna", "hei", "hello", "hey"]):
            răspuns = "Salut! Cu ce te pot ajuta? Ești interesat de achiziționarea full accesului?"

        elif any(x in mesaj for x in ["acces", "vreau acces", "cumpăr", "achiziționez", "dă-mi acces", "doresc acces"]):
            răspuns = "Cu ce metodă plătești? Revolut, PayPal sau transfer bancar. (Accesul costă 70 RON)"
            await start_follow_up_timer(message)

        elif any(x in mesaj for x in ["revolut", "rev"]):
            răspuns = "Poți plăti prin Revolut aici: https://revolut.me/liliancj2v"

        elif any(x in mesaj for x in ["paypal", "pp"]):
            răspuns = "Poți plăti prin PayPal aici: https://www.paypal.me/RomaniaQuiz"

        elif any(x in mesaj for x in ["card", "transfer", "iban"]):
            răspuns = "Poți face transfer la:\nIBAN: RO56BTRLRONCRT0CQ2528301\nTitular: Nume la alegere"

        elif any(x in mesaj for x in ["preț", "pret", "costă", "cât e"]):
            răspuns = "Prețul accesului este 70 RON."
            await start_follow_up_timer(message)

        elif any(x in mesaj for x in ["da", "ok", "sigur", "sunt interesat", "hai", "lets go", "confirm"]):
            răspuns = (
                "Perfect! Accesul costă **70 RON**.\n"
                "Poți plăti prin:\n"
                "- Revolut: https://revolut.me/liliancj2v\n"
                "- PayPal: https://www.paypal.me/RomaniaQuiz\n"
                "- Transfer: RO56BTRLRONCRT0CQ2528301\n"
                "Trimite dovada după ce plătești."
            )

        else:
            traducere = translator.translate(message.content, dest='ro')
            răspuns = (
                "Nu există răspuns pentru ce mi-ai scris (facem îmbunătățiri zilnice).\n"
                "Dacă întâmpini probleme, contactează Owner-ul serverului.\n\n"
                "Până atunci te pot ajuta cu:"
            )
            await message.channel.send(răspuns, view=HelpButtons(message.author))
            return

        await asyncio.sleep(1)
        await message.channel.send(răspuns)

        log = bot.get_channel(LOG_CHANNEL_ID)
        if log:
            await log.send(f"**[DM de la {message.author}]**\n**Mesaj:** {message.content}\n**Răspuns:** {răspuns}")

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
