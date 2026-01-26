from telegram import Update
from telegram.ext import (ApplicationBuilder, CommandHandler, ContextTypes)
import os
from dotenv import load_dotenv
import requests
import httpx

load_dotenv()

async def start(update, context):
    url = 'http://localhost:5000/api/subscription/add'
    chat_id = update.effective_chat.id
    args = context.args
    if not args:
        await update.message.reply_text(
            "❗ Please, subscribe via app."
        )
        return
    token = args[0]
    payload = {
        'token': token,
        'chat_id': chat_id
    }
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.post(url, json=payload)
        if response.json().get('success'):
            await update.message.reply_text(
                "✅ Telegram-сповіщення успішно підключені!"
            )
        else:
            await update.message.reply_text(
                "❌ Не вдалося підключити сповіщення.\n"
                "Можливо, токен недійсний або вже використаний."
            )
            print(response.json().get('error'))

    except Exception as e:
        await update.message.reply_text(
            "⚠️ Помилка сервера. Спробуйте пізніше."
        )
    


async def stop(update, context):
    chat_id = update.effective_chat.id
    url = f'http://localhost:5000/api/subscription/disable/{chat_id}'
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.patch(url)

        if response.status_code == 200 and response.json().get("success"):
            await update.message.reply_text(
                "🔕 Ви відписались від сповіщень.\n"
                "Можете знову підписатись через сайт."
            )
        else:
            await update.message.reply_text(
                "ℹ️ Ви не були підписані."
            )

    except Exception:
        await update.message.reply_text(
            "⚠️ Помилка сервера."
        )

async def ping(update, context):
    await update.message.reply_text('Pong')


BOT_TOKEN = os.getenv('BOT_TOKEN')
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler('start', start))
app.add_handler(CommandHandler('stop', stop))
app.add_handler(CommandHandler('ping', ping))

if __name__ == '__main__':
    print('Bot started')
    app.run_polling()