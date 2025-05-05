import discord
from discord.ext import commands
import os
import asyncio
from googletrans import Translator
from discord.ui import Button, View

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

class FallbackButtons(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Button(label="Metode de plată", style=discord.ButtonStyle.primary, custom_id="plata"))
        self.add_item(Button(label="Cum primesc accesul", style=discord.ButtonStyle.primary, custom_id="acces"))
        self.add_item(Button(label="Întâmpin dificultăți (Owner-ul te va contacta)", style=discord.ButtonStyle.secondary, custom_id="owner"))

@bot.event
async def on_ready():
    print(f"Botul este online ca {bot.user}")

@bot.event
async def on_interaction(interaction):
    if not interaction.type == discord.InteractionType.component:
        return

    if interaction.data["custom_id"] == "plata":
        await interaction.response.send_message(
            "Poți plăti prin:\n- Revolut: https://revolut.me/liliancj2v\n- PayPal: https://www.paypal.me/RomaniaQuiz\n- Card (transfer): IBAN: RO56BTRLRONCRT0CQ2528301",
            ephemeral=True
        )
    elif interaction.data["custom_id"] == "acces":
        await interaction.response.send_message(
            "Primești acces imediat pe server după confirmarea plății. Asigură-te că ești pe server!",
            ephemeral=True
        )
    elif interaction.data["custom_id"] == "owner":
        await interaction.response.send_message(
            "Owner-ul serverului va fi notificat și te va contacta cât de curând.",
            ephemeral=True
        )

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if isinstance(message.channel, discord.DMChannel):
        mesaj = message.content.lower()
        răspuns = None
        lang = "ro"

        try:
            traducere = translator.translate(message.content, dest='ro')
            mesaj_tradus = traducere.text.lower()
            if traducere.src == "en":
                lang = "en"
        except:
            mesaj_tradus = mesaj

        # Salut simplu
        if mesaj.strip() in ["salut", "sall", "buna", "bună", "alo", "hei", "hey", "hello", "hi"]:
            răspuns = "Salut! Cu ce te pot ajuta? Ești interesat de achiziționarea full accesului?"

        elif any(x in mesaj_tradus for x in ["am plătit", "gata", "am trimis", "am dat"]):
            await message.channel.send("Trimite-mi te rog o dovadă de plată (un screenshot).")
            return

        elif any(x in mesaj_tradus for x in [
            "acces", "vreau acces", "cumpăr", "achiziționez", "dă-mi acces",
            "vreau să cumpăr", "cum cumpăr", "how much", "price", "buy"
        ]):
            răspuns = "Cu ce metodă plătești? Revolut, PayPal sau transfer cu cardul. (Accesul costă 70 RON)"
            await start_follow_up_timer(message)

        elif "revolut" in mesaj_tradus or "rev" in mesaj_tradus:
            răspuns = "Poți plăti prin Revolut aici: https://revolut.me/liliancj2v"

        elif "paypal" in mesaj_tradus or "pp" in mesaj_tradus:
            răspuns = "Poți plăti prin PayPal aici: https://www.paypal.me/RomaniaQuiz"

        elif "iban" in mesaj_tradus or "card" in mesaj_tradus or "transfer" in mesaj_tradus:
            răspuns = "Poți face transfer la:\nIBAN: RO56BTRLRONCRT0CQ2528301\nTitular: Nume la alegere"

        elif "preț" in mesaj_tradus or "pret" in mesaj_tradus or "cât costă" in mesaj_tradus:
            răspuns = "Prețul accesului este 70 RON."
            await start_follow_up_timer(message)

        elif "ajutor" in mesaj_tradus or "help" in mesaj_tradus:
            răspuns = "Te pot ajuta cu:\n- Prețuri\n- Metode de plată\n- Livrare\nScrie ce te interesează."

        else:
            text_fallback = (
                "Nu există răspuns pentru ce mi-ai scris (facem îmbunătățiri zilnice). "
                "Dacă întâmpini probleme, contactează Owner-ul serverului. "
                "Până atunci, te pot ajuta cu:"
            )
            await message.channel.send(text_fallback, view=FallbackButtons())
            return

        if lang == "en":
            try:
                traducere = translator.translate(răspuns, dest="en")
                răspuns = traducere.text
            except:
                pass

        await message.channel.send(răspuns)

        # Log
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(
                f"**[DM de la {message.author}]**\n**Mesaj:** {message.content}\n**Răspuns:** {răspuns}"
            )

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
