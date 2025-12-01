# handlers_admin.py

from telegram import Update, ForceReply
from telegram.ext import (
    CommandHandler, MessageHandler, filters,
    ConversationHandler, ContextTypes
)
import requests
import logging
from config import (
    # config.py তে WEBSITE_API_BASE_URL সেট করা আছে ধরে নেওয়া হলো
    WEBSITE_API_UPLOAD_ENDPOINT, WEBSITE_SECRET_TOKEN, AUTHORIZED_ADMIN_IDS
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Conversation States (ডিলিট করার জন্য নতুন স্টেট যোগ করা হয়েছে)
PRODUCT_NAME, PRODUCT_PRICE, PRODUCT_DESCRIPTION, PRODUCT_PHOTO = range(4)
PRODUCT_ID_TO_DELETE = 4 # ডিলিট ফ্লো-র জন্য স্টেট

# config থেকে API Base URL আমদানি করার জন্য একটি ডামি ভেরিয়েবল
# NOTE: যদি config.py তে WEBSITE_API_BASE_URL না থাকে, তবে এই লাইনটি ত্রুটি দেবে।
try:
    from config import WEBSITE_API_BASE_URL
except ImportError:
    # যদি config.py তে না থাকে, তবে একটি ফলব্যাক URL ব্যবহার করুন
    WEBSITE_API_BASE_URL = "https://your-site.replit.dev/api/" 
    logger.warning("WEBSITE_API_BASE_URL not found in config. Using fallback.")


# ১. অথরাইজেশন চেক
def is_admin(user_id):
    """চেক করে ইউজার অ্যাডমিন কিনা।"""
    return user_id in AUTHORIZED_ADMIN_IDS

# কনভার্সেশন বাতিল করার ফাংশন (উভয় কনভার্সেশনের জন্য ব্যবহৃত হবে)
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ইউজার ম্যানুয়ালি কনভার্সেশন বাতিল করলে।"""
    context.user_data.clear()
    await update.message.reply_text("বর্তমান প্রক্রিয়া বাতিল করা হয়েছে।")
    return ConversationHandler.END


# =========================================================================
#                   /addproduct কার্যকারিতা
# =========================================================================

# ২. /addproduct কমান্ড শুরু (আগের মতোই)
async def start_add_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """কনভার্সেশন শুরু করে এবং অথরাইজেশন চেক করে।"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        logger.warning(f"Unauthorized access attempt by user {user_id} for /addproduct.")
        await update.message.reply_text("দুঃখিত, আপনার এই কমান্ড ব্যবহারের অনুমতি নেই।")
        return ConversationHandler.END

    await update.message.reply_text(
        "নতুন প্রোডাক্ট যোগ করার প্রক্রিয়া শুরু হলো।\n"
        "প্রোডাক্টের **নাম** লিখুন:",
        reply_markup=ForceReply(selective=True)
    )
    return PRODUCT_NAME

# ৩. নাম গ্রহণ (আগের মতোই)
async def get_product_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """প্রোডাক্টের নাম সেভ করে এবং দাম জানতে চায়।"""
    context.user_data['name'] = update.message.text
    await update.message.reply_text("প্রোডাক্টের **দাম** (শুধু সংখ্যায়) লিখুন:")
    return PRODUCT_PRICE

# ৪. দাম গ্রহণ (আগের মতোই)
async def get_product_price(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """প্রোডাক্টের দাম সেভ করে এবং বর্ণনা জানতে চায়।"""
    try:
        price = float(update.message.text.strip())
        context.user_data['price'] = price
        await update.message.reply_text("প্রোডাক্টের একটি সংক্ষিপ্ত **বর্ণনা** লিখুন:")
        return PRODUCT_DESCRIPTION
    except ValueError:
        await update.message.reply_text("দয়া করে শুধুমাত্র সংখ্যায় দাম লিখুন। আবার চেষ্টা করুন:")
        return PRODUCT_PRICE

# ৫. বর্ণনা গ্রহণ (আগের মতোই)
async def get_product_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """প্রোডাক্টের বর্ণনা সেভ করে এবং ছবি আপলোড করতে বলে।"""
    context.user_data['description'] = update.message.text
    await update.message.reply_text("এবার প্রোডাক্টের **ছবিটি** আপলোড করুন।")
    return PRODUCT_PHOTO

# ৬. ছবি গ্রহণ ও API-তে পাঠানো (সমাপ্তি) (আগের মতোই)
async def get_product_photo_and_finish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ছবি সেভ করে, ওয়েবসাইটে API-এর মাধ্যমে ডেটা পাঠায় এবং কনভার্সেশন শেষ করে।"""
    
    # লোডিং মেসেজ
    await update.message.reply_text("ছবি পেয়েছি! প্রোডাক্টটি ওয়েবসাইটে আপলোড করা হচ্ছে...")

    try:
        # ছবিটি ডাউনলোড করা
        photo_file = await update.message.photo[-1].get_file()
        photo_data = await photo_file.download_as_bytes()

        # API Payload তৈরি
        payload = {
            'name': context.user_data['name'],
            'price': context.user_data['price'],
            'description': context.user_data['description'],
            'api_token': WEBSITE_SECRET_TOKEN # সিকিউরিটির জন্য টোকেন
        }
        
        # files ডিকশনারি তৈরি
        files = {
            # ('filename', binary_data, 'mime_type')
            'product_image': (f"{context.user_data['name']}.jpg", photo_data, 'image/jpeg')
        }

        # API-তে POST রিকোয়েস্ট পাঠানো
        response = requests.post(
            WEBSITE_API_UPLOAD_ENDPOINT,
            data=payload,
            files=files,
            timeout=10 # ১০ সেকেন্ডের মধ্যে রেসপন্স না পেলে বন্ধ
        )
        
        if response.status_code in [200, 201]:
            await update.message.reply_text(
                f"✅ **সফল!** প্রোডাক্ট '{context.user_data['name']}' ওয়েবসাইটে যোগ করা হয়েছে।\n"
                f"সার্ভার রেসপন্স: {response.text[:100]}..."
            )
        else:
            await update.message.reply_text(
                f"❌ **দুঃখিত**, প্রোডাক্ট যোগ করা যায়নি। ওয়েবসাইটের ত্রুটি কোড: {response.status_code}\n"
                f"রেসপন্স: {response.text}"
            )

    except requests.exceptions.RequestException as e:
        logger.error(f"API Request failed: {e}")
        await update.message.reply_text(f"❌ API-তে যোগাযোগ ব্যর্থ হয়েছে। অনুগ্রহ করে সার্ভার এবং কনফিগারেশন চেক করুন।")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        await update.message.reply_text(f"❌ একটি অপ্রত্যাশিত ত্রুটি হয়েছে: {e}")

    # ডেটা পরিষ্কার করা এবং কনভার্সেশন শেষ করা
    context.user_data.clear()
    return ConversationHandler.END


# কনভার্সেশন হ্যান্ডলার তৈরি
add_product_handler = ConversationHandler(
    entry_points=[CommandHandler("addproduct", start_add_product)],
    states={
        PRODUCT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_product_name)],
        PRODUCT_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_product_price)],
        PRODUCT_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_product_description)],
        PRODUCT_PHOTO: [MessageHandler(filters.PHOTO, get_product_photo_and_finish)],
    },
    # যেকোনো ধাপে /cancel কমান্ড দিলে
    fallbacks=[CommandHandler('cancel', cancel)] 
)


# =========================================================================
#                   /deleteproduct কার্যকারিতা (নতুন যোগ)
# =========================================================================

async def start_delete_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """প্রোডাক্ট ডিলিট করার কনভার্সেশন শুরু করে এবং অথরাইজেশন চেক করে।"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("দুঃখিত, আপনার এই কমান্ড ব্যবহারের অনুমতি নেই।")
        return ConversationHandler.END

    await update.message.reply_text(
        "কোন প্রোডাক্টটি ডিলিট করতে চান? দয়া করে প্রোডাক্টের **নাম** অথবা **ID** লিখুন:",
        reply_markup=ForceReply(selective=True)
    )
    return PRODUCT_ID_TO_DELETE

async def get_product_id_and_finish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """প্রোডাক্ট ID/নাম গ্রহণ করে এবং ডিলিট API-তে পাঠায়।"""
    identifier = update.message.text.strip()
    await update.message.reply_text(f"প্রোডাক্ট '{identifier}' ডিলিট করার জন্য ওয়েবসাইটে অনুরোধ পাঠানো হচ্ছে...")

    try:
        # API Payload তৈরি
        payload = {
            'identifier': identifier, # নাম বা ID
            'api_token': WEBSITE_SECRET_TOKEN
        }
        
        # API-তে POST রিকোয়েস্ট পাঠানো (ডিলিট API ব্যবহার করে)
        # ⚠️ আপনার ওয়েবসাইটে এই URL-এ DELETE লজিক তৈরি করতে হবে
        response = requests.post( 
            WEBSITE_API_BASE_URL + "delete_product",
            data=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            await update.message.reply_text(
                f"✅ **সফল!** প্রোডাক্ট '{identifier}' ওয়েবসাইট থেকে ডিলিট করা হয়েছে।\n"
                f"সার্ভার রেসপন্স: {response.text[:100]}..."
            )
        else:
            await update.message.reply_text(
                f"❌ **দুঃখিত**, প্রোডাক্ট ডিলিট করা যায়নি। ত্রুটি কোড: {response.status_code}\n"
                f"রেসপন্স: {response.text}"
            )

    except requests.exceptions.RequestException as e:
        logger.error(f"Delete API Request failed: {e}")
        await update.message.reply_text(f"❌ API-তে যোগাযোগ ব্যর্থ হয়েছে। অনুগ্রহ করে সার্ভার চেক করুন।")
    except Exception as e:
        logger.error(f"An unexpected error occurred during delete: {e}")
        await update.message.reply_text(f"❌ একটি অপ্রত্যাশিত ত্রুটি হয়েছে: {e}")

    context.user_data.clear()
    return ConversationHandler.END


# ডিলিট কনভার্সেশন হ্যান্ডলার তৈরি
delete_product_handler = ConversationHandler(
    entry_points=[CommandHandler("deleteproduct", start_delete_product)],
    states={
        PRODUCT_ID_TO_DELETE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_product_id_and_finish)],
    },
    fallbacks=[CommandHandler('cancel', cancel)] 
)
