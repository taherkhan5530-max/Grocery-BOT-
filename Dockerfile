FROM python:3.9-slim
WORKDIR /app

# রিকোয়ারমেন্টস ইনস্টল
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# আপনার সব কোড ফাইল কপি (.py, config.py, handlers ইত্যাদি)
COPY . .

# Render এই পোর্টে এক্সপোজ করবে
EXPOSE 10000

# Gunicorn এর বদলে সরাসরি main.py ফাইলটি চালানো হচ্ছে
CMD ["python", "main.py"]
