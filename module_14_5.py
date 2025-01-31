import logging
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from crud_functions import initiate_db, add_user, is_included

logging.basicConfig(level=logging.INFO)

bot = Bot(token=' ')
dp = Dispatcher()

class RegistrationState(StatesGroup):
    username = State()
    email = State()
    age = State()

keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Регистрация')]
    ],
    resize_keyboard=True
)

@dp.message(Command('start'))
@dp.message(Command('help'))
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я бот для регистрации пользователей.\nДля регистрации нажмите на кнопку 'Регистрация' в главном меню.", reply_markup=keyboard)

@dp.message(lambda message: message.text == 'Регистрация')
async def sign_up(message: types.Message, state: FSMContext):
    await message.answer("Введите имя пользователя (только латинский алфавит):")
    await state.set_state(RegistrationState.username)

# Хэндлер для ввода имени пользователя
@dp.message(StateFilter(RegistrationState.username))
async def set_username(message: types.Message, state: FSMContext):
    if not is_included(message.text):
        await state.update_data(username=message.text)
        await message.answer("Введите свой email:")
        await state.set_state(RegistrationState.email)
    else:
        await message.answer("Пользователь существует, введите другое имя")
        await state.set_state(RegistrationState.username)

@dp.message(StateFilter(RegistrationState.email))
async def set_email(message: types.Message, state: FSMContext):
    await state.update_data(email=message.text)
    await message.answer("Введите свой возраст:")
    await state.set_state(RegistrationState.age)

# Хэндлер для ввода возраста пользователя
@dp.message(StateFilter(RegistrationState.age))
async def set_age(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    user_data = await state.get_data()
    add_user(user_data['username'], user_data['email'], user_data['age'])
    await state.clear()
    await message.answer("Вы успешно зарегистрированы!")

@dp.message()
async def unknown_command(message: types.Message):
    await message.answer("Неизвестная команда. Нажмите на кнопку 'Регистрация' в главном меню для регистрации.")

async def main():
    initiate_db()
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
