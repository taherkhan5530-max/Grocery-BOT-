# main.py

import logging
from telegram.ext import Application, CommandHandler
from config import TELEGRAM_BOT_TOKEN
from handlers_admin import add_product_handler

# Logging সেটআপ
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# সাধারণ /start কমান্ড হ্যান্ডলার
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """বট শুরু হলে ওয়েলকাম মেসেজ দেয়।"""
    user_id = update.effective_user.id
    if user_id in AUTHORIZED_ADMIN_IDS:
        message = (
            "স্বাগতম! আপনি একজন অনুমোদিত অ্যাডমিন।\n"
            "প্রোডাক্ট যোগ করার জন্য `/addproduct` ব্যবহার করুন।"
        )
    else:
        message = "স্বাগতম! আপনি একটি ওয়েবসাইট ম্যানেজমেন্ট বটে সংযুক্ত হয়েছেন। তবে আপনার অ্যাডমিন অনুমতি নেই।"
        
    await update.message.reply_text(message)

def main():
    """বট শুরু করার মূল ফাংশন।"""
    logger.info("Starting bot...")
    
    # অ্যাপ্লিকেশন তৈরি
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # কমান্ড হ্যান্ডলার যোগ করা
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(add_product_handler) # অ্যাডমিন কনভার্সেশন হ্যান্ডলার

    # বট শুরু
    logger.info("Bot started successfully. Polling for updates...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
