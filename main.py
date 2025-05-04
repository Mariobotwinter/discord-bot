import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True
intents.dm_messages = True
intents.members = True  # ca să poată da roluri

bot = commands.Bot(command_prefix="!", intents=intents)

LOG_CHANNEL_ID = 1367958714379927693
SERVER_ID = 1324363465745240118
ROL_ID = 1327354131181994004

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

        # Mesaj text: confirmare plată
        if any(cuv in mesaj for cuv in ["am plătit", "am platit", "gata", "am trimis", "am dat"]):
            răspuns = "Trimite-mi te rog o dovadă de plată (un screenshot)."
            await message.channel.send(răspuns)
            return

        # Răspunsuri automate clasice
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

        # Trimitere log text
        canal_log = bot.get_channel(LOG_CHANNEL_ID)
        if canal_log:
            await canal_log.send(f"**[DM de la {message.author}]**\n**Mesaj:** {message.content}\n**Răspuns:** {răspuns}")

    # Dacă mesajul conține o imagine (dovadă de plată)
    if isinstance(message.channel, discord.DMChannel) and message.attachments:
        for attachment in message.attachments:
            if attachment.content_type and attachment.content_type.startswith("image/"):
                log_channel = bot.get_channel(LOG_CHANNEL_ID)
                if log_channel:
                    await log_channel.send(f"**Dovadă de plată de la {message.author}:**")
                    await log_channel.send(attachment.url)

                # Adăugăm rolul pe server
                guild = bot.get_guild(SERVER_ID)
                if guild:
                    member = guild.get_member(message.author.id)
                    if member:
                        rol = guild.get_role(ROL_ID)
                        if rol:
                            await member.add_roles(rol)
                            await message.channel.send("Mulțumesc! Ți-am acordat accesul.")
                        else:
                            await message.channel.send("Nu am găsit rolul.")
                    else:
                        await message.channel.send("Te rog să intri pe serverul nostru pentru a-ți oferi accesul.")
                break

    await bot.process_commands(message)

bot.run(os.getenv("TOKEN"))
