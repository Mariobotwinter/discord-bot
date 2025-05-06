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

class HelpButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Metode de plată", style=discord.ButtonStyle.primary)
    async def metode_plata(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "Poți plăti prin:\n- Revolut: https://revolut.me/liliancj2v\n- PayPal: https://www.paypal.me/RomaniaQuiz\n- Transfer bancar: IBAN: RO56BTRLRONCRT0CQ2528301",
            ephemeral=True)

    @discord.ui.button(label="Cum primesc accesul", style=discord.ButtonStyle.primary)
    async def cum_primesc(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            "După confirmarea plății, trimite un screenshot cu dovada, iar botul îți va oferi accesul automat pe server.",
            ephemeral=True)

    @discord.ui.button(label="Întâmpin dificultăți", style=discord.ButtonStyle.danger)
    async def dificultati(self, interaction: discord.Interaction, button: discord.ui.Button):
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            await log_channel.send(f"{interaction.user.mention} a apăsat pe 'Întâmpin dificultăți'.")
        await interaction.response.send_message("Owner-ul serverului va fi notificat să te contacteze.", ephemeral=True)

@bot.command()
async def buton_acces(ctx):
    view = discord.ui.View()
    async def callback(interaction):
        try:
            await interaction.user.send("Salut! Am văzut că ești interesat de achiziționare. Accesul costă 70 de RON! Scrie cu ce metodă vrei să plătești și se rezolvă!")
            try:
                await interaction.response.send_message("Ți-am trimis un mesaj în privat!", ephemeral=True)
            except discord.errors.NotFound:
                pass
        except:
            try:
                await interaction.response.send_message("Nu ți-am putut trimite mesaj. Activează mesajele private.", ephemeral=True)
            except discord.errors.NotFound:
                pass

    button = discord.ui.Button(label="Vreau acces", style=discord.ButtonStyle.success)
    button.callback = callback
    view.add_item(button)
    await ctx.send("Dacă ești interesat, apasă pe butonul de mai jos sau mesaj în privat.", view=view)

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

        if any(cuv in mesaj for cuv in ["salut", "sall", "hello", "hei", "hey", "buna", "bună"]):
            răspuns = "Salut! Cu ce te pot ajuta? Ești interesat de achiziționarea full accesului?"

        elif any(cuv in mesaj for cuv in ["da", "ok", "sunt", "vreau", "vreau sa cumpar", "interesat", "intereseaza", "sunt interesat"]):
            răspuns = "Accesul costă 70 RON. Cu ce metodă dorești să plătești? Revolut, PayPal sau transfer bancar?"
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

        if răspuns:
            await message.channel.send(răspuns)
            log_channel = bot.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                await log_channel.send(f"**[DM de la {message.author}]**\n**Mesaj:** {message.content}\n**Răspuns:** {răspuns}")
        else:
            text = (
                "Nu există răspuns pentru ce mi-ai scris (facem îmbunătățiri zilnice).\n"
                "Dacă întâmpini probleme, contactează Owner-ul serverului.\n\n"
                "Până atunci te pot ajuta cu:"
            )
            await message.channel.send(text, view=HelpButtons())

        if user_id in pending_users:
            pending_users[user_id]["task"].cancel()
            del pending_users[user_id]

    await bot.process_commands(message)

async def start_follow_up_timer(message):
    user_id = message.author.id
    if user_id in pending_users:
        pending_users[user_id]["task"].cancel()

    async def timer():
        try:
            await asyncio.sleep(600)
            await message.channel.send("Mai ești aici? Pot să te ajut cu altceva?")
        except asyncio.CancelledError:
            pass

    task = asyncio.create_task(timer())
    pending_users[user_id] = {"task": task}

bot.run(os.getenv("TOKEN"))
