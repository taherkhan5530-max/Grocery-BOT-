# main.py

import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from config import TELEGRAM_BOT_TOKEN, AUTHORIZED_ADMIN_IDS # <--- AUTHORIZED_ADMIN_IDS ইমপোর্ট করা হয়েছে
from handlers_admin import add_product_handler, delete_product_handler # <--- delete_product_handler ইমপোর্ট করা হয়েছে

# Logging সেটআপ
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# সাধারণ /start কমান্ড হ্যান্ডলার
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """বট শুরু হলে ওয়েলকাম মেসেজ দেয়।"""
    # ensure effective_user is not None before accessing id
    if update.effective_user: 
        user_id = update.effective_user.id
    else:
        # If user is somehow None (rare), assume not authorized
        user_id = 0 
    
    # আইডি স্ট্রিং হিসাবে কনভার্ট করা
    # NOTE: AUTHORIZED_ADMIN_IDS সাধারণত int বা str হিসাবে থাকতে পারে। এখানে user_id int।
    # যদি config.py তে ADMIN_IDS স্ট্রিং থাকে, তাহলে user_id কে স্ট্রিং এ কনভার্ট করুন।
    # আমরা ধরে নিচ্ছি config.py তে এটি integer সেট করা আছে, যা ভালো অভ্যাস।
    
    if user_id in AUTHORIZED_ADMIN_IDS:
        message = (
            "স্বাগতম! আপনি একজন অনুমোদিত অ্যাডমিন।\n"
            "প্রোডাক্ট যোগ করার জন্য `/addproduct` এবং ডিলিট করার জন্য `/deleteproduct` ব্যবহার করুন।"
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
    application.add_handler(add_product_handler)        # ✅ /addproduct কনভার্সেশন হ্যান্ডলার
    application.add_handler(delete_product_handler)     # ✅ /deleteproduct কনভার্সেশন হ্যান্ডলার

    # বট শুরু
    logger.info("Bot started successfully. Polling for updates...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
