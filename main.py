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
    data['messages'][1]['text'] = text
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


# --------handlers-------
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


# @dp.message_handler(text='bio')
# async def gimme_bio(message: types.Message):
#


# ====================================callback handlers
@dp.callback_query_handler()
async def callback_query_keyboard(callback_query: types.CallbackQuery):
    cq_data = callback_query.data
    if cq_data == 'bio':
        await bot.send_message(chat_id=callback_query.from_user.id, text=f'{cq_data}')
    elif cq_data == 'telephone':
        await bot.send_message(chat_id=callback_query.from_user.id, text=f'{cq_data}')
    elif cq_data == 'email':
        await bot.send_message(chat_id=callback_query.from_user.id, text=f'{cq_data}')
    elif cq_data == 'biography':
        await bot.send_message(chat_id=callback_query.from_user.id, text=f'{cq_data}')


# -----------------------


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)  #, on_startup=database_start)
