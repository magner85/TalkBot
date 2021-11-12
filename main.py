import asyncio
import discord_command
import discord
import asyncio
import fileManager
import time
import os
import json

def delete_file(file:str):
    os.remove(file)

def download(url:str, name:str):
    for file in all_files():
        if file == name:
            return False
    f=open(r'saved\\' + name,"wb")
    ufr = requests.get(url)
    f.write(ufr.content)
    f.close()
    return True

def all_files():
    return os.listdir('saved')

def load_binding():
    try:
        with open('binding.json', 'r') as file:
            json_data = json.load(file)
            file.close()
        return json_data
    except:
        return None

def find_binding(text:str):
    json_file = load_binding()
    if json_file is None:
        return None
    for i in json_file:
        if i['text'] == text:
            return i['name']
    return None

def upload_binding(text:str, name_file:str):
    json_file = load_binding()
    if json_file is None:
        json_file = [{
            'text': text,
            'name':name_file
        }]
    else:
        if not find_binding(text) is None:
            return
        json_file.append({
            'text': text,
            'name': name_file
        })
    with open('binding.json', 'w') as file:
        json.dump(json_file, file)
        file.close()

def del_binding(text:str):
    json_file = load_binding()
    if json_file is None:
        return False
    for i in json_file:
        if i['text'] == text:
            json_file.remove(i)
            with open('binding.json', 'w') as file:
                json.dump(json_file, file)
                file.close()
            return True
    return False


def load_vol():
    try:
        with open('volume.json', 'r') as file:
            json_data = json.load(file)
            file.close()
        return json_data
    except:
        return None

def find_vol(name:str):
    json_file = load_vol()
    if json_file is None:
        return None
    for i in json_file:
        if i['name'] == name:
            return i['vol']
    return None

def upload_vol(name:str, volume:int):
    json_file = load_vol()
    if json_file is None:
        json_file = [{
            'name': name,
            'vol':volume
        }]
    else:
        for i in json_file:
            if i['name'] == name:
                json_file.remove(i)
                break
        json_file.append({
            'name': name,
            'vol':volume
        })
    with open('volume.json', 'w') as file:
        json.dump(json_file, file)
        file.close()

def del_vol(name:str):
    json_file = load_vol()
    if json_file is None:
        return False
    for i in json_file:
        if i['name'] == name:
            json_file.remove(i)
            with open('volume.json', 'w') as file:
                json.dump(json_file, file)
                file.close()
            return True
    return False
class MyClient:
    dialog = []
    playlist = {}
    playing = {}
    ffmpeg = "C:/ffmpeg/bin/ffmpeg"
    def __init__(self, token:str, msg_handler):
        self.token = token
        self.bot = discord.Client()
        @self.bot.event
        async def on_message(message):
            if message.author.bot == True:
                return
            if self.dialog.count(message.author) != 0:
                self.delete_dialog(message.author)
            else:
                await msg_handler(bot=self, message=message)

    async def start(self):
        asyncio.create_task(self.bot.start(self.token))
        await self.bot.wait_until_ready()

    async def send(self, channel:discord.TextChannel, text:str, delete_after:float=None):
        if text == '':
            return
        await channel.send(text, delete_after=delete_after)

    async def logout(self):
        await asyncio.wait_for(self.bot.logout(), timeout=60)

    async def new_dialog(self, name:str, timeout:int):
        self.dialog.append(name)
        async def delete():
            await asyncio.sleep(timeout)
            if self.dialog.count(name) != 0:
                self.delete_dialog(name)
        asyncio.create_task(delete())

    def delete_dialog(self, name:str):
        self.dialog.remove(name)

    async def wait_msg(self, author:str, timeout:int):
        await self.new_dialog(author, timeout)
        msg = await self.bot.wait_for('message', check=lambda m: m.author == author)
        if self.dialog.count(author) == 0:
            msg = None
        if msg == None:
            msg.content = ''
        elif msg.content == 'break':
            msg.content = ''
        return msg

    async def append_playlist(self, channel:discord.VoiceChannel, file):
        if not self.playlist.__contains__(channel.id) or len(self.playlist[channel.id]) == 0:
            self.playlist[channel.id] = [file]
            async def pl():
                t = time.time()
                retry = True
                while retry:
                    retry = False
                    try:
                        voice_channel = await channel.connect()
                    except:
                        if t < time.time() - 300:
                            return
                        else:
                            retry = True
                            await asyncio.sleep(1)
                await self.play(voice_channel, channel)
                await voice_channel.disconnect()
            asyncio.create_task(pl())
        else:
            self.playlist[channel.id].append(file)


    async def play(self, voice_channel:discord.VoiceClient, channel:discord.VoiceChannel):
        while len(self.playlist[channel.id]) != 0:
            file = self.playlist[channel.id][0]
            if not voice_channel.is_connected():
                await voice_channel.connect(reconnect=True)
            self.playing[channel.id] = voice_channel
            PCM = discord.FFmpegPCMAudio(executable=self.ffmpeg, source=file)
            if file[:5] == 'saved':
                name = file[6:]
                if fileManager.find_vol(name) != None:
                    PCM = discord.PCMVolumeTransformer(original=PCM, volume=fileManager.find_vol(name) / 50)
            voice_channel.play(PCM,
                                after=None)
            while voice_channel.is_playing():
                if self.playing[channel.id] == None:
                    voice_channel.stop()
                    await voice_channel.disconnect()
                    self.playlist[channel.id].clear()
                    return
                await asyncio.sleep(0.05)
            if file[:3] == 'tmp':
                fileManager.delete_file(file)
            self.playlist[channel.id].pop(0)
        self.playing[channel.id] = None

async def main():
    bot = DiscordApi.MyClient('NzMzMDA1MDYyNDQ3ODI1MDA3.Xw82KQ.zs0WjdpyyyoN6chxt5Euhu1nTno', discord_command.default_handler)
    await bot.start()
    print('ready')
    while True:
        await asyncio.sleep(1000)

asyncio.run(main())