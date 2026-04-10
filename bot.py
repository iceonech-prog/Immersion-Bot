Kondicioner
Kondicioner
foksimilian
•
отдыхаю

khs. #xvckhs. #xvc [+VII],  — 1:41
чек
че
ты даун
нет
khs. #xvckhs. #xvc [+VII],  — 16:40
import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

bot.py
14 кб
import aiosqlite

DB_NAME = "bot_database.db"

# Создаем таблицу при первом запуске
async def init_db():

database.py
3 кб
aiogram==3.4.1
aiosqlite==0.19.0
pydantic==2.5.0
aiohttp==3.9.5
requirements.txt
1 кб
# config.py
# ВНИМАНИЕ: На Render этот файл НЕ ИСПОЛЬЗУЕТСЯ!
# Токен и ID админов берутся из переменных окружения.
# Этот файл нужен только для локального тестирования на вашем компьютере.

BOT_TOKEN = "8711955237:AAHUUI-Of_k4A-jwacmD_QdcnLn3mFwcSow"

config.py
1 кб
KondicionerKondicioner [+VII],  — 16:43
https://github.com/iceonech-prog/Immersion-Bot.git
GitHub
GitHub - iceonech-prog/Immersion-Bot
Contribute to iceonech-prog/Immersion-Bot development by creating an account on GitHub.
khs. #xvckhs. #xvc [+VII],  — 16:49
python-3.10.11
runtime.txt
1 кб
KondicionerKondicioner [+VII],  — 20:41
Але
кутак
https://github.com/iceonech-prog/Immersion-Bot.git
GitHub
GitHub - iceonech-prog/Immersion-Bot
Contribute to iceonech-prog/Immersion-Bot development by creating an account on GitHub.
khs. #xvckhs. #xvc [+VII],  — 20:58
aiogram==3.3.0
aiosqlite==0.19.0
pydantic==2.4.2
aiohttp==3.8.5
python-dotenv==1.0.0
requirements.txt
1 кб
import asyncio
import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ConversationHandler, ContextTypes
from telegram.constants import ParseMode

bot.py
16 кб
python-telegram-bot==20.6
aiosqlite==0.19.0
python-dotenv==1.0.0
requirements.txt
1 кб
khs. #xvckhs. #xvc [+VII],  — 21:25
import asyncio
import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ConversationHandler, ContextTypes
from telegram.constants import ParseMode

message.txt
16 кб
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import logging
import os

message.txt
16 кб
khs. #xvckhs. #xvc [+VII],  — 22:32
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import logging
import os

message.txt
15 кб
﻿
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ConversationHandler, ContextTypes
from telegram.constants import ParseMode

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения")

ADMIN_IDS_STR = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(x.strip()) for x in ADMIN_IDS_STR.split(",") if x.strip()] if ADMIN_IDS_STR else []

from database import init_db, save_ticket, update_ticket_status, get_user_by_message, get_ticket_status

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

WAITING_IDEA, WAITING_QUESTION, WAITING_REPLY = range(3)

ticket_counter = 0

def get_next_ticket_number():
    global ticket_counter
    ticket_counter += 1
    return ticket_counter

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="💡 Отправить идею")],
        [KeyboardButton(text="❓ Задать вопрос")]
    ],
    resize_keyboard=True
)

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"👋 Привет, {update.effective_user.full_name}!\n\n"
        "Я бот для связи с командой.\nВыберите действие:",
        reply_markup=main_keyboard
    )

async def idea_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📝 Опишите свою идею ниже:",
        reply_markup=ReplyKeyboardMarkup.remove_keyboard()
    )
    return WAITING_IDEA

async def question_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "❓ Опишите ваш вопрос ниже:",
        reply_markup=ReplyKeyboardMarkup.remove_keyboard()
    )
    return WAITING_QUESTION

