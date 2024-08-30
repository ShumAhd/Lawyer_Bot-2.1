import re
from aiogram import types, Bot, Dispatcher, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.filters import Command
import config

# Проверка переменных окружения
if not config.TOKEN or not config.LAWYER_CHAT_ID or not config.TOPIC_ID or not config.TARGET_CHAT_ID:
    raise ValueError("Необходимо определить переменные окружения TOKEN, LAWYER_CHAT_ID, TOPIC_ID и TARGET_CHAT_ID в .env файле")

# Инициализация бота и диспетчера
bot = Bot(token=config.TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()

# FSM для состояния пользователя
class Form(StatesGroup):
    waiting_for_question = State()
    waiting_for_phone = State()

# Функция для проверки соответствия message_thread_id
def is_relevant_thread(message: Message):
    return message.message_thread_id == 2

# Обработчики команд и сообщений
@router.message(Command(commands=["start"]))
async def start_handler(message: Message):
    if message.chat.type == 'private':
        await ask_question(message)
    else:
        markup = types.InlineKeyboardMarkup()
        bot_username = (await bot.get_me()).username
        button = types.InlineKeyboardButton('Задать вопрос юристу', url=f't.me/{bot_username}?start=ask')
        markup.add(button)
        await message.answer(
            "Добро пожаловать! Нажмите кнопку ниже, чтобы задать вопрос юристу.",
            reply_markup=markup
        )

async def ask_question(message: Message):
    await message.answer(
        'Задайте себе несколько вопросов:\n'
        '1. Решение моего вопроса облегчит мне жизнь?\n'
        '2. Я готов воспользоваться ответом юриста?\n'
        '3. Я готов решить данный вопрос окончательно?\n'
        'Только если на все вопросы ответ "Да", задавайте ваш вопрос.'
    )
    await message.answer('Напишите ваш вопрос:')
    await Form.waiting_for_question.set()

@router.message(Form.waiting_for_question)
async def process_question_step(message: Message, state: FSMContext):
    question_text = message.text

    if not any(char.isalpha() for char in question_text):
        await message.answer('Вопрос не может состоять только из цифр. Пожалуйста, задайте вопрос, используя буквы.')
        return

    await state.update_data(question=question_text)

    await message.answer(
        'Для продолжения введите номер своего телефона в международном формате, пример: +79241233223'
    )
    await Form.waiting_for_phone.set()

@router.message(Form.waiting_for_phone)
async def process_phone_step(message: Message, state: FSMContext):
    if re.match(r"^\+\d{11}$", message.text):
        user_data = await state.get_data()
        question = user_data['question']

        await bot.send_message(
            config.LAWYER_CHAT_ID,
            f'Новый вопрос от {message.from_user.first_name} @{message.from_user.username}\n\n'
            f'Вопрос: {question}\nКонтактный номер: {message.text}'
        )

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(types.KeyboardButton('Задать новый вопрос юристу'))
        await message.answer('Спасибо! Ваш вопрос отправлен. С вами свяжутся юристы РО.', reply_markup=markup)
        await state.clear()

    else:
        await message.answer('Пожалуйста, введите корректный номер телефона в международном формате, пример: +79241233223.')

@router.message(lambda message: message.text == 'Задать новый вопрос юристу')
async def new_question_handler(message: Message):
    await ask_question(message)

def is_relevant_topic(message: Message):
    return message.is_topic_message and int(message.message_thread_id) == int(config.TOPIC_ID)

@router.message(lambda message: message.text == "Привет" and is_relevant_topic(message))
async def text_handler(message: Message):
    if message.chat.id == int(config.LAWYER_CHAT_ID):
        await message.answer("Привет! Чем могу помочь?")
    else:
        await message.answer("Сообщения из этого чата или темы не обрабатываются.")

dp.include_router(router)
