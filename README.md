# Personal Finance Tracker 💰

A modern, secure, and user-friendly personal finance management system built with **Django** and **Django REST Framework**.  
This application allows users to **track income, expenses, budgets, and account balances** in one central dashboard,  
with **built-in analytics**, **JWT authentication**, and **CSV export features**.

---

## 📌 Features

### 🔐 Authentication & Security
- **JWT Authentication** for secure login & API access.
- User-specific data isolation — each user only sees their own accounts, categories, and transactions.

### 💵 Accounts & Balances
- Create and manage multiple bank accounts.
- Track current account balances in real-time.

### 📂 Categories
- Organize transactions into categories with colors for better visualization.
- Custom category creation per user.

### 📑 Transactions
- Add income & expenses with date, description, category, and account.
- Filter by **date range** and **category**.
- Export filtered transactions as **CSV** for reports.

### 📊 Dashboard & Analytics
- **Monthly summary** with total income, expenses, and category breakdown.
- **Daily trends** showing income and expenses for the month.
- **Budget overview** with limit, usage, and percentage used.
- **Card summary API** for front-end integration.

### 📆 Budgets
- Create monthly budgets with spending limits.
- Automatic calculation of used amount and remaining limit.

### 📤 Export & Reports
- Export transaction history to CSV (UTF-8, Excel-compatible).
- Filter exports by date and category.

---

## ⚙️ Technology Stack

- **Backend:** Django, Django REST Framework
- **Database:** SQLite (default, can be changed to PostgreSQL/MySQL)
- **Auth:** JWT via `djangorestframework-simplejwt`
- **API Docs:** drf-spectacular (Swagger/OpenAPI)
- **Frontend:** Django Templates (can be replaced with React, Vue, etc.)
- **Other:** CSV Export, Date Filtering, Custom Permissions

---


2️⃣ Create a virtual environment & install dependencies
bash
Copy
Edit
python -m venv .venv
.venv\Scripts\activate    # On Windows
pip install -r requirements.txt

3️⃣ Apply migrations & create a superuser
bash
Copy

## Screenshots

![Dashboard Screenshot](https://drive.google.com/uc?export=view&id=1qU_uJh-VSagNeaMKE52qx-gQpXUU6k4y)


Edit
python manage.py migrate
python manage.py createsuperuser

4️⃣ Run the server
bash
Copy
Edit
python manage.py runserver
