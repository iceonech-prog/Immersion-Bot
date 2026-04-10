import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# Токен и ID админов берем из переменных окружения Render
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS_STR = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(x.strip()) for x in ADMIN_IDS_STR.split(",") if x.strip()]

from database import init_db, save_ticket, update_ticket_status, get_user_by_message, get_ticket_status

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Состояния
class Form(StatesGroup):
    waiting_for_idea = State()
    waiting_for_question = State()
    waiting_for_reply = State()

# Клавиатура
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💡 Отправить идею")],
        [KeyboardButton(text="❓ Задать вопрос")]
    ],
    resize_keyboard=True
)

# Счётчик заявок (сбрасывается при перезапуске бота)
ticket_counter = 0

def get_next_ticket_number():
    global ticket_counter
    ticket_counter += 1
    return ticket_counter

# ========== КОМАНДА /start ==========
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        f"👋 Привет, {message.from_user.full_name}!\n\n"
        "Я бот для связи с командой.\nВыберите действие:",
        reply_markup=main_keyboard
    )

# ========== ОТПРАВИТЬ ИДЕЮ ==========
@dp.message(F.text == "💡 Отправить идею")
async def idea_start(message: types.Message, state: FSMContext):
    await message.answer("📝 Опишите свою идею ниже:", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Form.waiting_for_idea)

# ========== ЗАДАТЬ ВОПРОС ==========
@dp.message(F.text == "❓ Задать вопрос")
async def question_start(message: types.Message, state: FSMContext):
    await message.answer("❓ Опишите ваш вопрос ниже:", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Form.waiting_for_question)

# ========== ПОЛУЧЕНИЕ ИДЕИ ==========
@dp.message(Form.waiting_for_idea)
async def process_idea(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username or "без username"
    ticket_num = get_next_ticket_number()
    
    admin_kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Одобрить", callback_data=f"approve_{message.message_id}_{ticket_num}"),
            InlineKeyboardButton(text="❌ Отказать", callback_data=f"reject_{message.message_id}_{ticket_num}")
        ]
    ])
    
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                f"💡 <b>НОВАЯ ИДЕЯ #{ticket_num}</b>\n\n"
                f"👤 От: @{username} (ID: <code>{user_id}</code>)\n\n"
                f"📄 <b>Содержание:</b>\n{message.text}",
                reply_markup=admin_kb,
                parse_mode="HTML"
            )
        except Exception as e:
            logging.error(f"Ошибка отправки админу {admin_id}: {e}")
    
    await save_ticket(user_id, username, message.message_id, "idea", message.text)
    await message.answer(
        f"✅ Ваша идея отправлена на рассмотрение!\n"
        f"📌 Номер заявки: <b>#{ticket_num}</b>\n\n"
        f"Ожидайте ответа от команды.",
        reply_markup=main_keyboard,
        parse_mode="HTML"
    )
    await state.clear()

# ========== ПОЛУЧЕНИЕ ВОПРОСА ==========
@dp.message(Form.waiting_for_question)
async def process_question(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username or "без username"
    ticket_num = get_next_ticket_number()
    
    admin_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Ответить", callback_data=f"reply_{message.message_id}_{ticket_num}")]
    ])
    
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                admin_id,
                f"❓ <b>НОВЫЙ ВОПРОС #{ticket_num}</b>\n\n"
                f"👤 От: @{username} (ID: <code>{user_id}</code>)\n\n"
                f"📄 <b>Вопрос:</b>\n{message.text}",
                reply_markup=admin_kb,
                parse_mode="HTML"
            )
        except Exception as e:
            logging.error(f"Ошибка отправки админу {admin_id}: {e}")
    
    await save_ticket(user_id, username, message.message_id, "question", message.text)
    await message.answer(
        f"✅ Ваш вопрос отправлен команде!\n"
        f"📌 Номер заявки: <b>#{ticket_num}</b>\n\n"
        f"Ожидайте ответа от команды.",
        reply_markup=main_keyboard,
        parse_mode="HTML"
    )
    await state.clear()

