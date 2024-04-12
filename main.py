import json
import logging
import os
import requests
from aiogram import executor, Dispatcher, Bot, types
from aiogram.dispatcher.filters import IsReplyFilter
from aiogram.dispatcher.filters.state import State, StatesGroup  # состояние
from aiogram.dispatcher import FSMContext  # работа с контекстом
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

# from database import db_start as db

load_dotenv()

bot = Bot(token=os.getenv('API_TOKEN'))
dp = Dispatcher(bot)

# logging.basicConfig(level=logging.DEBUG)  # логирование уровень: дебаг


yan_ident = os.getenv('YANDEX_IDENTIFIER')
yan_api = os.getenv('YANDEX_API_TOKEN')

keyboard = InlineKeyboardMarkup(row_width=2)

keyboard.add(InlineKeyboardButton(text='ФИО', callback_data='bio'),
             InlineKeyboardButton(text='Телефон', callback_data='telephone'),
             InlineKeyboardButton(text='Почта', callback_data='email'),
             InlineKeyboardButton(text='Эпитафия', callback_data='epitaph'))


class User_data(StatesGroup):
    bio = State()
    telephone = State()
    email = State()


class Epitaph(StatesGroup):
    bday = State()
    dday = State()
    mothercity = State()
    activity = State()
    personality = State()


dp.filters_factory.bind(IsReplyFilter)

# --------functions-------
# async def database_start(_):
#     db()
#     print('db OK')


with open('body.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
f.close()
data['modelUri'] = f"gpt://{yan_ident}/yandexgpt-lite"
with open('body.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
f.close()


def gpt(text):
    headers = {
        'Authorization': f'Api-Key {yan_api}'
    }
    url = 'https://llm.api.cloud.yandex.net/foundationModels/v1/completion'
    with open('body.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    f.close()
    data['messages'][2]['text'] = text
    with open('body.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    f.close()
    with open('body.json', 'r', encoding='utf-8') as f:
        data = json.dumps(json.load(f))
    resp = requests.post(url, headers=headers, data=data)

    if resp.status_code != 200:
        raise RuntimeError(
            'Invalid response received: code: {}, message: {}'.format(
                {resp.status_code}, {resp.text}
            )
        )
    return resp.json()['result']['alternatives'][0]['message']['text']


# ------------------------


# =============================  handlers  ====================================
@dp.message_handler(commands='start')
async def send_welcome(message: types.Message):
    await message.answer_sticker('CAACAgIAAxkBAAOsZhLm2J26S3mtglXYkcwgycjeg8oAAmowAAIDUjlLyDwdIQNK90c0BA')
    await message.answer(f"Привет, {message.from_user.first_name}! Я бот, интегрированный с Яндекс ГПТ.")
    await message.answer('Заполни свои личные данные пожалуйста', reply_markup=keyboard)


@dp.message_handler(commands='bot')  # убрать или добавить проверку на админа
async def call_bot(message: types.Message):
    await message.answer('звали?')


@dp.message_handler(is_reply=True)  # переделать не на reply, а на контекст epitaph
async def gpt_usage(message: types.Message):
    generated_text = gpt(message.text)
    await message.answer(generated_text)


# -----------bio
@dp.callback_query_handler(lambda query: query.data == 'bio')
async def callback_bio(callback_query: types.CallbackQuery):
    await User_data.bio.set()
    await bot.send_message(chat_id=callback_query.from_user.id, text='Введите ФИО')


@dp.message_handler(state='bio')
async def write_bio(message: types.Message, state: FSMContext):
    async with state.proxy() as info:
        info['bio'] = message.text
    await state.finish()


# --------------


# ---------telephone
@dp.callback_query_handler(lambda query: query.data == 'telephone')
async def callback_telephone(call: types.CallbackQuery, state: FSMContext):
    await User_data.telephone.set()
    await bot.send_message(chat_id=call.from_user.id, text='Введите телефон')
    async with state.proxy() as info:
        info['telephone'] = call.data
    await state.finish()


# ------------------

# ----------------email
@dp.callback_query_handler(lambda query: query.data == 'email')
async def callback_email(call: types.CallbackQuery, state: FSMContext):
    await User_data.email.set()
    await bot.send_message(chat_id=call.from_user.id, text='Введите почту')


@dp.message_handler(state='email')
async def write_email(message: types.Message, state: FSMContext):
    async with state.proxy() as info:
        info['email'] = message.text
    await state.finish()


# --------------------


@dp.callback_query_handler(lambda query: query.data == 'epitaph')
async def callback_epitath_bday(call: types.CallbackQuery, state: FSMContext):
    await Epitaph.bday.set()
    await bot.send_message(chat_id=call.from_user.id, text='Сейчас давайте ответим на '
                                                           'несколько вопросов для заполнения эпитафии')
    await bot.send_message(chat_id=call.from_user.id, text='Когда человек родился?')
    async with state.proxy() as data:
        data['bday'] = call.data
    state.finish()




# ====================================================================


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)  # , on_startup=database_start)

#todo подумать где хранится дата и как делать цепочку диалога через состояния

#todo также подумать, нужно ли делать состояние в состоянии и почему inline кнопка бесконечно грузится

#todo добавить везде кнопку cancel