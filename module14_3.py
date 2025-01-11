import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto

logging.basicConfig(level=logging.INFO)

class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

API_TOKEN = '7789653976:AAHvzizuR1Tgnbp62o5UcBL2wF66mggpMCc'
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
button_calculate = KeyboardButton('Рассчитать')
button_info = KeyboardButton('Информация')
button_buy = KeyboardButton('Купить')
keyboard.add(button_calculate, button_info, button_buy)

inline_keyboard_buy = InlineKeyboardMarkup(row_width=1)
button_product1 = InlineKeyboardButton('Product1', callback_data='product_buying')
button_product2 = InlineKeyboardButton('Product2', callback_data='product_buying')
button_product3 = InlineKeyboardButton('Product3', callback_data='product_buying')
button_product4 = InlineKeyboardButton('Product4', callback_data='product_buying')
inline_keyboard_buy.add(button_product1, button_product2, button_product3, button_product4)

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
    products = [
        {'name': 'Product1', 'description': 'Описание продукта 1', 'price': 100, 'photo': 'https://images.faberlic.com/images/fl/TflGoods/lg/1001180948373_16167568241.jpg'},
        {'name': 'Product2', 'description': 'Описание продукта 2', 'price': 200, 'photo': 'https://faberlic-ofis.ru/wp-content/uploads/2018/06/kokteyl-faberlic-welness.jpg'},
        {'name': 'Product3', 'description': 'Описание продукта 3', 'price': 300, 'photo': 'https://faberlic-ofis.ru/wp-content/uploads/2018/06/smuzi-faberlic.jpg'},
        {'name': 'Product4', 'description': 'Описание продукта 4', 'price': 400, 'photo': 'https://images.faberlic.com/images/fl/TflGoods/md/1001180948363_16208940071.jpg'},
    ]

    for product in products:
        await message.answer(f'Название: {product["name"]} | Описание: {product["description"]} | Цена: {product["price"]}₽')
        await message.answer_photo(product["photo"])

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
