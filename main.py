import DiscordApi
import asyncio
import discord_command

async def main():
    bot = DiscordApi.MyClient('NzMzMDA1MDYyNDQ3ODI1MDA3.Xw82KQ.zs0WjdpyyyoN6chxt5Euhu1nTno', discord_command.default_handler)
    await bot.start()
    print('ready')
    while True:
        await asyncio.sleep(1000)

asyncio.run(main())