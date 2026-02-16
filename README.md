 Backend API 

## Texnologiyalar
- Python & Django & DRF
- PostgreSQL
- Docker & Docker Compose
- JWT Authentication
- Swagger Documentation




#Docker ushin 
```bash
docker-compose up --build

Bul proekt — tolıq funkcionalǵa iye **E-commerce (Internet dúkan)** ushın jaratılǵan **RESTful API**.
Paydalanıwshılar ónimlerdi kóriwi, sebetke qosıwı hám buyırtpa beriwi múmkin. Administratorlar bolsa tolıq basqarıw huqıqına iye.

##  Texnologiyalar
- **Python 3.10** & **Django 4.x**
- **Django REST Framework (DRF)** — API jaratıw ushın.
- **PostgreSQL** — Maǵlıwmatlar bazası.
- **JWT (Simple JWT)** — Xavfsizlik hám Avtorizaciya.
- **Swagger (drf-spectacular)** — API dokumentaciya.
- **Docker** — Proektti konteynerde júrgiziw ushın.

---

## Funkcionallıq

### 👤 Paydalanıwshılar (Client)
- Dizimnen ótiw (Register) hám Kiriw (Login).
- Ónimlerdi kategoriyalar boyınsha izlew hám filterlew.
- **Sebet (Cart):** Ónim qosıw, sanın ózgertiw, óshiriw.
- **Buyırtpa (Order):** Sebetdegi ónimlerdi rásmiylestiriw (Checkout).
- **Izohlar (Reviews):** Satıp alınǵan ónimge baha beriw.

###  Administrator (Admin)
- Kategoriyalar hám Ónimlerdi (CRUD) basqarıw.
- Qoymadaǵı (Stock) ónimler sanın qadaǵalaw.
- Barlıq buyırtpalardı kóriw.


 Iske túsiriw (Installation)

Proektti kompyuterińizge júklep alıw:

```bash
git clone https://github.com/SizdinUsername/online-dukan-api.git
cd online-dukan-api

Virtual ortalıqtı jaratıw hám aktivlestiriw:
Bash
python -m venv venv
# Windows ushın:
venv\Scripts\activate
# Mac/Linux ushın:
source venv/bin/activate
Kitapxanalardı ornatıw:
code
Bash
pip install -r requirements.txt

Maǵlıwmatlar bazasın migraciyalas:
code
Bash
python manage.py migrate

Superuser (Admin) jaratıw:
code
Bash
python manage.py createsuperuser

Proektti iske túsiriw:
Bash
python manage.py runserver