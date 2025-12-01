# config.py

# ==================================
# Telegram Bot Configuration
# ==================================
# আপনার দেওয়া বট টোকেন বসানো হয়েছে
TELEGRAM_BOT_TOKEN = "8334178606:AAFUnL3NRKOgWnqvuSdjZBphV53n6mme0ts" 

# আপনার দেওয়া চ্যাট আইডি (5939435550) অ্যাডমিন আইডি হিসেবে ব্যবহার করা হয়েছে।
ADMIN_IDS = [5939435550] 
# আগের ডামি অ্যাডমিন আইডিগুলো (123456789, 987654321) বাদ দেওয়া হয়েছে।

# যদি DB_CHANNEL_ID আপনার চ্যানেলের আইডি হয়, তবে এটি ঠিক আছে।
# যদি এটি আপনার নিজের চ্যাট আইডি হয়, তবে এটিকে নেগেটিভ (-100) হতে হবে না। 
# ধরে নেওয়া হলো 5939435550 হলো আপনার ব্যক্তিগত চ্যাট আইডি এবং আপনি এটিই লগিং এর জন্য ব্যবহার করবেন।
DB_CHANNEL_ID = 5939435550 


# ==================================
# API Keys (For Image Processing)
# ==================================
# ⚠️ আপনাকে এই কীগুলি বসাতে হবে।
RBG_API = "YOUR_REMOVE_BG_API_KEY_XYZ" 
SE_API_USER = "YOUR_SIGHTENGINE_API_USER_XYZ" 
SE_API_SECRET = "YOUR_SIGHTENGINE_API_SECRET_XYZ" 


# ==================================
# Website Product Management API Config
# ==================================
# আপনার Flask ওয়েবসাইটের রুট API URL
WEBSITE_API_BASE_URL = "https://your-site.replit.dev/api/" 
# প্রোডাক্ট যোগ করার সম্পূর্ণ URL
WEBSITE_API_UPLOAD_ENDPOINT = WEBSITE_API_BASE_URL + "add_product"
# সিকিউরিটির জন্য বটের সাথে ওয়েবসাইটের গোপন টোকেন
WEBSITE_SECRET_TOKEN = "bazerwala_secret_7a9c2b8f4e1d6a3c9e2f5b8a1d4c7e0f"

# PRODUCT API এর জন্য AUTHORIZED_ADMIN_IDS ব্যবহার করা হবে
AUTHORIZED_ADMIN_IDS = ADMIN_IDS
