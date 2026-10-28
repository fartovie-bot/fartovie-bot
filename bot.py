import os
from flask import Flask
from threading import Thread

app = Flask(__name__)
@app.route('/')
def home():
    return "Fartovie bot is alive!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

Thread(target=run_web, daemon=True).start()
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

TOKEN = "8738317837:AAFa5YnMtUD6xuZKnL7HIafcbWu9s1QxaF4"
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
    if data.startswith("price_"):
        price = data.split("_")[1]
        context.user_data["last_price"] = price
        qr_file = f"qr_{price}.jpg"
        if os.path.exists(qr_file):
            await context.bot.send_photo(chat_id=query.from_user.id, photo=open(qr_file, "rb"), caption=f"Оплати {price} тг по QR.\nПосле оплаты скинь СКРИН чека сюда 👇")
        else:
            await query.message.reply_text(f"QR {qr_file} не найден")
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
                await asyncio.sleep(2)
                with open("prompts.pdf", "rb") as f:
                    await context.bot.send_document(chat_id=query.from_user.id, document=f, caption="Часть 2/2 - 100 промптов 💎")
            await query.message.reply_text("Готово! ✅")
        except Exception as e:
            await query.message.reply_text(f"Ошибка: {e}")

async def handle_screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    price = context.user_data.get("last_price")
    if not price:
        await update.message.reply_text("Сначала выбери тариф /start")
        return
    try:
        await context.bot.forward_message(chat_id=ADMIN_ID, from_chat_id=update.effective_chat.id, message_id=update.message.message_id)
    except:
        pass
    keyboard = [[InlineKeyboardButton(f"✅ Получить файлы за {price} тг", callback_data=f"check_{price}")]]
    await update.message.reply_text("Чек получил! Нажми кнопку:", reply_markup=InlineKeyboardMarkup(keyboard))

app = Application.builder().token(TOKEN).connect_timeout(120).read_timeout(120).write_timeout(120).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(handle_buttons))
app.add_handler(MessageHandler(filters.PHOTO, handle_screenshot))
print("Bot started... ФИНАЛ ВЕРСИЯ")
app.run_polling()
