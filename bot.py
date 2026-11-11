import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from dotenv import load_dotenv
from database import init_db, add_participant, get_participants

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

class Registration(StatesGroup):
    full_name = State()
    game = State()
    game_nickname = State()

game_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="CS2"), KeyboardButton(text="Dota 2")],
        [KeyboardButton(text="Minecraft"), KeyboardButton(text="Roblox")],
        [KeyboardButton(text="Другая дисциплина")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! 👋 Это бот для записи на турнир.\n\n"
        "Нажми /register, чтобы зарегистрироваться."
    )

@dp.message(Command("register"))
async def cmd_register(message: types.Message, state: FSMContext):
    await message.answer("Введите ваши ФИО (Фамилия Имя):", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Registration.full_name)

@dp.message(Registration.full_name)
async def process_full_name(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await message.answer("Выберите или напишите дисциплину (игру):", reply_markup=game_kb)
    await state.set_state(Registration.game)

@dp.message(Registration.game)
async def process_game(message: types.Message, state: FSMContext):
    await state.update_data(game=message.text)
    await message.answer("Введите ваш игровой никнейм или ID:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Registration.game_nickname)

@dp.message(Registration.game_nickname)
async def process_nickname(message: types.Message, state: FSMContext):
    data = await state.get_data()
    
    success = add_participant(
        user_id=message.from_user.id,
        username=message.from_user.username or "No username",
        full_name=data['full_name'],
        game=data['game'],
        game_nickname=message.text
    )
    
    if success:
        await message.answer(
            f"✅ **Вы успешно зарегистрированы!**\n\n"
            f"📌 **ФИО:** {data['full_name']}\n"
            f"🎮 **Дисциплина:** {data['game']}\n"
            f"🏷 **Ник:** {message.text}",
            parse_mode="Markdown"
        )
    else:
        await message.answer("⚠️ Вы уже зарегистрированы на турнир.")
        
    await state.clear()

@dp.message(Command("list"))
async def cmd_list(message: types.Message):
    participants = get_participants()
    if not participants:
        await message.answer("Список участников пока пуст.")
        return
    
    text = "📋 **Зарегистрированные участники:**\n\n"
    for idx, (name, game, nick) in enumerate(participants, 1):
        text += f"{idx}. {name} — [{game}] Ник: `{nick}`\n"
    
    await message.answer(text, parse_mode="Markdown")

async def main():
    init_db()
    logging.basicConfig(level=logging.INFO)
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())