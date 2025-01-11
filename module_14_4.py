import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
import crud_functions

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Определение состояний
class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

# Инициализация бота
API_TOKEN = '7789653976:AAHvzizuR1Tgnbp62o5UcBL2wF66mggpMCc'  # Замените на ваш токен
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Создаем подключение к базе данных и таблице Products
crud_functions.initiate_db()

# Основное меню
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
button_calculate = KeyboardButton('Рассчитать')
button_info = KeyboardButton('Информация')
button_buy = KeyboardButton('Купить')  # Новая кнопка "Купить"
keyboard.add(button_calculate, button_info, button_buy)

# Inline-клавиатура для покупки
inline_keyboard_buy = InlineKeyboardMarkup(row_width=1)
button_product1 = InlineKeyboardButton('Product1', callback_data='product_buying')
button_product2 = InlineKeyboardButton('Product2', callback_data='product_buying')
button_product3 = InlineKeyboardButton('Product3', callback_data='product_buying')
button_product4 = InlineKeyboardButton('Product4', callback_data='product_buying')
inline_keyboard_buy.add(button_product1, button_product2, button_product3, button_product4)

# Inline-клавиатура
inline_keyboard = InlineKeyboardMarkup(row_width=2)
button_calories = InlineKeyboardButton('Рассчитать норму калорий', callback_data='calories')
button_formulas = InlineKeyboardButton('Формулы расчёта', callback_data='formulas')
inline_keyboard.add(button_calories, button_formulas)

@dp.message_handler(commands=['start', 'help'])
async def cmd_start(message: types.Message):
    await message.reply('Привет! Я бот, помогающий твоему здоровью.', reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == 'Купить')
async def buy_products(message: types.Message):
    await message.answer("Выберите продукт для покупки:", reply_markup=inline_keyboard_buy)
    await get_buying_list(message)

async def get_buying_list(message: types.Message):
    products = crud_functions.get_all_products()

    for product in products:
        await message.answer(f'Название: {product[1]} | Описание: {product[2]} | Цена: {product[3]}₽')
        await message.answer_photo(product[4])

@dp.callback_query_handler(text='formulas')
async def get_formulas(call: types.CallbackQuery):
    await call.message.answer("Формула Миффлина-Сан Жеора:\n"
                              "BMR = 10 * вес(кг) + 6.25 * рост(см) - 5 * возраст(годы) + 5 (для мужчин)\n"
                              "или\n"
                              "BMR = 10 * вес(кг) + 6.25 * рост(см) - 5 * возраст(годы) - 161 (для женщин)")
    await call.answer()

@dp.callback_query_handler(text='calories')
async def set_age(call: types.CallbackQuery):
    await UserState.age.set()
    await call.message.answer("Введите свой возраст:")
    await call.answer()

@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await UserState.growth.set()
    await message.reply("Введите свой рост:")

@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    await state.update_data(growth=message.text)
    await UserState.weight.set()
    await message.reply("Введите свой вес:")

@dp.message_handler(state=UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    await state.update_data(weight=message.text)

    data = await state.get_data()
    age = int(data.get('age'))
    growth = int(data.get('growth'))
    weight = int(data.get('weight'))

    bmr = 10 * weight + 6.25 * growth - 5 * age + 5
    await message.reply(f"Ваша норма калорий: {bmr:.2f} калорий в день.")

    await state.finish()

@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call: types.CallbackQuery):
    await call.message.answer("Вы успешно приобрели продукт!")
    await call.answer()

@dp.message_handler(lambda message: True)
async def all_messages(message: types.Message):
    await message.reply('Введите команду /start, чтобы начать общение.')

if __name__ == '__main__':
    print("Запуск бота...")
    executor.start_polling(dp, skip_updates=True)
