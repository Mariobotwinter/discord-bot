import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.message_content = True
intents.dm_messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

LOG_CHANNEL_ID = 1367958714379927693  # ← Înlocuiește cu ID-ul canalului tău de log

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

        if any(cuvânt in mesaj for cuvânt in ["salut", "bună", "buna", "hello", "hey", "hei"]):
            răspuns = "Salut! Cu ce te pot ajuta?"
            await message.channel.send(răspuns)

        elif any(expr in mesaj for expr in [
            "acces", "vreau acces", "vreau să cumpăr", "vreau sa cumpar",
            "achiziționez", "achizitionez", "vreau să achiziționez", "vreau sa achizitionez",
            "cum cumpăr", "cum pot cumpăra", "pot cumpăra", "vreau să iau",
            "aș vrea să cumpăr", "as vrea sa cumpar", "cum iau acces", "dă-mi acces", "da-mi acces",
            "doresc acces", "doresc să cumpăr", "doresc sa cumpar"
        ]):
            răspuns = "Cu ce metodă plătești? Revolut, PayPal sau transfer cu cardul. (Accesul costă 70 RON)"
            await message.channel.send(răspuns)

        elif any(cuvânt in mesaj for cuvânt in ["revolut", "rev"]):
            răspuns = "Poți plăti prin Revolut aici: https://revolut.me/exemplu"
            await message.channel.send(răspuns)

        elif any(cuvânt in mesaj for cuvânt in ["paypal", "pp"]):
            răspuns = "Poți plăti prin PayPal aici: https://paypal.me/exemplu"
            await message.channel.send(răspuns)

        elif any(cuvânt in mesaj for cuvânt in ["card", "transfer", "prin iban"]):
            răspuns = "Pentru transfer cu cardul sau IBAN, te rog să ceri detalii suplimentare. Vom reveni imediat cu informațiile."
            await message.channel.send(răspuns)

        elif "preț" in mesaj or "pret" in mesaj or "cât costă" in mesaj or "cat costa" in mesaj:
            răspuns = "Prețul serviciului este 70 RON."
            await message.channel.send(răspuns)

        elif "servicii" in mesaj or "ce oferi" in mesaj or "ofertă" in mesaj or "oferta" in mesaj:
            răspuns = "Ofer servicii de automatizare, configurare Discord și suport tehnic."
            await message.channel.send(răspuns)

        elif "cum pot plăti" in mesaj or "modalitate de plată" in mesaj or "modalitate de plata" in mesaj:
            răspuns = "Poți plăti prin Revolut sau PayPal. Spune-mi ce preferi."
            await message.channel.send(răspuns)

        elif "livrare" in mesaj or "cât durează" in mesaj or "cat dureaza" in mesaj:
            răspuns = "Livrarea se face în 1-2 ore după confirmarea plății."
            await message.channel.send(răspuns)

        elif "factură" in mesaj or "factura" in mesaj or "bon" in mesaj or "dovadă" in mesaj or "dovada" in mesaj:
            răspuns = "Desigur, pot oferi factură la cerere. Te rog să specifici după plată."
            await message.channel.send(răspuns)

        elif "sigur" in mesaj or "este sigur" in mesaj or "încredere" in mesaj or "incredere" in mesaj:
            răspuns = "Desigur! Ofer suport complet și am clienți mulțumiți. Poți verifica recenziile."
            await message.channel.send(răspuns)

        elif "cum primesc" in mesaj or "ce primesc" in mesaj:
            răspuns = "Primești totul pe Discord, imediat după confirmarea plății."
            await message.channel.send(răspuns)

        elif "ajutor" in mesaj or "help" in mesaj:
            răspuns = "Te pot ajuta cu:
- Prețuri
- Modalități de plată
- Servicii oferite
- Livrare
Scrie ce te interesează."
            await message.channel.send(răspuns)

        else:
            răspuns = "Îmi pare rău, nu am înțeles. Scrie 'ajutor' pentru opțiuni."
            await message.channel.send(răspuns)

        canal_log = bot.get_channel(LOG_CHANNEL_ID)
        if canal_log:
            await canal_log.send(
                f"**[DM de la {message.author}]**
"
                f"**Mesaj:** {message.content}
"
                f"**Răspuns:** {răspuns}"
            )

try:
    bot.run(os.getenv("TOKEN"))
except Exception as e:
    print(f"Eroare la pornirea botului: {e}")
