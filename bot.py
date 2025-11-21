import discord
from discord.ext import commands
from logic import FusionBrainAPI
from config import TOKEN, API_KEY, SECRET_KEY
import os

# Bot başlatma
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.command(name='start')
async def start(ctx):
    help_message = (
        "Merhaba! 👋\n"
        "Ben, yazdığınız metne göre görüntü üretebilen bir botum!\n"
        "Bana sadece bir açıklama yazın, sizin için resmi oluşturayım. 🎨"
    )
    await ctx.send(help_message)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Komutları işleme
    if message.content.startswith(bot.command_prefix):
        await bot.process_commands(message)
        return

    async with message.channel.typing():

        notify_message = await message.channel.send("Görüntü üretiliyor... ⏳")

        prompt = message.content

        api = FusionBrainAPI('https://api-key.fusionbrain.ai/', API_KEY, SECRET_KEY)

        pipeline_id = api.get_pipeline()
        if pipeline_id is None:
            await notify_message.edit(content="❌ Pipeline bulunamadı.")
            return

        uuid = api.generate(prompt, pipeline_id)
        images = api.check_generation(uuid)

        if not images:
            await notify_message.edit(content="❌ Görüntü oluşturulamadı.")
            return

        file_path = "generated_image.png"   # PNG kaydediyoruz, sorun yok
        api.save_image(images[0], file_path)

        await notify_message.delete()

        # Görseli gönder
        with open(file_path, "rb") as photo:
            await message.channel.send(file=discord.File(photo, "generated_image.png"))

        os.remove(file_path)

bot.run(TOKEN)
