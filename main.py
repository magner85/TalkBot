import discord
import asyncio
import time
import os
import json
import random
import re
import parametrs
import subprocess
import requests

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
                if find_vol(name) != None:
                    PCM = discord.PCMVolumeTransformer(original=PCM, volume=find_vol(name) / 50)
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
                delete_file(file)
            self.playlist[channel.id].pop(0)
        self.playing[channel.id] = None

    def add_handler(self, coro, text:str):
        self.dctext.append(text)
        self.dc.append(coro)

class MsgParser:
    prefix = '$'
    voice_command = {
        r'\[v \d{1,3}\]': 'volume',
        r'\[p \d{1,3}\]': 'pitch_voice',
        r'\[s \d{1,3}\]': 'voice_speed'
    }
    text_command = {
        r'\[vc [^\]]{1,50}\]':'voice',
        r'\[ch [^\]]{1,50}\]':'channel'
    }
    voice_file = r'\[f [^\]]{1,20}\]'
    dc = []
    dctext = []
    
    def __init__(self, message:discord.message, client:MyClient):
        text = message.content
        if text[0] == self.prefix:
            text = text[1:]
            self.is_talk = True
            self.channel = None
            self.file_mas = []
            while len(text) != 0:
                f = re.search(self.voice_file, text)
                if f:
                    filename = f[0][3:-1]
                    t = text[:f.start()]
                    text = text[f.end():]
                else:
                    filename = None
                    t = text
                    text = []
                out_par = parametrs.Talker()
                for pattern in self.voice_command.keys():
                    val = re.search(pattern, t)
                    if val:
                        num = int(re.search(r'\d{1,3}', val[0]).group())
                        if num <= 100 and num > 0:
                            out_par.set_par(par=self.voice_command[pattern], value=num)
                        t = t[:val.start()] + t[val.end():]
                for pattern in self.text_command.keys():
                    val = re.search(pattern, t)
                    if val:
                        txt = val[0][4:-1]
                        if self.text_command[pattern] == 'voice':
                            out_par.voice = txt
                        if self.text_command[pattern] == 'channel':
                            for channels in message.guild.voice_channels:
                                if channels.name == txt:
                                    self.channel = channels
                                    break
                        t = t[:val.start()] + t[val.end():]
                if t != '':
                    name = message.author.name
                    while os.listdir(os.path.abspath('tmp')).count(name):
                        name += '!'
                    out_par.text = t
                    Talker(out_par).run(name)
                    self.file_mas.append('tmp\\'+name)
                if filename is None:
                    break
                for f in all_files():
                    if f == filename:
                        self.file_mas.append('saved\\'+filename)
                        break

        else:
            self.is_talk = False
            try:
                i = 0
                if self.dctext == []:
                    discord_command.append_handler(self)
                for cmd in self.dctext:
                    if cmd == text:
                        asyncio.create_task(self.dc[i](client, message= message))
                        break
                    i += 1
            except:
                pass