async def process_idea(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or "без username"
    ticket_num = get_next_ticket_number()
    message_text = update.message.text
    message_id = update.message.message_id
    
    admin_kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Одобрить", callback_data=f"approve_{message_id}_{ticket_num}"),
            InlineKeyboardButton("❌ Отказать", callback_data=f"reject_{message_id}_{ticket_num}")
        ]
    ])
    
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=(
                    f"💡 <b>НОВАЯ ИДЕЯ #{ticket_num}</b>\n\n"
                    f"👤 От: @{username} (ID: <code>{user_id}</code>)\n\n"
                    f"📄 <b>Содержание:</b>\n{message_text}"
                ),
                reply_markup=admin_kb,
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Ошибка отправки админу {admin_id}: {e}")
    
    await save_ticket(user_id, username, message_id, "idea", message_text)
    
    await update.message.reply_text(
        f"✅ Ваша идея отправлена на рассмотрение!\n"
        f"📌 Номер заявки: <b>#{ticket_num}</b>\n\n"
        f"Ожидайте ответа от команды.",
        reply_markup=main_keyboard,
        parse_mode=ParseMode.HTML
    )
    return ConversationHandler.END

async def process_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    username = update.effective_user.username or "без username"
    ticket_num = get_next_ticket_number()
    message_text = update.message.text
    message_id = update.message.message_id
    
    admin_kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 Ответить", callback_data=f"reply_{message_id}_{ticket_num}")]
    ])
    
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=(
                    f"❓ <b>НОВЫЙ ВОПРОС #{ticket_num}</b>\n\n"
                    f"👤 От: @{username} (ID: <code>{user_id}</code>)\n\n"
                    f"📄 <b>Вопрос:</b>\n{message_text}"
                ),
                reply_markup=admin_kb,
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            logger.error(f"Ошибка отправки админу {admin_id}: {e}")
    
    await save_ticket(user_id, username, message_id, "question", message_text)
    
    await update.message.reply_text(
        f"✅ Ваш вопрос отправлен команде!\n"
        f"📌 Номер заявки: <b>#{ticket_num}</b>\n\n"
        f"Ожидайте ответа от команды.",
        reply_markup=main_keyboard,
        parse_mode=ParseMode.HTML
    )
    return ConversationHandler.END

async def reply_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("⛔ Нет прав", show_alert=True)
        return ConversationHandler.END
    
    parts = query.data.split("_")
    message_id = int(parts[1])
    ticket_num = parts[2] if len(parts) > 2 else "?"
    
    status = await get_ticket_status(message_id)
    if status and status != "pending":
        await query.answer(f"⛔ Заявка #{ticket_num} уже обработана (статус: {status})", show_alert=True)
        return ConversationHandler.END
    
    context.user_data["reply_to_msg"] = message_id
    context.user_data["ticket_num"] = ticket_num
    
    await query.message.reply_text(f"✏️ Напишите ответ пользователю (заявка #{ticket_num}):")
    return WAITING_REPLY

async def send_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return ConversationHandler.END
    
    original_msg_id = context.user_data.get("reply_to_msg")
    ticket_num = context.user_data.get("ticket_num", "?")
    
    if not original_msg_id:
        await update.message.reply_text("❌ Ошибка: не найден ID сообщения")
        return ConversationHandler.END
    
    status = await get_ticket_status(original_msg_id)
    if status and status != "pending":
        await update.message.reply_text(f"⛔ Заявка #{ticket_num} уже обработана (статус: {status}). Ответ не отправлен.")
        return ConversationHandler.END
    
    user_id, ticket_type = await get_user_by_message(original_msg_id)
    admin_name = update.effective_user.username or update.effective_user.full_name
    
    if user_id:
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    f"📬 <b>Ответ на ваш вопрос #{ticket_num}</b>\n\n"
                    f"👤 <b>Администратор:</b> @{admin_name}\n"
                    f"📝 <b>Ответ:</b>\n{update.message.text}"
                ),
                parse_mode=ParseMode.HTML
            )
            await update_ticket_status(original_msg_id, "answered")
            await update.message.reply_text(f"✅ Ответ на заявку #{ticket_num} отправлен пользователю!")
            
            for admin in ADMIN_IDS:
                try:
                    await context.bot.send_message(
                        chat_id=admin,
                        text=f"✅ <b>Администратор @{admin_name}</b> ответил на вопрос <b>#{ticket_num}</b>.",
                        parse_mode=ParseMode.HTML
                    )
                except:
                    pass
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {e}")
    else:
        await update.message.reply_text("❌ Пользователь не найден")
    
    return ConversationHandler.END

