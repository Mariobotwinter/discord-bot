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
                    await log_channel.send(f"**Dovadă de plată de la {message.author}:**")
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

        if any(cuv in mesaj for cuv in ["salut", "sall", "bună", "buna", "hello", "hei", "hey"]):
            răspuns = "Salut! Cu ce te pot ajuta? Ești interesat de achiziționarea full accesului?"

        elif any(expr in mesaj for expr in [
            "acces", "vreau acces", "vreau să cumpăr", "achiziționez",
            "vreau să achiziționez", "cum cumpăr", "pot cumpăra",
            "vreau să iau", "dă-mi acces", "doresc acces"
        ]):
            răspuns = "Cu ce metodă plătești? Revolut, PayPal sau transfer cu cardul. (Accesul costă 70 RON)"
            await start_follow_up_timer(message)

        elif any(cuv in mesaj for cuv in ["revolut", "rev"]):
            răspuns = "Poți plăti prin Revolut aici: https://revolut.me/liliancj2v"

        elif any(cuv in mesaj for cuv in ["paypal", "pp"]):
            răspuns = "Poți plăti prin PayPal aici: https://www.paypal.me/RomaniaQuiz"

        elif any(cuv in mesaj for cuv in ["card", "transfer", "iban"]):
            răspuns = "Poți face transfer la:\nIBAN: RO56BTRLRONCRT0CQ2528301\nTitular: Nume la alegere"

        elif "preț" in mesaj or "pret" in mesaj or "cât costă" in mesaj:
            răspuns = "Prețul accesului este 70 RON."
            await start_follow_up_timer(message)

        elif any(cuv in mesaj for cuv in ["da", "ok", "sigur", "desigur", "normal", "sunt interesat", "hai", "vreau", "confirm", "lets go", "go"]):
            răspuns = (
                "Perfect! Accesul costă **70 RON**.\n"
                "Poți plăti prin:\n"
                "- Revolut: https://revolut.me/liliancj2v\n"
                "- PayPal: https://www.paypal.me/RomaniaQuiz\n"
                "- Transfer bancar: RO56BTRLRONCRT0CQ2528301\n"
                "Trimite dovada după ce plătești."
            )

        else:
            traducere = translator.translate(message.content, dest='ro')
            răspuns = (
                "Nu există răspuns pentru ce mi-ai scris (facem îmbunătățiri zilnice).\n"
                "Dacă întâmpini probleme, contactează Owner-ul serverului.\n\n"
                "Până atunci te pot ajuta cu:\n"
                "**• Metode de plată**\n"
                "**• Cum primesc accesul**\n"
                "**• Întâmpin dificultăți** – Owner-ul te va contacta."
            )

        await asyncio.sleep(1)
        await message.channel.send(răspuns)

        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(f"**[DM de la {message.author}]**\n**Mesaj:** {message.content}\n**Răspuns:** {răspuns}")

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
