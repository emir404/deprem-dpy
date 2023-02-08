import re
import json
from urllib.request import urlopen
from datetime import datetime
from bs4 import BeautifulSoup
import discord
from discord.ext import commands
import time

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!', description="Deprem Bilgilendirme", intents=intents)

global status
global settings

with open('settings.json') as f:
    settings = json.load(f)

@bot.event
async def on_ready():
    print(f'{bot.user.name} adlı bota giriş sağlandı.')
    #await send_messages(bot)

async def send_messages(channel):
    lastData = ""
    await channel.send(content="Veriler yükleniyor.")
    while status:
        time.sleep(15)
        data = get_kandilli_data()
        if lastData != data["date"]:
            lastData = data["date"]
        
            embedVar = discord.Embed(title="‼️‼️‼️‼️", color=0x00ff00)
            embedVar.set_author(name='Deprem Bilgilendirme - Kandilli Rasathanesi - @wearus')
            embedVar.add_field(name="🌐 Deprem Bölgesi", value=data["location"], inline=False)
            embedVar.add_field(name="🧱 Derinlik", value="{} km".format(data["depth"]), inline=False)
            embedVar.add_field(name="🪨 Büyüklük", value="{} ML".format(data["size"]["ml"]), inline=False)
            embedVar.add_field(name="⏱️ Zaman", value="<t:{}:R> - {}".format(data["timestamp"], data["date"]), inline=False)
            
            mention = settings["everyone"] and "@everyone" or settings["here"] and "@here"
            await channel.send(content="{}".format((data["size"]["ml"] > settings["size"]) and mention or ""), embed=embedVar)
        pass


@bot.command(name="başlat")
@commands.has_permissions(administrator=True)
async def start(ctx, channel: discord.TextChannel):
    try: 
        if channel:
            global status
            status = True
            await ctx.reply(content="Belirtilen kanalda bilgilendirme başlatıldı, durdurmak için !durdur <kanal>")
            await send_messages(channel)
        else:
            await ctx.reply(content="Belirtilen kanal bulunamadı.")
    except: pass

@bot.command(name="durdur")
@commands.has_permissions(administrator=True)
async def stop  (ctx, channel: discord.TextChannel):
    try: 
        if channel:
            global status
            status = False
            await ctx.reply(content="Belirtilen kanalda bilgilendirme durduruldu, başlatmak için !baslat <kanal>" )
        else:
            await ctx.reply(content="Belirtilen kanalda bilgilendirme bulunamadı.")
    except: pass

@bot.group(name='ayarlar', invoke_without_command=True)
@commands.has_permissions(administrator=True)
async def ayarlar(ctx):
    embed = discord.Embed()
    embed.set_author(name="Ayarlar")
    embed.add_field(name="everyone", value="<aç / kapat>", inline=False)
    embed.add_field(name="here", value="<aç / kapat>", inline=False)
    embed.add_field(name="büyüklük", value="<sayı>", inline=False)
    embed.set_footer(text="!ayarlar <ayar> <durum>")
    await ctx.reply(embed=embed)

@ayarlar.command()
@commands.has_permissions(administrator=True)
async def everyone(ctx, stat):
    try:
        if stat:
            everyoneStatus = stat.lower() == "aç" and True or False
            if settings["everyone"] != everyoneStatus:
                settings["everyone"] = everyoneStatus
                await ctx.reply(content="Everyone ayarı {}.".format(everyoneStatus and "açıldı" or "kapatıldı"))
            else:
                await ctx.reply(content="Everyone ayarı aynı, farklı bir değer girmelisin.")

        else:
            await ctx.reply(content="Bir durum belirtmen gerekiyor, <aç/kapat>")
    except: pass

@ayarlar.command()
@commands.has_permissions(administrator=True)
async def here(ctx, stat):
    try:
        if stat:
            hereStatus = stat.lower() == "aç" and True or False
            if settings["everyone"] != hereStatus:
                settings["here"] = hereStatus
                await ctx.reply(content="Here ayarı {}.".format(hereStatus and "açıldı" or "kapatıldı"))
            else:
                await ctx.reply(content="Here ayarı aynı, farklı bir değer girmelisin.")
        else:
            await ctx.reply(content="Bir durum belirtmen gerekiyor, <aç/kapat>")
    except: pass

@ayarlar.command(name="büyüklük")
@commands.has_permissions(administrator=True)
async def size(ctx, stat: int):
    try:
        if stat:
            settings["size"] = stat
            await ctx.reply(content=f"Büyüklük ayarı {stat} olarak değiştirildi.")
        else:
            await ctx.reply(content="Bir durum belirtmen gerekiyor, <sayı>")
    except: pass

@ayarlar.command(name="kaydet")
@commands.has_permissions(administrator=True)
async def save(ctx):
    try:
        await ctx.reply(content="``settings.json`` başarıyla kaydedildi.")
        with open('settings.json', 'w') as f:
            json.dump(settings, f)
    except: pass

def get_kandilli_data():
    array = []
    data = urlopen('http://www.koeri.boun.edu.tr/scripts/sondepremler.asp').read()
    soup = BeautifulSoup(data, 'html.parser')
    data = soup.find_all('pre')
    data = str(data).strip().split('--------------')[2]

    data = data.split('\n')
    data.pop(0)
    data.pop()
    data.pop()
    for index in range(len(data)):
        element = str(data[index].rstrip())
        element = re.sub(r'\s\s\s', ' ', element)
        element = re.sub(r'\s\s\s\s', ' ', element)
        element = re.sub(r'\s\s', ' ', element)
        element = re.sub(r'\s\s', ' ', element)
        Args=element.split(' ')
        location = Args[8]+element.split(Args[8])[len(element.split(Args[8])) - 1].split('İlksel')[0].split('REVIZE')[0]
        json_data = json.dumps({
            "id": index+1,
            "date": Args[0]+" "+Args[1],
            "timestamp": int(datetime.strptime(Args[0]+" "+Args[1], "%Y.%m.%d %H:%M:%S").timestamp()),
            "latitude": float(Args[2]),
            "longitude": float(Args[3]),
            "depth": float(Args[4]),
            "size": {
                "md": float(Args[5].replace('-.-', '0')),
                "ml": float(Args[6].replace('-.-', '0')),
                "mw": float(Args[7].replace('-.-', '0')) 
            },
            "location": location.strip(),
            "attribute": element.split(location)[1].split()[0]
        }, sort_keys=False)

        array.append(json.loads(json_data))
    return array[0]

bot.run('')
