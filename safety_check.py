# app.py বা server.py

from flask import Flask, request, jsonify
import os
import uuid
import sqlite3 # <--- SQLite ইমপোর্ট করা হয়েছে

# ফাইলপথ
WEBSITE_SECRET_TOKEN = "bazerwala_secret_7a9c2b8f4e1d6a3c9e2f5b8a1d4c7e0f"
UPLOAD_FOLDER = 'static/uploads'
DATABASE_FILE = 'products.db' # ডেটাবেসের নাম

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# নিশ্চিত করুন আপলোড ফোল্ডারটি বিদ্যমান
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# =========================================================================
#                          ডেটাবেস ফাংশন
# =========================================================================

def get_db_connection():
    """ডেটাবেসের সাথে সংযোগ তৈরি করে।"""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row # কলামের নাম ব্যবহার করে ডেটা অ্যাক্সেসের জন্য
    return conn

def init_db():
    """ডেটাবেস এবং প্রোডাক্ট টেবিল তৈরি করে (যদি না থাকে)।"""
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            description TEXT,
            image_url TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# অ্যাপ শুরু হওয়ার আগে ডেটাবেস ইনিশিয়ালাইজ করুন
init_db()

# =========================================================================
#                     /api/add_product (প্রোডাক্ট যোগ)
# =========================================================================

# (add_product_api ফাংশনটি নিচে দেখুন)
