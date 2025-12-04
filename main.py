import os
import telebot

import db
import handlers

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set")

ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))
ADMIN_IDS = [ADMIN_ID] if ADMIN_ID != 0 else []

BOT_TOKEN = "8241908340:AAHGKanrbnNxTRCQVKITiglZwLtjA96WRRw"
ADMIN_IDS = [6000971026]
REQUIRED_CHANNEL = "@BTBB_ERA"
CONTACT_BOT = "@Govindchoudharybot"

bot = telebot.TeleBot(BOT_TOKEN)

handlers.setup_handlers(bot, ADMIN_IDS, REQUIRED_CHANNEL, CONTACT_BOT)

if __name__ == "__main__":
    print("Bot started…")
    bot.infinity_polling()