async def approve_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("⛔ Нет прав", show_alert=True)
        return
    
    parts = query.data.split("_")
    message_id = int(parts[1])
    ticket_num = parts[2] if len(parts) > 2 else "?"
    
    status = await get_ticket_status(message_id)
    if status and status != "pending":
        await query.answer(f"⛔ Заявка #{ticket_num} уже обработана (статус: {status})", show_alert=True)
        return
    
    user_id, _ = await get_user_by_message(message_id)
    admin_name = query.from_user.username or query.from_user.full_name
    
    if user_id:
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    f"🎉 <b>Отличные новости!</b>\n\n"
                    f"Ваша идея <b>#{ticket_num}</b> была <b>ОДОБРЕНА</b>!\n\n"
                    f"👤 <b>Администратор:</b> @{admin_name}\n"
                    f"Спасибо за ваш вклад!"
                ),
                parse_mode=ParseMode.HTML
            )
            await update_ticket_status(message_id, "approved")
            await query.edit_message_reply_markup(reply_markup=None)
            
            for admin_id in ADMIN_IDS:
                try:
                    await context.bot.send_message(
                        chat_id=admin_id,
                        text=f"🎉 <b>Администратор @{admin_name}</b> одобрил идею <b>#{ticket_num}</b>.",
                        parse_mode=ParseMode.HTML
                    )
                except:
                    pass
        except Exception as e:
            await query.answer(f"❌ Ошибка: {e}", show_alert=True)
    else:
        await query.answer("❌ Пользователь не найден", show_alert=True)

async def reject_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.from_user.id not in ADMIN_IDS:
        await query.answer("⛔ Нет прав", show_alert=True)
        return
    
    parts = query.data.split("_")
    message_id = int(parts[1])
    ticket_num = parts[2] if len(parts) > 2 else "?"
    
    status = await get_ticket_status(message_id)
    if status and status != "pending":
        await query.answer(f"⛔ Заявка #{ticket_num} уже обработана (статус: {status})", show_alert=True)
        return
    
    user_id, _ = await get_user_by_message(message_id)
    admin_name = query.from_user.username or query.from_user.full_name
    
    if user_id:
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    f"📋 <b>Статус вашей идеи #{ticket_num}</b>\n\n"
                    f"К сожалению, ваша идея пока не может быть реализована.\n\n"
                    f"👤 <b>Администратор:</b> @{admin_name}\n"
                    f"Но мы ценим ваше участие и будем рады новым предложениям!"
                ),
                parse_mode=ParseMode.HTML
            )
            await update_ticket_status(message_id, "rejected")
            await query.edit_message_reply_markup(reply_markup=None)
            
            for admin_id in ADMIN_IDS:
                try:
                    await context.bot.send_message(
                        chat_id=admin_id,
                        text=f"📋 <b>Администратор @{admin_name}</b> отклонил идею <b>#{ticket_num}</b>.",
                        parse_mode=ParseMode.HTML
                    )
                except:
                    pass
        except Exception as e:
            await query.answer(f"❌ Ошибка: {e}", show_alert=True)
    else:
        await query.answer("❌ Пользователь не найден", show_alert=True)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Действие отменено.", reply_markup=main_keyboard)
    return ConversationHandler.END

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init_db())
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    idea_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^💡 Отправить идею$"), idea_start)],
        states={
            WAITING_IDEA: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_idea)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    
    question_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^❓ Задать вопрос$"), question_start)],
        states={
            WAITING_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_question)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    
    reply_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(reply_button, pattern="^reply_")],
        states={
            WAITING_REPLY: [MessageHandler(filters.TEXT & ~filters.COMMAND, send_reply)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    
    application.add_handler(CommandHandler("start", cmd_start))
    application.add_handler(idea_conv)
    application.add_handler(question_conv)
    application.add_handler(reply_conv)
    application.add_handler(CallbackQueryHandler(approve_button, pattern="^approve_"))
    application.add_handler(CallbackQueryHandler(reject_button, pattern="^reject_"))
    
    print("✅ Бот запущен на Render.com!")
    
    application.run_polling()
message.txt
15 кб