# ========== КНОПКА "ОТВЕТИТЬ" ==========
@dp.callback_query(F.data.startswith("reply_"))
async def reply_to_question(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Нет прав", show_alert=True)
        return
    
    parts = callback.data.split("_")
    message_id = int(parts[1])
    ticket_num = parts[2] if len(parts) > 2 else "?"
    
    status = await get_ticket_status(message_id)
    if status and status != "pending":
        await callback.answer(f"⛔ Заявка #{ticket_num} уже обработана (статус: {status})", show_alert=True)
        return
    
    await state.update_data(reply_to_msg=message_id, ticket_num=ticket_num)
    await state.set_state(Form.waiting_for_reply)
    await callback.message.answer(f"✏️ Напишите ответ пользователю (заявка #{ticket_num}):")
    await callback.answer()

# ========== ОТПРАВКА ОТВЕТА ==========
@dp.message(Form.waiting_for_reply)
async def send_reply(message: types.Message, state: FSMContext):
    if message.from_user.id not in ADMIN_IDS:
        return
    
    data = await state.get_data()
    original_msg_id = data.get("reply_to_msg")
    ticket_num = data.get("ticket_num", "?")
    
    if not original_msg_id:
        await message.answer("❌ Ошибка: не найден ID сообщения")
        await state.clear()
        return
    
    status = await get_ticket_status(original_msg_id)
    if status and status != "pending":
        await message.answer(f"⛔ Заявка #{ticket_num} уже обработана (статус: {status}). Ответ не отправлен.")
        await state.clear()
        return
    
    user_id, ticket_type = await get_user_by_message(original_msg_id)
    admin_name = message.from_user.username or message.from_user.full_name
    
    if user_id:
        try:
            await bot.send_message(
                user_id,
                f"📬 <b>Ответ на ваш вопрос #{ticket_num}</b>\n\n"
                f"👤 <b>Администратор:</b> @{admin_name}\n"
                f"📝 <b>Ответ:</b>\n{message.text}",
                parse_mode="HTML"
            )
            await update_ticket_status(original_msg_id, "answered")
            await message.answer(f"✅ Ответ на заявку #{ticket_num} отправлен пользователю!")
            
            for admin in ADMIN_IDS:
                try:
                    await bot.send_message(
                        admin,
                        f"✅ <b>Администратор @{admin_name}</b> ответил на вопрос <b>#{ticket_num}</b>.",
                        parse_mode="HTML"
                    )
                except:
                    pass
        except Exception as e:
            await message.answer(f"❌ Ошибка: {e}")
    else:
        await message.answer("❌ Пользователь не найден")
    
    await state.clear()

# ========== ОДОБРЕНИЕ ИДЕИ ==========
@dp.callback_query(F.data.startswith("approve_"))
async def approve_idea(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Нет прав", show_alert=True)
        return
    
    parts = callback.data.split("_")
    message_id = int(parts[1])
    ticket_num = parts[2] if len(parts) > 2 else "?"
    
    status = await get_ticket_status(message_id)
    if status and status != "pending":
        await callback.answer(f"⛔ Заявка #{ticket_num} уже обработана (статус: {status})", show_alert=True)
        return
    
    user_id, _ = await get_user_by_message(message_id)
    admin_name = callback.from_user.username or callback.from_user.full_name
    
    if user_id:
        try:
            await bot.send_message(
                user_id,
                f"🎉 <b>Отличные новости!</b>\n\n"
                f"Ваша идея <b>#{ticket_num}</b> была <b>ОДОБРЕНА</b>!\n\n"
                f"👤 <b>Администратор:</b> @{admin_name}\n"
                f"Спасибо за ваш вклад!",
                parse_mode="HTML"
            )
            await update_ticket_status(message_id, "approved")
            await callback.message.edit_reply_markup(reply_markup=None)
            await callback.answer("✅ Идея одобрена!")
            
            for admin_id in ADMIN_IDS:
                try:
                    await bot.send_message(
                        admin_id,
                        f"🎉 <b>Администратор @{admin_name}</b> одобрил идею <b>#{ticket_num}</b>.",
                        parse_mode="HTML"
                    )
                except:
                    pass
        except Exception as e:
            await callback.answer(f"❌ Ошибка: {e}", show_alert=True)
    else:
        await callback.answer("❌ Пользователь не найден", show_alert=True)

# ========== ОТКЛОНЕНИЕ ИДЕИ ==========
@dp.callback_query(F.data.startswith("reject_"))
async def reject_idea(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔ Нет прав", show_alert=True)
        return
    
    parts = callback.data.split("_")
    message_id = int(parts[1])
    ticket_num = parts[2] if len(parts) > 2 else "?"
    
    status = await get_ticket_status(message_id)
    if status and status != "pending":
        await callback.answer(f"⛔ Заявка #{ticket_num} уже обработана (статус: {status})", show_alert=True)
        return
    
    user_id, _ = await get_user_by_message(message_id)
    admin_name = callback.from_user.username or callback.from_user.full_name
    
    if user_id:
        try:
            await bot.send_message(
                user_id,
                f"📋 <b>Статус вашей идеи #{ticket_num}</b>\n\n"
                f"К сожалению, ваша идея пока не может быть реализована.\n\n"
                f"👤 <b>Администратор:</b> @{admin_name}\n"
                f"Но мы ценим ваше участие и будем рады новым предложениям!",
                parse_mode="HTML"
            )
            await update_ticket_status(message_id, "rejected")
            await callback.message.edit_reply_markup(reply_markup=None)
            await callback.answer("✅ Отказ отправлен")
            
            for admin_id in ADMIN_IDS:
                try:
                    await bot.send_message(
                        admin_id,
                        f"📋 <b>Администратор @{admin_name}</b> отклонил идею <b>#{ticket_num}</b>.",
                        parse_mode="HTML"
                    )
                except:
                    pass
        except Exception as e:
            await callback.answer(f"❌ Ошибка: {e}", show_alert=True)
    else:
        await callback.answer("❌ Пользователь не найден", show_alert=True)

# ========== ЗАПУСК ==========
async def main():
    await init_db()
    print("✅ Бот запущен на Render.com!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())