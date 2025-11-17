import config
import handlers_user
import handlers_admin
import db_helpers  # db_helpers আমদানি করা হয়েছে

import os
import asyncio
import telegram
import urllib.request
from flask import Flask, request

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    PicklePersistence,
    filters
)
from telegram.constants import ChatType

# --- Flask App Init ---
# আপনার bot (2).py ফাইলের মতো Flask সার্ভার তৈরি করুন
server = Flask(__name__)

def setup_bot():
    """
    বট অ্যাপ্লিকেশন তৈরি করে এবং সমস্ত হ্যান্ডলার যোগ করে।
    """
    
    # বট রিস্টার্ট হলেও ডাটা মনে রাখার জন্য পারসিস্টেন্স অবজেক্ট তৈরি করুন
    persistence = PicklePersistence(filepath='bot_persistence')

    # অ্যাপ্লিকেশন বিল্ডার তৈরি করুন
    application = (Application.builder()
        .token(config.BOT_TOKEN)
        .persistence(persistence)
        .build())

    # --- ইউজার হ্যান্ডলার যোগ করুন ---
    application.add_handler(CommandHandler("start", handlers_user.start_command, filters=filters.ChatType.PRIVATE))
    application.add_handler(CommandHandler("help", handlers_user.help_command, filters=filters.ChatType.PRIVATE))
    application.add_handler(CommandHandler("status", handlers_user.status_command, filters=filters.ChatType.PRIVATE))
    
    # প্রাইভেট চ্যাটে আসা ফটোগুলো হ্যান্ডেল করার জন্য
    application.add_handler(MessageHandler(filters.PHOTO & filters.ChatType.PRIVATE, handlers_user.handle_photo))
    
    # --- কলব্যাক (বাটন ক্লিক) হ্যান্ডলার ---
    application.add_handler(CallbackQueryHandler(handlers_user.show_credits_callback, pattern="^show_credits$"))
    application.add_handler(CallbackQueryHandler(handlers_user.handle_conversion, pattern="^convert_"))
    
    # --- অ্যাডমিন হ্যান্ডলার যোগ করুন ---
    application.add_handler(CommandHandler("ban", handlers_admin.ban_user))
    application.add_handler(CommandHandler("unban", handlers_admin.unban_user))
    application.add_handler(CommandHandler("sendmsg", handlers_admin.send_message_to_user))
    application.add_handler(CommandHandler("sendmsgall", handlers_admin.send_message_all))

    # --- গ্রুপ বা চ্যানেলের মেসেজ উপেক্ষা করার হ্যান্ডলার ---
    application.add_handler(MessageHandler(
        filters.ChatType.GROUP | filters.ChatType.SUPERGROUP | filters.ChatType.CHANNEL,
        handlers_user.ignore_non_private_chats
    ))

    return application

# --- গ্লোবাল বট অ্যাপ্লিকেশন ---
# অ্যাপ্লিকেশনটি একবার তৈরি করে রাখুন
application = setup_bot()

# --- Webhook Routes (bot (2).py এর মতো) ---

@server.route('/' + config.BOT_TOKEN, methods=['POST'])
def webhook_update():
    """
    টেলিগ্রাম থেকে আসা প্রতিটি আপডেট হ্যান্ডেল করে।
    """
    update_json = request.get_json()
    update = telegram.Update.de_json(update_json, application.bot)
    
    # Flask (Sync) থেকে PTB (Async) তে আপডেটটি প্রসেস করার জন্য পাঠানো হচ্ছে
    try:
        # একটি রানিং ইভেন্ট লুপে টাস্ক হিসেবে যোগ করার চেষ্টা করুন
        loop = asyncio.get_running_loop()
        loop.create_task(application.process_update(update))
    except RuntimeError:
        # যদি কোনো লুপ না চলে (যেমন gunicorn এর sync worker এ),
        # প্রতিটি আপডেটের জন্য একটি নতুন লুপে রান করুন।
        asyncio.run(application.process_update(update))
            
    return "ok", 200

@server.route("/")
def set_webhook():
    """
    বট চালু হলে স্বয়ংক্রিয়ভাবে টেলিগ্রামকে ওয়েবহুক সেট করতে বলে।
    (এটি আপনার bot (2).py ফাইল থেকে নেওয়া)
    """
    # RENDER_EXTERNAL_HOSTNAME একটি এনভায়রনমেন্ট ভেরিয়েবল যা Render.com এ স্বয়ংক্রিয়ভাবে সেট হয়
    # আপনি যদি অন্য কোনো প্ল্যাটফর্ম ব্যবহার করেন, এটি পরিবর্তন করতে হতে পারে
    host_url = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
    if not host_url:
        print("WARNING: RENDER_EXTERNAL_HOSTNAME not set. Webhook may fail.")
        # একটি ফলব্যাক ইউআরএল দিন বা শুধু রুট ডোমেইন ব্যবহার করুন
        # এই অংশটি আপনার হোস্টিং প্ল্যাটফর্মের উপর নির্ভরশীল
        return "Webhook setup failed: Host URL not found.", 500

    bot_url = f"https://{host_url}/{config.BOT_TOKEN}"
    api_url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/"
    
    req = urllib.request.Request(api_url + "setWebhook?url=" + bot_url)
    try:
        urllib.request.urlopen(req)
        print(f"Webhook set successfully to {bot_url}")
        return "Webhook set!", 200
    except Exception as e:
        print(f"Webhook setup error: {e}")
        return f"Webhook error: {e}", 500

# --- Main Execution ---
if __name__ == "__main__":
    
    # বট চালু করার আগে চেক করুন সব এনভায়রনমেন্ট ভেরিয়েবল ঠিক আছে কিনা
    if not all([config.BOT_TOKEN, config.ADMIN_IDS, config.DB_C_ID, config.RBG_API, config.SE_API_USER, config.SE_API_SECRET]):
        print("ERROR: Environment variables are not set correctly. Please check.")
        print("Missing one or more of: BOT_TOKEN, ADMIN_IDS, DB_C_ID, RBG_API, SE_API_USER, SE_API_SECRET")
    else:
        print("Configuration loaded successfully. Starting webhook server...")
        # Flask সার্ভার চালু করুন (Gunicorn এটি চালাবে)
        # Polling এর পরিবর্তে, আমরা এখন Flask সার্ভার রান করছি
        port = int(os.environ.get("PORT", 10000))
        server.run(host="0.0.0.0", port=port)
