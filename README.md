# 🛒 E-commerce Backend (Django + Stripe)

This project is a simple **E-commerce backend API** built with **Django Rest Framework (DRF)**.  
It allows users to browse products, manage a shopping cart, place orders, and complete payments using **Stripe**.

---

## 📌 Features

- **User Authentication**
  - Register, Login, Logout (JWT or Token-based)
- **Products**
  - List, Create, Update, Delete (restricted to admin for write operations)
- **Cart**
  - Add items to cart
  - Update & remove items
  - View current user's cart
- **Orders**
  - Place orders from cart
  - Track order status (`Pending`, `Successful`, `Failed`)
- **Payments (Stripe Integration)**
  - Create Stripe **PaymentIntent** when placing an order
  - Use **Stripe Webhooks** to confirm payments
  - Update `Order` status automatically after payment is confirmed

---

## 🛠️ Tech Stack

- **Backend:** Django, Django REST Framework
- **Payments:** Stripe API
- **Database:** SQLite (default, can switch to PostgreSQL/MySQL)
- **Auth:** Django Rest Framework Authentication / JWT
- **Environment Management:** python-dotenv

---

## ⚙️ Installation & Setup

### 1. Clone the repository

git clone https://github.com/your-username/ecommerce-backend.git
cd e-com

### 2. Create and acticate virtual Environment
python -m venv .env
source .env/bin/activate   # Linux/Mac
.env\Scripts\activate      # Windows

### 3. Install dependencies
pip install -r requirements.txt

### 4. Configure environment variables
Create a file named .env in the project root:
SECRET_KEY=your_django_secret_key
DEBUG=True

STRIPE_SECRET_KEY=sk_test_1234567890
STRIPE_PUBLIC_KEY=pk_test_1234567890
STRIPE_ENDPOINT_SECRET=whsec_1234567890

### 5. Run migrations
python manage.py migrate

### 6. Start development server
python manage.py runserver


## Stripe Integration

### 1. Create a PaymentIntent

When an order is placed, the backend generates a Stripe PaymentIntent:

```bash intent = stripe.PaymentIntent.create(
    amount=order.total_amount * 100,  # in cents
    currency="usd",
    metadata={"order_id": order.id},
)
```



The client_secret is sent to the frontend for the user to complete the payment.

### 2. Handle Stripe Webhooks

Stripe sends events to /stripe/webhook/.
Your backend verifies the event and updates the order status:

payment_intent.succeeded → mark order as Successful

payment_intent.payment_failed → mark order as Failed

## Testing Stripe Locally

Install Stripe CLI -> https://stripe.com/docs/stripe-cli

### Login:

stripe login


### Forward webhooks to your local server:

stripe listen --forward-to localhost:8000/stripe/webhook/


### Trigger a test payment event:

stripe trigger payment_intent.succeeded

## Project Structure
e-com/
│── shop/           # App: products, cart, orders, authentication
│── store/               # Django project folder 
│── manage.py
│── README.md
│── requirements.txt
│── shop.http         # make requests to the server using Visual studio's REST client extension

## Authentication

Endpoints use DRF Authentication / JWT.

Only admin users can create, update, or delete products.

Regular users can browse products, manage their cart, and place orders.

