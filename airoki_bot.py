import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, ContextTypes, filters
)

# === Hardcoded API Keys ===
TELEGRAM_BOT_TOKEN = "7002663931:AAEjyA5R-FfQ3N5zgFV0c1nO7-rMy-nj6Fg"
OPENROUTER_API_KEY = "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"

# Store user-specific personality in memory (reset on bot restart)
user_personality = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hi! I'm Airoki, your emotional AI companion.\n"
        "Would you like me to act like a boy or a girl?\n\n"
        "Type /boy or /girl to choose."
    )

async def set_boy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_personality[update.effective_user.id] = (
        "You are a friendly, emotional, and funny boy. Respond with empathy, jokes, and human warmth."
    )
    await update.message.reply_text("✅ Okay! I'm now acting like a boy. Let's talk!")

async def set_girl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_personality[update.effective_user.id] = (
        "You are a caring, emotional, and supportive girl. Respond like a best friend or loving companion."
    )
    await update.message.reply_text("✅ Alright! I'm now acting like a girl. I'm here for you!")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    personality = user_personality.get(user_id, "You are a friendly and supportive AI.")
    message = update.message.text

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://airoki.onrender.com",
        "X-Title": "AirokiBot"
    }

    payload = {
        "model": "google/gemini-2.0-flash-exp:free",
        "messages": [
            {"role": "system", "content": personality},
            {"role": "user", "content": message}
        ]
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers)
        reply = response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print("Error:", e)
        reply = "😞 Sorry, I’m having trouble replying right now."

    await update.message.reply_text(reply)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("boy", set_boy))
    app.add_handler(CommandHandler("girl", set_girl))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("✅ Airoki is running...")
    app.run_polling()


