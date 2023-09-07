from aiogram import types
from handlers.default_handlers.start import start_settings
from loader import dp


@dp.message_handler(commands=["help"])
async def bot_help(message: types.Message):
    await message.reply('Вот список доступных команд')
    await start_settings(message)
