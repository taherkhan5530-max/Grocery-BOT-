FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
# অতিরিক্ত প্রয়োজনীয়তা যোগ করুন: gunicorn
RUN pip install --no-cache-dir -r requirements.txt gunicorn 
COPY . .
EXPOSE 10000
# Flask/API অ্যাপ্লিকেশন হোস্ট করার জন্য Gunicorn ব্যবহার করুন
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
