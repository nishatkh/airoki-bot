import os
import aiohttp
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, ContextTypes, filters
)

# Load environment variables (only needed for local testing or .env usage)
from dotenv import load_dotenv
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Optional - if using Replit
try:
    from keep_alive import keep_alive
    keep_alive()
except:
    pass

# Store user-specific personality
user_personality = {}

# Custom keyboard for gender selection
gender_keyboard = ReplyKeyboardMarkup(
    [["/boy", "/girl"]],
    resize_keyboard=True
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ Welcome to *Airoki*, your emotional AI chat buddy! 💬\n\n"
        "Would you like me to act like a *boy* or a *girl*?\n"
        "Use the buttons below or type /boy or /girl to choose.",
        reply_markup=gender_keyboard,
        parse_mode="Markdown"
    )

async def set_boy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_personality[update.effective_user.id] = (
        "You are a friendly, emotional, and funny boy. Respond with empathy, humor, and charm like a close male friend."
    )
    await update.message.reply_text("✅ I'm now acting like a boy! Let's chat.")

async def set_girl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_personality[update.effective_user.id] = (
        "You are a caring, emotional, and supportive girl. Talk warmly and kindly like a best friend or loving companion."
    )
    await update.message.reply_text("✅ I'm now acting like a girl! I'm here for you 💖")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    personality = user_personality.get(user_id, "You are a helpful, friendly AI with emotional expression.")
    user_message = update.message.text

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://openrouter.ai",
        "X-Title": "airoki-bot"
    }

    data = {
        "model": "google/gemini-2.0-flash-exp:free",
        "messages": [
            {"role": "system", "content": personality},
            {"role": "user", "content": user_message}
        ]
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data) as resp:
                response_json = await resp.json()
                reply = response_json["choices"][0]["message"]["content"]
        except Exception as e:
            print("Error:", e)
            reply = "😔 Sorry, I'm having trouble responding right now. Try again soon."

    await update.message.reply_text(reply)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("boy", set_boy))
    app.add_handler(CommandHandler("girl", set_girl))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("🤖 Airoki is live!")
    app.run_polling()
