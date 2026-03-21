# 🛒 ShopMaster - Smart Inventory & Sales Management System

## 📌 Project Overview
**ShopMaster** is a powerful, full-stack web application built using **Django** that helps businesses efficiently manage inventory, sales, expenses, and financial insights.

It is designed as an **all-in-one shop management solution**, featuring real-time analytics, role-based access control, invoicing, and an advanced AI-driven business insight engine to forecast future growth.

---

## ✨ Key Features

### 📊 Dashboard & Analytics
* **Real-time Metrics:** Instantly view Today's Sales 💰, Total Orders 📦, Inventory Value 📈, and Low Stock Alerts ⚠️.
* **Visualizations:** Weekly sales chart visualizations and recent transaction tracking.

### 🔐 Authentication & Authorization
* **Secure Login System:** Fully integrated Django authentication.
* **Role-Based Access Control (RBAC):**
  * 👑 **Admin/Owner:** Full administrative access (Financials, Staff Management, AI Insights).
  * 👨‍💼 **Staff/Cashier:** Restricted access (Processing sales and viewing inventory only).

### 📦 Inventory Management
* Add, update, and delete products within customized categories.
* Automated stock tracking with visual dashboard alerts.
* Tracks Cost Price vs. Selling Price for accurate profit calculation.
* Support for external product images.

### 💰 Sales & Billing
* Seamless Point-of-Sale (POS) interface with automatic stock deduction.
* Dynamic Invoice generation system 🧾.
* Comprehensive daily sales tracking and historical reporting.

### 📉 Financial Management
* Dedicated expense tracking module.
* Automated Monthly Profit & Loss calculations.
* Tracks critical metrics: Revenue, COGS (Cost of Goods Sold), Gross Profit, Net Profit, and Profit Margins.

### 👥 Entity Management
* Maintain organized databases for **Customers** 👤, **Suppliers** 🚚, and **Staff** 👨‍💼.

### 🤖 AI-Based Insights (Advanced Feature)
* **Smart Business Suggestions:** Automated alerts for customer growth, payroll insights, and supplier risks.
* **Future Prediction Engine:** Custom-built forecasting tool utilizing **Weighted Moving Average (WMA)** and Growth Rate analysis to predict future sales trends.

---

## 🛠️ Technology Stack

| Layer         | Technology |
|---------------|------------|
| **Backend** | Python, Django |
| **Frontend** | HTML5, CSS3, Bootstrap 5 |
| **Database** | SQLite3 (Configured for Development) |
| **UI Icons** | Font Awesome |
| **Charts** | Custom Chart Logic |
| **Version Control** | Git & GitHub |

---

## 📁 Clean Project Structure
```text
📦 ShopMaster
 ┣ 📂 core
 ┃ ┣ 📂 migrations/
 ┃ ┣ 📂 templates/
 ┃ ┃ ┣ 📂 core/
 ┃ ┃ ┃ ┣ 📜 home.html, inventory.html, sell_product.html, predictions.html ...
 ┃ ┃ ┗ 📂 registration/
 ┃ ┃   ┗ 📜 login.html, register.html
 ┃ ┣ 📂 templatetags/
 ┃ ┃ ┗ 📜 currency_filters.py
 ┃ ┣ 📜 admin.py
 ┃ ┣ 📜 forms.py
 ┃ ┣ 📜 models.py
 ┃ ┣ 📜 urls.py
 ┃ ┗ 📜 views.py
 ┣ 📂 shop_project/
 ┃ ┣ 📜 settings.py
 ┃ ┗ 📜 urls.py
 ┣ 📜 db.sqlite3
 ┣ 📜 manage.py
 ┗ 📜 requirements.txt
