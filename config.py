# config.py

# আপনার দেওয়া টেলিগ্রাম বট টোকেন
TELEGRAM_BOT_TOKEN = "8334178606:AAFUnL3NRKOgWnqvuSdjZBphV53n6mme0ts"

# আপনার ওয়েবসাইটের API কনফিগারেশন (এইগুলো অবশ্যই পরিবর্তন করুন)
WEBSITE_API_BASE_URL = "https://your-website.com/api/"
WEBSITE_API_UPLOAD_ENDPOINT = WEBSITE_API_BASE_URL + "add_product" 
WEBSITE_SECRET_TOKEN = "YOUR_SUPER_SECURE_API_KEY_12345" # আপনার ওয়েবসাইটের গোপন API Key

# অনুমোদিত অ্যাডমিন ইউজারের Telegram ID (আপনার দেওয়া Chat ID)
# এই আইডিগুলোই কেবল ওয়েবসাইট ম্যানেজমেন্ট কমান্ড চালাতে পারবে
AUTHORIZED_ADMIN_IDS = [5939435550]
