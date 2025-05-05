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
user_data = {}

@bot.event
async def on_ready():
    print(f"Botul este online ca {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    user_id = message.author.id
    username = message.author.name

    # Inițializare
    if user_id not in user_data:
        user_data[user_id] = {
            "last_msg": "",
            "interactions": 0
        }

    user_data[user_id]["last_msg"] = message.content
    user_data[user_id]["interactions"] += 1

    # Dacă e poză (fără text sau cu)
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
                            await message.channel.send("Mulțumesc pentru dovadă de plată! Ți-am oferit accesul.")
                        else:
                            await message.channel.send("Rolul nu a fost găsit.")
                    else:
                        await message.channel.send("Te rog să fii pe server pentru a-ți oferi accesul.")
                return

    if isinstance(message.channel, discord.DMChannel):
        mesaj = message.content.lower()
        răspuns = None
        lang = 'ro'

        # Detectare limbă + traducere
        try:
            traducere = translator.translate(message.content, dest='ro')
            mesaj_tradus = traducere.text.lower()
            if traducere.src == "en":
                lang = "en"
        except:
            mesaj_tradus = mesaj

        # Text: am plătit -> cere dovadă
        if any(x in mesaj_tradus for x in ["am plătit", "gata", "am trimis", "am dat"]):
            await message.channel.send("Trimite-mi te rog o dovadă de plată (un screenshot).")
            return

        # Salut
        if any(x in mesaj_tradus for x in ["salut", "bună", "hello", "hei", "hey"]):
            răspuns = f"Salut {username}! Cu ce te pot ajuta?"

        # Dorință acces / cumpărare
        elif any(x in mesaj_tradus for x in [
            "acces", "vreau acces", "cumpăr", "achiziționez", "dă-mi acces",
            "vreau să cumpăr", "cum cumpăr", "how much", "price", "buy"
        ]):
            răspuns = "Cu ce metodă plătești? Revolut, PayPal sau transfer cu cardul. (Accesul costă 70 RON)"
            await start_follow_up_timer(message)

        # Metode plată
        elif "revolut" in mesaj_tradus or "rev" in mesaj_tradus:
            răspuns = "Poți plăti prin Revolut aici: https://revolut.me/liliancj2v"

        elif "paypal" in mesaj_tradus or "pp" in mesaj_tradus:
            răspuns = "Poți plăti prin PayPal aici: https://www.paypal.me/RomaniaQuiz"

        elif "iban" in mesaj_tradus or "card" in mesaj_tradus or "transfer" in mesaj_tradus:
            răspuns = "Poți face transfer la:\nIBAN: RO56BTRLRONCRT0CQ2528301\nTitular: Nume la alegere"

        # Preț
        elif "preț" in mesaj_tradus or "pret" in mesaj_tradus or "cât costă" in mesaj_tradus:
            răspuns = "Prețul accesului este 70 RON."
            await start_follow_up_timer(message)

        # Ajutor
        elif "ajutor" in mesaj_tradus or "help" in mesaj_tradus:
            răspuns = "Te pot ajuta cu:\n- Prețuri\n- Metode de plată\n- Livrare\nScrie ce te interesează."

        else:
            răspuns = "Îmi pare rău, nu am înțeles. Scrie 'ajutor' pentru opțiuni."

        if lang == "en":
            try:
                traducere = translator.translate(răspuns, dest="en")
                răspuns = traducere.text
            except:
                pass

        await message.channel.send(răspuns)

        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(
                f"**[DM de la {message.author}]**\n**Mesaj:** {message.content}\n**Răspuns:** {răspuns}"
            )

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
