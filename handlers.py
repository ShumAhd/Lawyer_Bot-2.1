import re
import logging
from aiogram import types, Bot, Dispatcher, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram.filters import CommandStart

import config
from config import TOKEN, TOPIC_ID, TARGET_CHAT_ID

# Проверка переменных окружения
if not config.TOKEN or not config.LAWYER_CHAT_ID or not config.TOPIC_ID or not config.TARGET_CHAT_ID:
    raise ValueError("Необходимо определить переменные окружения TOKEN, LAWYER_CHAT_ID, TOPIC_ID и TARGET_CHAT_ID в .env файле")

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()

# FSM для состояния пользователя
class Form(StatesGroup):
    waiting_for_question = State()
    waiting_for_phone = State()

# Функция для проверки релевантности топика
def is_relevant_topic(message: Message) -> bool:
    return (
        message.chat.type == "private" or
        (message.is_topic_message and message.message_thread_id is not None and int(message.message_thread_id) == int(TOPIC_ID))
    )

@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    if message.chat.type == "private":
        await ask_question(message, state)
    elif is_relevant_topic(message):
        await message.answer("Для того чтобы задать вопрос юристу РО, просто напишите 'Вопрос юристу'")

@router.message(lambda message: message.text.lower() == "вопрос юристу")
async def handle_question_to_lawyer(message: Message, state: FSMContext):
    if message.chat.type == "private":
        await ask_question(message, state)
    elif is_relevant_topic(message):
        bot_info = await bot.get_me()
        bot_username = bot_info.username
        button = types.InlineKeyboardButton(
            text='Перейти в личные сообщения',
            url=f'https://t.me/{bot_username}?start=ask'
        )
        markup = types.InlineKeyboardMarkup(inline_keyboard=[[button]])
        await message.answer("Чтобы задать вопрос юристу, перейдите в личные сообщения.", reply_markup=markup)

async def ask_question(message: Message, state: FSMContext):
    await message.answer(
        'Задайте себе несколько вопросов:\n'
        '1. Решение моего вопроса облегчит мне жизнь?\n'
        '2. Я готов воспользоваться ответом юриста?\n'
        '3. Я готов решить данный вопрос окончательно?\n'
        'Только если на все вопросы ответ "Да", задавайте ваш вопрос.'
    )
    await message.answer('Напишите ваш вопрос:')
    await state.set_state(Form.waiting_for_question)

@router.message(Form.waiting_for_question)
async def process_question_step(message: Message, state: FSMContext):
    question_text = message.text
    if not any(char.isalpha() for char in question_text):
        await message.answer('Пожалуйста, используйте буквы в вашем вопросе, а не только цифры.')
        return

    await state.update_data(question=question_text)
    await message.answer('Для продолжения введите номер своего телефона в международном формате, пример: +79241233223')
    await state.set_state(Form.waiting_for_phone)

@router.message(Form.waiting_for_phone)
async def process_phone_step(message: Message, state: FSMContext):
    logging.info("Processing phone step")

    if re.match(r"^\+\d{11}$", message.text):
        user_data = await state.get_data()
        question = user_data['question']

        await bot.send_message(
            TARGET_CHAT_ID,
            f'Новый вопрос от {message.from_user.first_name} @{message.from_user.username}\n\n'
            f'Вопрос: {question}\nКонтактный номер: {message.text}'
        )

        markup = types.ReplyKeyboardMarkup(
            keyboard=[[types.KeyboardButton(text='Задать новый вопрос юристу')]],
            resize_keyboard=True,
            one_time_keyboard=True
        )

        await message.answer(
            'Спасибо! Ваш вопрос отправлен. С вами свяжутся юристы.',
            reply_markup=markup
        )

        await state.clear()
    else:
        await message.answer(
            'Пожалуйста, введите корректный номер телефона в международном формате, пример: +79241233223.'
        )

@router.message(lambda message: message.text == 'Задать новый вопрос юристу')
async def new_question_handler(message: Message, state: FSMContext):
    await ask_question(message, state)

# Подключение роутера к диспетчеру
dp.include_router(router)

all = ['dp', 'bot']
