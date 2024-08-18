import os
import json
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

bot = Bot(os.getenv('API_TOKEN'))
dp = Dispatcher(bot)

PATHS = {
    'PC': "C:\\Users\\Lenovo\\OneDrive\\Робочий стіл\\python work\\PC",
    'XBOX': "C:\\Users\\Lenovo\\OneDrive\\Робочий стіл\\python work\\XBOX",
    'PLAYSTATION': "C:\\Users\\Lenovo\\OneDrive\\Робочий стіл\\python work\\PLAYSTATION"
}

async def send_platform_choice(chat_id):
    keyboard = InlineKeyboardMarkup()
    buttons = [
        InlineKeyboardButton(text="PC", callback_data="platform_PC"),
        InlineKeyboardButton(text="XBOX", callback_data="platform_XBOX"),
        InlineKeyboardButton(text="PLAYSTATION", callback_data="platform_PLAYSTATION")
    ]
    keyboard.add(*buttons)
    await bot.send_message(chat_id, "Оберіть платформу:", reply_markup=keyboard)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    welcome_message = (
        "Привіт, я metacriticbot, але можеш мене називати Грег. Цей бот створений для того, щоб дізнатися кращі ігри певного року."
    )
    await message.reply(welcome_message)
    await send_platform_choice(message.chat.id)

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('platform_'))
async def handle_platform(callback_query: types.CallbackQuery):
    platform = callback_query.data.split('_')[1]

    if platform == 'XBOX':
        years = range(2001, 2025)
    else:
        years = range(1996, 2025)

    keyboard = InlineKeyboardMarkup(row_width=4)
    buttons = [InlineKeyboardButton(text=str(year), callback_data=f"year_{platform}_{year}") for year in years]
    keyboard.add(*buttons)
    await bot.send_message(callback_query.from_user.id, f"Оберіть рік для {platform}:", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data and c.data.startswith('year_'))
async def handle_year(callback_query: types.CallbackQuery):
    _, platform, year = callback_query.data.split('_')
    json_filename = f'games_{year}.json'
    json_path = os.path.join(PATHS[platform], json_filename)

    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as json_file:
                games_data = json.load(json_file)

            if games_data:
                games_list = "\n".join(games_data)
                await bot.send_message(callback_query.from_user.id, f"Ігри для {platform} за {year} рік:\n{games_list}")

        except json.JSONDecodeError:
            pass  
        except Exception:
            pass  
    
    await send_platform_choice(callback_query.from_user.id)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
