import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True
intents.dm_messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

LOG_CHANNEL_ID = 1367958714379927693  # Înlocuiește cu ID-ul canalului tău de log dacă vrei

@bot.event
async def on_ready():
    print(f"Botul este online ca {bot.user}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if isinstance(message.channel, discord.DMChannel):
        mesaj = message.content.lower()
        răspuns = None

        if any(cuvânt in mesaj for cuvânt in ["salut", "bună", "hello", "hei", "hey"]):
            răspuns = "Salut! Cu ce te pot ajuta?"
        elif any(expr in mesaj for expr in [
            "acces", "vreau acces", "vreau să cumpăr", "achiziționez",
            "vreau să achiziționez", "cum cumpăr", "pot cumpăra",
            "vreau să iau", "dă-mi acces", "doresc acces"
        ]):
            răspuns = "Cu ce metodă plătești? Revolut, PayPal sau transfer cu cardul. (Accesul costă 70 RON)"
        elif any(cuvânt in mesaj for cuvânt in ["revolut", "rev", "Rev"]):
            răspuns = "Poți plăti prin Revolut aici: https://revolut.me/liliancj2v"
        elif any(cuvânt in mesaj for cuvânt in ["paypal", "pp", "PayPal"]):
            răspuns = "Poți plăti prin PayPal aici: https://www.paypal.me/RomaniaQuiz"
        elif any(cuvânt in mesaj for cuvânt in ["card", "transfer", "iban", "IBAN"]):
            răspuns = "Poți face transfer la:\nIBAN: RO56BTRLRONCRT0CQ2528301\nTitular: Nume la alegere"
        elif "preț" in mesaj or "pret" in mesaj or "cât costă" in mesaj:
            răspuns = "Prețul serviciului este 70 RON."
        elif "ajutor" in mesaj or "help" in mesaj:
            răspuns = "Te pot ajuta cu:\n- Prețuri\n- Metode de plată\n- Livrare\nScrie ce te interesează."
        else:
            răspuns = "Îmi pare rău, nu am înțeles. Scrie 'ajutor' pentru opțiuni."

        await message.channel.send(răspuns)

        canal_log = bot.get_channel(LOG_CHANNEL_ID)
        if canal_log:
            await canal_log.send(
                f"**[DM de la {message.author}]**\n**Mesaj:** {message.content}\n**Răspuns:** {răspuns}"
            )

    await bot.process_commands(message)

bot.run(os.getenv("TOKEN"))
