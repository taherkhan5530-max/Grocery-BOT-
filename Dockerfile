FROM python:3.9-slim
WORKDIR /app
requirements.txt কপি করুন এবং ইন্সটল করুন
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
বাকি সব সোর্স কোড কপি করুন
COPY . .
আপনার bot (2).py ফাইলের মতো পোর্ট এক্সপোজ করুন
EXPOSE 10000
Gunicorn দিয়ে 'main.py' ফাইলের 'server' নামক Flask অ্যাপটি চালান
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "main:server"]
