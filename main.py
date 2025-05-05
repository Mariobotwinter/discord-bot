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
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(label="Metode de plată", style=discord.ButtonStyle.blurple, custom_id="plata"))
        self.add_item(Button(label="Cum primesc accesul", style=discord.ButtonStyle.blurple, custom_id="acces"))
        self.add_item(Button(label="Întâmpin dificultăți", style=discord.ButtonStyle.danger, custom_id="problema"))

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

        if any(cuv in mesaj for cuv in ["am plătit", "am platit", "gata", "am trimis", "am dat"]):
            await message.channel.send("Trimite-mi te rog o dovadă de plată (un screenshot).")
            return

        salutari = ["salut", "bună", "buna", "hei", "hey", "sall", "sal", "salve"]
        confirmari = ["da", "ok", "bine", "sigur", "hai", "vreau", "let's go", "yes"]

        if any(cuv in mesaj for cuv in salutari):
            răspuns = "Salut! Cu ce te pot ajuta? Ești interesat de achiziționarea full accesului?"

        elif any(cuv in mesaj for cuv in confirmari):
            răspuns = "Perfect! Accesul costă 70 RON. Cu ce metodă vrei să plătești? (Revolut, PayPal sau transfer card)"

        elif any(expr in mesaj for expr in ["acces", "vreau acces", "cumpăr", "cum cumpăr", "iau", "dă-mi acces", "achiziționez"]):
            răspuns = "Cu ce metodă plătești? Revolut, PayPal sau transfer cu cardul. (Accesul costă 70 RON)"
            await start_follow_up_timer(message)

        elif any(cuv in mesaj for cuv in ["revolut", "rev"]):
            răspuns = "Poți plăti prin Revolut aici: https://revolut.me/liliancj2v"

        elif any(cuv in mesaj for cuv in ["paypal", "pp"]):
            răspuns = "Poți plăti prin PayPal aici: https://www.paypal.me/RomaniaQuiz"

        elif any(cuv in mesaj for cuv in ["card", "transfer", "iban"]):
            răspuns = "Poți face transfer la:"
IBAN: RO56BTRLRONCRT0CQ2528301
Titular: Nume la alegere"

        elif "preț" in mesaj or "pret" in mesaj or "cât costă" in mesaj:
            răspuns = "Prețul accesului este 70 RON."
            await start_follow_up_timer(message)

        else:
            await message.channel.send(
                "Nu există răspuns pentru ce mi-ai scris (facem îmbunătățiri zilnice)."
                
                "Dacă întâmpini probleme, contactează Owner-ul serverului."

                "Până atunci te pot ajuta cu:"
            )
            await message.channel.send(view=HelpButtons())
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

@bot.event
async def on_interaction(interaction):
    if not interaction.type.name == "component":
        return

    if interaction.data["custom_id"] == "plata":
        await interaction.response.send_message("Metode disponibile: Revolut, PayPal, transfer cu cardul.", ephemeral=True)

    elif interaction.data["custom_id"] == "acces":
        await interaction.response.send_message("După plată și dovadă, primești automat acces pe server.", ephemeral=True)

    elif interaction.data["custom_id"] == "problema":
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(f"**[Notificare]** {interaction.user.mention} întâmpină dificultăți.")
        await interaction.response.send_message("Un admin a fost notificat și te va contacta.", ephemeral=True)

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
