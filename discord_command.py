import fileManager
import discord
import MsgParser
import asyncio
import Talker
import parametrs
import random

def append_handler(parser:MsgParser.MsgParser):
    async def stop(bot, message):
        bot.playing[message.author.voice.channel.id] = None
        await message.delete()
    parser.add_handler(stop, 'stop')

    async def voices(bot, message):
        voices = Talker.Talker(parametrs.Talker()).get_voices()
        text = ''
        for i in voices:
            text += i + '\n'
        await bot.send(message.channel, text, delete_after=180)
        await message.delete()
    parser.add_handler(voices, 'voices')

    async def off(bot, message):
        if message.author.name == 'barpacha':
            await bot.logout()
            print('logout')
    parser.add_handler(off, 'off')

    async def help(bot, message):
        text = '''Бот для проигрыша фраз и озвучки текста. НЕ ДЛЯ МУЗЫКИ!
Бот работает только когда barpacha онлайн!

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
        saved = fileManager.all_files()
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
        if fileManager.all_files().__contains__(message.content):
            fileManager.delete_file('saved\\' + message.content)
            for bind in fileManager.load_binding():
                if bind['name'] == message.content:
                    fileManager.del_binding(bind['text'])
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
        if not fileManager.all_files().__contains__(message.content):
            return
        name_file = message.content
        await message.delete()
        fileManager.upload_binding(text, name_file)
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
        if fileManager.del_binding(message.content) == True:
            await bot.send(message.channel, 'удалено', delete_after=5)
        await message.delete()
    parser.add_handler(del_binding, 'dbind')

    async def print_binding(bot, message):
        await message.delete()
        msg = ''
        for bind in fileManager.load_binding():
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
            fileManager.del_vol(file)
        else:
            fileManager.upload_vol(file, int(message.content))
        await message.delete()
    parser.add_handler(set_vol, 'setvol')

    async def print_vol(bot, message):
        await message.delete()
        message = await bot.wait_msg(message.author, 120)
        await message.delete()
        if message.content == '':
            return
        file = fileManager.find_vol(message.content)
        if file == None:
            if fileManager.all_files().__contains__(message.content):
                await bot.send(message.channel, '50%', delete_after=30)
        else:
            await bot.send(message.channel, str(file) + '%', delete_after=30)
    parser.add_handler(print_vol, 'pvol')


    for bind in fileManager.load_binding():
        async def universal(bot, message):
            message.content = r'$[f ' + fileManager.find_binding(message.content) + ']'
            await default_handler(bot, message)
        parser.add_handler(universal, bind['text'])
    return parser

async def default_handler(bot, message):
    if message.content == '':
        return
    if message.channel.type == discord.ChannelType.private:
        if len(message.attachments) == 0:
            return
        if fileManager.download(message.attachments[0].url, message.content):
            await bot.send(message.channel, 'готово', delete_after=None)
        else:
            await bot.send(message.channel, 'имя занято', delete_after=None)
    else:
        m = MsgParser.MsgParser(message, bot)
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