def append_handler(parser:MsgParser):
    async def stop(bot, message):
        bot.playing[message.author.voice.channel.id] = None
        await message.delete()
    parser.add_handler(stop, 'stop')

    async def voices(bot, message):
        voices = Talker(parametrs.Talker()).get_voices()
        text = ''
        for i in voices:
            text += i + '\n'
        await bot.send(message.channel, text, delete_after=180)
        await message.delete()
    parser.add_handler(voices, 'voices')

    async def off(bot, message):
        if message.author.name == 'barpacha' or message.author.name == 'Magner85':
            await bot.logout()
            print('logout')
    parser.add_handler(off, 'off')

    async def help(bot, message):
        text = '''Бот для проигрыша фраз и озвучки текста. НЕ ДЛЯ МУЗЫКИ!
Бот работает на облаках

Добавить фразу:
1) Отправить файл .mp3/.wav в личку боту
2) При отправке написать название фразы (любое, нужно для проигрывания и привязки к смайлам)

Удалить фразу:
1) Первое сообщение в чат на сервере remove
2) Второе сообщение название фразы
(привязка удаляется автоматически)

Воспроизвести фразу: 
1) Первое сообщение в чат на сервере f 
2) Второе сообщение название фразы

Привязка к смайлам:
1) Первым сообением в чат на сервере написать bind
2) Вторым сообщением ввести смайл или любой текст
3) Третьим сообщением ввести название фразы

Удаление привязки:
1) Первое сообщение - dbind
2) Второе сообщение - привязанный смайл или текст (НЕ НАЗВАНИЕ ФРАЗЫ!)

Озвучить текст:
$ перед воспроизводимым сообщением
Можно использовать теги [тег значение]
Список тегов (1-3 в процентах от 0 до 100):
1) v - громкость (работает только для озвучки текста)
2) p - высота голоса (работает только для озвучки текста)
3) s - скорость воспроизведения (работает только для озвучки текста)
4) ch - канал (там где ДРУГИЕ ИГОРЫ)
5) vc - голос (дословно из списка voices)
6) f - воспроизведение фразы из файла

Пример использования: $[f frog][v 100]захлопнулась
Воспроизведет фразу frog(ЛИГУШКА) из файла и слово "захлопнулась" на полной громкости

Другие команды:
казино - испытай удачу! Выведет победу или проигрыш
ping - выводит ваш пинг в чат (аналогично смайлу PING)
stop - прекратить воспроизведение
voices - отображает доступные голоса озвучки
pbind - отображает все привязки фраз
saved - отображает сохраненные фразы
botsay - saved для Магнера'''
        await bot.send(message.channel, text, delete_after=300)
        await message.delete()
    parser.add_handler(help, 'help')

    async def ping(bot, message):
        await bot.send(message.channel, random.randint(0, 1000).__str__(), delete_after=300)
        await asyncio.sleep(300)
        await message.delete()
    parser.add_handler(ping, 'ping')
    parser.add_handler(ping, '<:ping:798579897726926938>')

    async def saved(bot, message):
        saved = all_files()
        text = ''
        for i in saved:
            text += i + '\n'
        await bot.send(message.channel, text, delete_after=180)
        await message.delete()
    parser.add_handler(saved, 'saved')
    parser.add_handler(saved, 'botsay')

    async def kazino(bot, message):
        if random.randint(0, 3) == 1:
            await bot.send(message.channel, 'вы выиграли', delete_after=180)
        else:
            await bot.send(message.channel, 'вы проиграли', delete_after=180)
        await asyncio.sleep(180)
        await message.delete()
    parser.add_handler(kazino, 'казино')

    async def test(bot, message):
        await message.delete()
        message = await bot.wait_msg(message.author,60)
        print(message.content)
    parser.add_handler(test, 'test')

    async def fast_f(bot, message):
        await message.delete()
        message = await bot.wait_msg(message.author,120)
        if message == None:
            return
        if message.content == '':
            return
        message.content = r'$[f ' + message.content  + ']'
        await default_handler(bot, message)
    parser.add_handler(fast_f, 'f')

    async def del_file(bot, message):
        await message.delete()
        message = await bot.wait_msg(message.author, 120)
        if message.content == '':
            return
        if all_files().__contains__(message.content):
            delete_file('saved\\' + message.content)
            for bind in load_binding():
                if bind['name'] == message.content:
                    del_binding(bind['text'])
                    break
            await bot.send(message.channel, 'удалено', delete_after=10)
    parser.add_handler(del_file, 'remove')

    async def binding(bot, message):
        await message.delete()
        message = await bot.wait_msg(message.author, 120)
        if message.content == '':
            return
        text = message.content
        await message.delete()
        message = await bot.wait_msg(message.author, 120)
        if message.content == '':
            return
        if not all_files().__contains__(message.content):
            return
        name_file = message.content
        await message.delete()
        upload_binding(text, name_file)
        async def universal(bot, message):
            message.content = r'$[f ' + name_file + ']'
            await default_handler(bot, message)
        parser.add_handler(universal, text)
    parser.add_handler(binding, 'bind')

    async def del_binding(bot, message):
        await message.delete()
        message = await bot.wait_msg(message.author, 120)
        if message.content == '':
            return
        if del_binding(message.content) == True:
            await bot.send(message.channel, 'удалено', delete_after=5)
        await message.delete()
    parser.add_handler(del_binding, 'dbind')

    async def print_binding(bot, message):
        await message.delete()
        msg = ''
        for bind in load_binding():
            msg += bind['text'] + ' ' + bind['name'] + '\n'
        await bot.send(message.channel, msg, delete_after=120)
    parser.add_handler(print_binding, 'pbind')

    async def skip(bot, message):
        await message.delete()
        return
    parser.add_handler(skip, 'skip')

    async def set_vol(bot, message):
        await message.delete()
        message = await bot.wait_msg(message.author, 120)
        if message.content == '':
            return
        file = message.content
        await message.delete()
        message = await bot.wait_msg(message.author, 120)
        if message.content == '':
            return
        try:
            int(message.content)
        except:
            return
        if not (int(message.content) >= 0 and int(message.content) <= 100):
            return
        if int(message.content) == 50:
            del_vol(file)
        else:
            upload_vol(file, int(message.content))
        await message.delete()
    parser.add_handler(set_vol, 'setvol')

    async def print_vol(bot, message):
        await message.delete()
        message = await bot.wait_msg(message.author, 120)
        await message.delete()
        if message.content == '':
            return
        file = find_vol(message.content)
        if file == None:
            if all_files().__contains__(message.content):
                await bot.send(message.channel, '50%', delete_after=30)
        else:
            await bot.send(message.channel, str(file) + '%', delete_after=30)
    parser.add_handler(print_vol, 'pvol')


    for bind in load_binding():
        async def universal(bot, message):
            message.content = r'$[f ' + find_binding(message.content) + ']'
            await default_handler(bot, message)
        parser.add_handler(universal, bind['text'])
    return parser

