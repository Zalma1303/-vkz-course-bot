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
        [InlineKeyboardButton(text="🔽 Выбрать курс", callback_data="select_course")],
        [InlineKeyboardButton(text="ℹ️ О фонде", url="https://www.osoo.kg/inn/02104201110143/")],
        [InlineKeyboardButton(text="📞 Поддержка: Алмаз (WhatsApp)", url="https://wa.me/996557555234")]
    ])

    await message.answer(
        f"{LOGO}\n\n"
        "<b>Мы проводим онлайн-курсы для родителей, специалистов и всех, кто заботится о развитии и здоровье детей.</b>\n\n"
        "📚 <b>Доступные направления:</b>\n"
        "• АВА-терапия\n"
        "• Дефектология\n"
        "• Сенсорная интеграция\n\n"
        "📍 На русском и кыргызском языках\n"
        "📍 Одобрено Министерством здравоохранения и культуры КР\n\n"
        "Нажмите кнопку ниже, чтобы начать обучение 👇",
        reply_markup=kb
    )


@router.callback_query(F.data == "select_course")
async def show_courses(callback: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="АВА-терапия", callback_data="course:АВА-терапия")],
        [InlineKeyboardButton(text="Дефектология", callback_data="course:Дефектология")],
        [InlineKeyboardButton(text="Сенсорная интеграция", callback_data="course:Сенсорная интеграция")]
    ])
    await callback.message.edit_text("Выберите интересующий вас курс:", reply_markup=kb)
    await callback.answer()


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
    price_kgs = course_info["price"]

    # Фиксированные цены в других валютах
    price_rub = {
        "АВА-терапия": 3200,
        "Дефектология": 2300,
        "Сенсорная интеграция": 2800
    }[course_name]

    price_usd = {
        "АВА-терапия": 40,
        "Дефектология": 30,
        "Сенсорная интеграция": 35
    }[course_name]

    user_selected_course[callback.from_user.id] = (course_name, lang)

    qr_image = FSInputFile(QR_PATH)

    caption = (
        f"📘 <b>{course_name} ({lang})</b>\n\n"
        f"💰 Стоимость курса:\n"
        f"• <b>{price_kgs} сом</b> (Кыргызстан)\n"
        f"• <b>{price_rub} ₽</b> (Россия)\n"
        f"• <b>${price_usd}</b> (США и другие страны)\n\n"
        "🌍 <b>Как оплатить:</b>\n"
        "➤ Для России — перевод через ЮMoney\n"
        "➤ Для Кыргызстана — MБанк (QR ниже)\n"
        "➤ После оплаты — отправьте чек (фото / скрин)\n\n"
        f"{DISCLAIMER}"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Оплатить через ЮMoney", url="https://yoomoney.ru/to/4100119099824929")],
        [InlineKeyboardButton(text="📞 Поддержка: Алмаз (WhatsApp)", url="https://wa.me/996557555234")]
    ])

    await callback.message.answer_photo(
        qr_image,
        caption=caption,
        reply_markup=kb
    )
    await callback.answer()