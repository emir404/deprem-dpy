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

description = 'Deprem Güncelleme Botu'

bot = commands.Bot(command_prefix='!', description=description, intents=intents)
lastData = None

@bot.event
async def on_ready():
    print(f'{bot.user.name} adlı bota giriş sağlandı.')
    channel = bot.get_channel(1072336930571825163)
    await channel.send(content="Veriler yükleniyor.")
    while True:
        time.sleep(15)
        data = get_kandilli_data()
        if lastData != data["timestamp"]:
          lastData = data["timestamp"]
          print(data["location"], data["date"], data["size"]["ml"])
          embedVar = discord.Embed(title="‼️‼️‼️‼️", color=0x00ff00)
          embedVar.set_author(name='Deprem Bilgilendirme - Kandilli Rasathanesi - @wearus')
          embedVar.add_field(name="🌐 Deprem Bölgesi", value=data["location"], inline=False)
          embedVar.add_field(name="🧱 Derinlik", value="{} km".format(data["depth"]), inline=False)
          embedVar.add_field(name="🪨 Büyüklük", value="{} ML".format(data["size"]["ml"]), inline=False)
          embedVar.add_field(name="⏱️ Zaman", value="<t:{}:R> - {}".format(data["timestamp"], data["date"]), inline=False)
          await channel.send(content="{}".format(data["size"]["ml"] > 5 and "@everyone" or ""), embed=embedVar)

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
