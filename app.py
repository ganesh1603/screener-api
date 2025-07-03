from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import requests
import os

# Fetch secrets from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
ZAPIER_WEBHOOK_URL = os.getenv("ZAPIER_WEBHOOK_URL")

# Simple in-memory user tracking
user_state = {}

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_state[user_id] = "awaiting_stock"
    await update.message.reply_text("👋 Welcome! Please enter a stock name (e.g. TCS, INFY):")

# Handle stock input
async def handle_stock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    stock = update.message.text.strip().upper()

    if user_state.get(user_id) == "awaiting_stock":
        payload = {
            "stock_name": stock,
            "chat_id": user_id
        }

        try:
            requests.post(ZAPIER_WEBHOOK_URL, json=payload)
            await update.message.reply_text(f"📊 Analyzing *{stock}*... please wait!", parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text("❌ Failed to send data to Zapier.")

        user_state[user_id] = None
    else:
        await update.message.reply_text("❗ Please type /start to begin.")

# Main runner
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_stock))
    app.run_polling()

if __name__ == "__main__":
    main()
