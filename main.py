from dotenv import load_dotenv

load_dotenv()

import os
import aiogram as ag
import asyncio
import logging

from bot.handlers import router
from bot.database.models import async_main


TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

bot = ag.Bot(token=TELEGRAM_BOT_TOKEN)
dp = ag.Dispatcher()


async def main():
    await async_main()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    if os.getenv('DEBUG_MODE', 'false'):
        logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except Exception as e:
        print(e)