async def default_handler(bot, message):
    if message.content == '':
        return
    if message.channel.type == discord.ChannelType.private:
        if len(message.attachments) == 0:
            return
        if download(message.attachments[0].url, message.content):
            await bot.send(message.channel, 'готово', delete_after=None)
        else:
            await bot.send(message.channel, 'имя занято', delete_after=None)
    else:
        m = MsgParser(message, bot)
        if not m.is_talk:
            return
        if message.author.voice is None and m.channel is None:
            return
        if m.channel is None:
            channel = message.author.voice.channel
        else:
            channel = m.channel
        for f in m.file_mas:
            await bot.append_playlist(channel, f)
        await message.delete()

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
    return os.listdir(os.path.abspath('saved'))

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

class Talker:
    def __init__(self, TalkerSet: parametrs.Talker, path :str = os.path.abspath('balcon.exe')):
        self.path = path
        self.Talker_settings = TalkerSet

    def run(self, file: str):
        cmd = [self.path]
        cmd.append('-w'); cmd.append('tmp\\' + file)
        cmd.append('-t'); cmd.append(self.Talker_settings.text.__str__())
        cmd.append('-s'); cmd.append((int)((self.Talker_settings.voice_speed-50)/5).__str__())
        cmd.append('-p'); cmd.append((int)((self.Talker_settings.pitch_voice-50)/5).__str__())
        cmd.append('-v'); cmd.append(self.Talker_settings.volume.__str__())
        cmd.append('-n'); cmd.append(self.Talker_settings.voice)
        subprocess.run(cmd)

    def get_voices(self):
        rez = subprocess.run([self.path, '-l'], stdout=subprocess.PIPE)
        voices = []
        for voice in rez.stdout.decode('utf-8').split("\n")[2:-1]:
            voices.append(voice[2:-1])
        return voices

async def main():
    bot = MyClient('NzMzMDA1MDYyNDQ3ODI1MDA3.Xw82KQ.zs0WjdpyyyoN6chxt5Euhu1nTno', default_handler)
    await bot.start()
    print('ready')
    while True:
        await asyncio.sleep(1000)

asyncio.run(main())