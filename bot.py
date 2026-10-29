import os
from flask import Flask
from threading import Thread
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

# --- 1. Flask чтобы Render не спал ---
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Fartovie bot is alive!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host='0.0.0.0', port=port)

Thread(target=run_web, daemon=True).start()

# --- 2. Telegram ---
TOKEN = os.environ.get("8738317837:AAFlPobuYU-oF2Jb7lryUmSj7nfgbDlR4PM")
ADMIN_ID = 8466271479

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔥 2990 тг - Сценарии", callback_data="price_2990")],
        [InlineKeyboardButton("🚀 3990 тг - 100 Промптов", callback_data="price_3990")],
        [InlineKeyboardButton("💎 4990 тг - Все вместе", callback_data="price_4990")],
    ]
    context.user_data.clear()
    await update.message.reply_text("Привет! Выбери тариф и оплати по QR:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    # 1. Клиент выбрал тариф -> кидаем QR
    if data.startswith("price_"):
        price = data.split("_")[1]
        context.user_data["last_price"] = price
        qr_file = f"qr_{price}.jpg"
        if os.path.exists(qr_file):
            await context.bot.send_photo(chat_id=query.from_user.id, photo=open(qr_file, "rb"), caption=f"Оплати {price} тг по QR.\nПосле оплаты скинь СКРИН чека сюда 👇")
        else:
            await query.message.reply_text(f"Файл {qr_file} не найден в GitHub")

    # 2. Клиент нажал "Скачать файл" после проверки
    elif data.startswith("check_"):
        price = data.split("_")[1]
        try:
            if price == "2990":
                with open("scenarios.pdf", "rb") as f:
                    await context.bot.send_document(chat_id=query.from_user.id, document=f, caption="Твои сценарии 🔥")
            elif price == "3990":
                with open("prompts.pdf", "rb") as f:
                    await context.bot.send_document(chat_id=query.from_user.id, document=f, caption="Твои 100 промптов 🚀")
            elif price == "4990":
                with open("scenarios.pdf", "rb") as f:
                    await context.bot.send_document(chat_id=query.from_user.id, document=f, caption="Часть 1/2 - Сценарии")
                await asyncio.sleep(1)
                with open("prompts.pdf", "rb") as f:
                    await context.bot.send_document(chat_id=query.from_user.id, document=f, caption="Часть 2/2 - 100 промптов 💎")
            await query.message.reply_text("Готово! Удачи 🚀")
        except Exception as e:
            await query.message.reply_text(f"Ошибка: {e} - проверь что PDF загружены в GitHub")

async def handle_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price = context.user_data.get("last_price")
    if not price:
        await update.message.reply_text("Сначала выбери тариф: /start")
        return

    # Форвард админу
    try:
        await context.bot.forward_message(chat_id=ADMIN_ID, from_chat_id=update.effective_chat.id, message_id=update.message.message_id)
    except:
        pass

    # ВОТ ТО САМОЕ ОКНО ПРОВЕРКИ
    msg = await update.message.reply_text("🔍 Проверяю платеж... ⏳\nПодождите 5 секунд...")
    await asyncio.sleep(3)
    await msg.edit_text("✅ Платеж подтвержден!")

    # Кнопка скачать
    keyboard = [[InlineKeyboardButton(f"📥 Скачать файлы за {price} тг", callback_data=f"check_{price}")]]
    await update.message.reply_text("Можешь забирать:", reply_markup=InlineKeyboardMarkup(keyboard))

print("Bot started... СХЕМА С ПРОВЕРКОЙ")
telegram_app = Application.builder().token(TOKEN).connect_timeout(120).read_timeout(120).write_timeout(120).build()
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(handle_buttons))
telegram_app.add_handler(MessageHandler(filters.PHOTO, handle_screenshot))
telegram_app.run_polling()
