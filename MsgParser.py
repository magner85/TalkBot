import re
import discord_command
import parametrs
import asyncio
import Talker
import os
import DiscordApi
import discord
import fileManager

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

    def __init__(self, message:discord.message, client:DiscordApi.MyClient):
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
                    while os.listdir('tmp').count(name):
                        name += '!'
                    out_par.text = t
                    Talker.Talker(out_par).run(name)
                    self.file_mas.append('tmp\\'+name)
                if filename is None:
                    break
                for f in fileManager.all_files():
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

    def add_handler(self, coro, text:str):
        self.dctext.append(text)
        self.dc.append(coro)