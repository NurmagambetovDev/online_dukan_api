# Python 3.10
FROM python:3.10

# Ishchi papka
WORKDIR /app

# Talablarni o'rnatish
COPY requirements.txt .
RUN pip install -r requirements.txt

# Kodni ko'chirish
COPY . .

# Portni ochish
EXPOSE 8000

# Serverni ishga tushirish
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]