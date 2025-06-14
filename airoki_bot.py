import os
import aiohttp
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, ContextTypes, filters
)
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
SITE_URL = "https://airoki-chatbot.vercel.app"  # optional
SITE_NAME = "AirokiBot"  # optional

user_personality = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome! I'm *Airoki*, your emotional AI friend.\n\n"
        "Do you want me to behave like a boy or a girl?\n\n"
        "👉 Type /boy or /girl to choose!",
        parse_mode='Markdown'
    )

async def set_boy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_personality[update.effective_user.id] = (
        "You're a friendly, emotional, and funny boy. Always respond with empathy, a bit of humor, and human-like warmth."
    )
    await update.message.reply_text("✅ I'm now acting like a boy. Let's chat!")

async def set_girl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_personality[update.effective_user.id] = (
        "You're a caring, emotional, and sweet girl. Respond like a loving friend or companion with warmth and support."
    )
    await update.message.reply_text("✅ I'm now acting like a girl. I'm here for you!")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    personality = user_personality.get(user_id, "You are a friendly and supportive AI.")
    user_msg = update.message.text

    prompt = [
        {"role": "system", "content": personality},
        {"role": "user", "content": user_msg}
    ]

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": SITE_URL,
        "X-Title": SITE_NAME
    }

    payload = {
        "model": "google/gemini-2.0-flash-exp:free",
        "messages": prompt
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload) as resp:
                data = await resp.json()
                reply = data['choices'][0]['message']['content']
    except Exception as e:
        print("Error:", e)
        reply = "😞 Sorry, I couldn't get a reply right now."

    await update.message.reply_text(reply)

async def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("boy", set_boy))
    app.add_handler(CommandHandler("girl", set_girl))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("✅ Airoki is running...")
    await app.run_polling()
    
if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
