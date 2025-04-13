# handlers/start.py

from aiogram import Router, F
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
)
from config import COURSES, MBANK_PHONE, QR_PATH

router = Router()

# 🔐 Хранилище выбранного курса пользователем
user_selected_course = {}

# 🧠 Логотип и бренд
LOGO = "🧠 Фонд «Вместе к Здоровью» | VKZ"
DISCLAIMER = (
    "⚠️ Все материалы предназначены только для личного пользования.\n"
    "Распространение без письменного разрешения Фонда запрещено."
)

@router.message(F.text == "/start")
async def start_handler(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="АВА-терапия", callback_data="course:АВА-терапия")],
        [InlineKeyboardButton(text="Дефектология", callback_data="course:Дефектология")],
        [InlineKeyboardButton(text="Сенсорная интеграция", callback_data="course:Сенсорная интеграция")]
    ])

    await message.answer(
        f"{LOGO}\n\n"
        "<b>Добро пожаловать в обучающий бот фонда!</b>\n"
        "Здесь вы можете приобрести доступ к образовательным курсам, направленным на поддержку здоровья, развития и благополучия.\n\n"
        "Выберите интересующий вас курс ниже 👇",
        reply_markup=kb
    )


@router.callback_query(F.data.startswith("course:"))
async def choose_language(callback: CallbackQuery):
    course_name = callback.data.split(":")[1]

    mapping = {
        "АВА-терапия": "ava",
        "Дефектология": "defekt",
        "Сенсорная интеграция": "sensor"
    }

    course_code = mapping[course_name]

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data=f"lang:{course_code}:ru"),
            InlineKeyboardButton(text="🇰🇬 Кыргызский", callback_data=f"lang:{course_code}:kg")
        ]
    ])

    await callback.message.edit_text(
        f"📘 <b>{course_name}</b>\n\nВыберите язык обучения:", reply_markup=kb
    )
    await callback.answer()


@router.callback_query(F.data.startswith("lang:"))
async def show_payment_info(callback: CallbackQuery):
    _, course_code, lang_code = callback.data.split(":")

    course_reverse = {
        "ava": "АВА-терапия",
        "defekt": "Дефектология",
        "sensor": "Сенсорная интеграция"
    }

    lang_reverse = {
        "ru": "Русский",
        "kg": "Кыргызский"
    }

    course_name = course_reverse[course_code]
    lang = lang_reverse[lang_code]
    course_info = COURSES[course_name][lang]
    price = course_info["price"]

    user_selected_course[callback.from_user.id] = (course_name, lang)

    qr_image = FSInputFile(QR_PATH)

    await callback.message.answer_photo(
        qr_image,
        caption=(
            f"📘 <b>{course_name} ({lang})</b>\n\n"
            f"💰 Стоимость курса: <b>{price} сом</b>\n"
            f"📱 Оплатите на номер MБанк: <code>{MBANK_PHONE}</code>\n\n"
            "После оплаты отправьте фото чека в этот чат. Администратор проверит платёж и предоставит доступ.\n\n"
            f"{DISCLAIMER}"
        )
    )
    await callback.answer()