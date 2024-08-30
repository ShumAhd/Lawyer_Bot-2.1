import asyncio
import logging
import traceback
from aiogram import Bot, Dispatcher
from handlers import dp, bot
import config

logging.basicConfig(level=logging.INFO)

async def on_startup(dispatcher: Dispatcher):
    logging.info("Bot is starting...")

async def on_shutdown(dispatcher: Dispatcher):
    logging.warning("Shutting down...")
    # Закрыть соединения и т.д.
    await bot.session.close()

async def start_polling_with_recovery(dp: Dispatcher, bot: Bot):
    while True:
        try:
            await dp.start_polling(bot, on_startup=on_startup, on_shutdown=on_shutdown)
        except (asyncio.TimeoutError, ConnectionError) as e:
            logging.error(f"Polling error: {e}")
            await asyncio.sleep(15)  # Задержка перед повторным запуском Polling
        except Exception as e:
            logging.error(f"Unexpected error: {traceback.format_exc()}")
            await asyncio.sleep(15)  # Задержка перед повторным запуском Polling

if __name__ == '__main__':
    asyncio.run(start_polling_with_recovery(dp, bot))
