import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# ========= CONFIG =========
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL = os.getenv("MODEL", "openai/gpt-3.5-turbo")   # default model

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# ========= OPENROUTER WRAPPER =========
def ask_openrouter(prompt: str) -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        res = requests.post(url, headers=headers, json=payload, timeout=60)
        res.raise_for_status()
        data = res.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ OpenRouter API error: {e}"

# ========= HANDLERS =========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hey! I'm powered by OpenRouter. Ask me anything!")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    reply_text = ask_openrouter(user_message)
    await update.message.reply_text(reply_text)

# ========= MAIN =========
def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("✅ Bot is running with OpenRouter...")
    app.run_polling()

if __name__ == "__main__":
    main()