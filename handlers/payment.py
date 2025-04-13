# handlers/payment.py

from aiogram import Router, F
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
)
from db import log_purchase
from config import ADMIN_IDS, COURSES
from handlers.start import user_selected_course  # импортируем выбор курса

router = Router()

# Временно храним ID → файл чека
user_pending_payments = {}

@router.message(F.photo | F.document)
async def handle_payment_proof(message: Message):
    user_id = message.from_user.id
    file_id = (
        message.photo[-1].file_id if message.photo else message.document.file_id
    )

    # Запоминаем чек
    user_pending_payments[user_id] = file_id

    # Создаем кнопки для админа
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"approve:{user_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject:{user_id}")
        ]
    ])

    for admin_id in ADMIN_IDS:
        await message.bot.send_message(
            admin_id,
            f"📩 Новый чек от пользователя @{message.from_user.username or user_id}\n"
            f"User ID: <code>{user_id}</code>",
            reply_markup=kb
        )

        # Отправляем файл чека
        if message.photo:
            await message.bot.send_photo(admin_id, file_id)
        else:
            await message.bot.send_document(admin_id, file_id)

    await message.reply("✅ Чек отправлен на модерацию. Ожидайте подтверждения.")


@router.callback_query(F.data.startswith("approve:"))
async def approve_access(callback: CallbackQuery):
    user_id = int(callback.data.split(":")[1])

    course_name, lang = user_selected_course.get(user_id, (None, None))

    if course_name and lang:
        link = COURSES[course_name][lang]["link"]
        
        await log_purchase(
    user_id=user_id,
    username=callback.from_user.username or "no_username",
    course=course_name,
    lang=lang,
    confirmed_by=callback.from_user.username or "admin"
)
        await callback.bot.send_message(
            user_id,
            f"✅ Ваш платёж подтверждён!\n\n"
            f"<b>{course_name} ({lang})</b>\n"
            f"Вот ваша ссылка на курс: {link}"
        )
    else:
        await callback.bot.send_message(
            user_id,
            "⚠️ Платёж подтверждён, но не удалось определить курс. Пожалуйста, свяжитесь с поддержкой."
        )

    await callback.message.edit_text("Платёж подтверждён ✅")
    await callback.answer()


@router.callback_query(F.data.startswith("reject:"))
async def reject_access(callback: CallbackQuery):
    user_id = int(callback.data.split(":")[1])

    await callback.bot.send_message(
        user_id,
        "❌ Ваш чек был отклонён. Пожалуйста, перепроверьте оплату или обратитесь в поддержку."
    )

    await callback.message.edit_text("Чек отклонён ❌")
    await callback.answer()