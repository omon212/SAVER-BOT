import asyncio
import logging
import requests
import re
from config import config
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()


async def downloader(urls):
    url = "https://auto-download-all-in-one.p.rapidapi.com/v1/social/autolink"

    payload = {"url": urls}
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": "0f95c9454bmshfbfff6f7be74315p12102djsnc98492887d39",
        "X-RapidAPI-Host": "auto-download-all-in-one.p.rapidapi.com"
    }

    response = requests.post(url, json=payload, headers=headers)

    return (response.json())


@dp.message(Command('start'))
async def send_welcome(message: types.Message):
    await message.reply("Send me Url !")


@dp.message()
async def download_content(message: types.Message):
    url = message.text
    reg_ins = 'https:\/\/www\.instagram\.com\/(p|reel)\/([A-Za-z0-9-_]+)\/'
    reg_tt = r'https:\/\/(www\.tiktok\.com\/@[\w]+\/video\/\d+(?:\?\S*)?|vt\.tiktok\.com\/[\w]+\/?)'
    instagram = re.search(reg_ins, url)
    tiktok = re.search(reg_tt, url)
    try:
        if instagram:
            content = await downloader(urls=url)
            if content['error'] == False and content['medias'][0]['type'] == 'image':
                photo = content['medias'][0]['url']
                msg = await message.answer('⏳ Please wait...')
                await asyncio.sleep(1)
                await msg.delete()
                await bot.send_photo(chat_id=message.chat.id, photo=photo)
            elif content['error'] == False and content['medias'][0]['type'] == 'video':
                video = content['medias'][0]['url']
                msg = await message.answer('⏳ Please wait...')
                await asyncio.sleep(1)
                await msg.delete()
                await bot.send_video(chat_id=message.chat.id, video=video)
            else:
                dd = url.replace('www.', 'dd')
                msg = await message.answer('⏳ Please wait...')
                await asyncio.sleep(0.5)
                await msg.delete()
                await message.answer(dd)

        elif tiktok:
            content = await downloader(urls=url)
            if content['error'] == False:
                video = content['medias'][0]['url']
                music = content['medias'][-1]['url']
                msg = await message.answer('⏳ Please wait...')
                await asyncio.sleep(1)
                await msg.delete()
                await bot.send_video(chat_id=message.chat.id, video=video)
                await bot.send_audio(chat_id=message.chat.id, audio=music)

    except Exception as e:
        logger.error(f"Failed to send media: {e}")
        await message.answer("Failed to process the media.")


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())