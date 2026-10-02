# FinTrack

FinTrack is a personal finance and portfolio management web application built with Python, Django REST Framework, and MySQL.

It allows users to manage their income and expenses, organize transactions using categories, track investments, and view financial summaries from a centralized dashboard.

---

## Features

### User Management
- User registration
- User login and logout
- JWT authentication for API access
- User profile management
- Profile picture upload
- Profile picture deletion

### Transaction Management
- Add income and expenses
- View transactions
- Edit transactions
- Delete transactions
- Transaction categories
- Custom categories for individual users
- Search transactions by description
- Filter transactions by transaction type
- Sort transactions by amount or date
- Pagination through the transaction API

### Investment Management
- Add investments
- View investments
- Edit investments
- Delete investments
- Live market price tracking
- Investment current value calculation
- Profit/loss calculation
- Return percentage calculation
- Overall investment summary

### Financial Analytics
- Total income
- Total expenses
- Current balance
- Category-wise expense summary
- Monthly income and expense summary
- Monthly net balance
- Investment portfolio summary

### Security and Validation
- Authentication required for protected API endpoints
- User-specific transaction access
- User-specific investment access
- Ownership checks for update and delete operations
- Category ownership validation
- Transaction amount validation
- Transaction type validation
- Investment quantity validation
- Investment buy-price validation
- Required-field validation

---

## Technologies Used

- Python
- Django
- Django REST Framework
- MySQL
- JWT Authentication
- HTML
- CSS
- Git
- GitHub

---

## Project Structure

```text
FinTrack/
│
├── accounts/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── config/
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── static/
│   └── css/
│       └── style.css
│
├── templates/
│   ├── category_create.html
│   ├── dashboard.html
│   ├── investment_create.html
│   ├── investment_edit.html
│   ├── investments.html
│   ├── login.html
│   ├── profile.html
│   ├── profile_edit.html
│   ├── signup.html
│   ├── transaction_create.html
│   ├── transaction_edit.html
│   └── transactions.html
│
├── transactions/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── market_api.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── .gitignore
├── manage.py
└── README.md
```

---

## Main API Endpoints

### Authentication

```text
POST /api/token/
```

### Transactions

```text
GET    /transactions/
POST   /transactions/create/
GET    /transactions/<id>/
PUT    /transactions/<id>/update/
PATCH  /transactions/<id>/update/
DELETE /transactions/<id>/delete/

GET    /transactions/summary/
GET    /transactions/category-summary/
GET    /transactions/monthly-summary/
```

### Investments

```text
GET    /investments/
POST   /investments/create/
GET    /investments/<id>/
PUT    /investments/<id>/update/
PATCH  /investments/<id>/update/
DELETE /investments/<id>/delete/

GET    /investments/summary/
```

---

## Data Models

### Profile

Stores additional user profile information such as:

- Phone number
- Preferred currency
- Profile picture

### Category

Stores transaction categories.

Custom categories are associated with individual users so that users cannot use another user's private category.

### Transaction

Stores:

- User
- Amount
- Transaction type
- Description
- Date
- Category

Transaction types:

```text
INCOME
EXPENSE
```

### Investment

Stores:

- User
- Symbol
- Quantity
- Buy price
- Purchase date

The application calculates current value, profit/loss, and return percentage using the current market price.

---

## Running the Project Locally

### 1. Clone the repository

```bash
git clone https://github.com/Tushar1212543/FinTrack.git
cd FinTrack
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

For Windows PowerShell:

```powershell
.env\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install django djangorestframework djangorestframework-simplejwt mysqlclient pillow
```

### 5. Configure environment variables

Create a `.env` file in the project root and configure the required:

- Django secret key
- MySQL database credentials
- Market API credentials
- Other application secrets used by the project

Do not commit the `.env` file to GitHub.

### 6. Configure MySQL

Create the required MySQL database and database user, then configure the database connection using the environment variables used by the project.

### 7. Run migrations

```bash
python manage.py migrate
```

### 8. Create a superuser

```bash
python manage.py createsuperuser
```

### 9. Start the development server

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

---

## Security

FinTrack implements user-specific access control for financial data.

Protected API endpoints require authentication.

Transactions and investments are filtered according to the authenticated user, and update/delete operations also verify ownership.

Transaction categories are additionally validated so that a user cannot use another user's private category.

Sensitive files and local development files are excluded from Git using `.gitignore`.

---

## Validation

The application validates user input at the API level.

### Transactions

- Amount must be greater than zero
- Transaction type must be `INCOME` or `EXPENSE`
- Required fields are validated
- Category ownership is validated

### Investments

- Symbol is required
- Quantity must be greater than zero
- Buy price must be greater than zero
- Required fields are validated

---

## Financial Calculations

### Transaction Balance

```text
Balance = Total Income - Total Expenses
```

### Investment Value

```text
Invested Value = Quantity × Buy Price
```

```text
Current Value = Quantity × Current Market Price
```

```text
Profit/Loss = Current Value - Invested Value
```

```text
Return % = (Profit/Loss ÷ Invested Value) × 100
```

---

## Testing Performed

The project has been manually tested for:

- User authentication
- Unauthorized API access
- User-to-user data isolation
- Transaction ownership protection
- Investment ownership protection
- Category ownership protection
- Transaction amount validation
- Invalid transaction type validation
- Investment quantity validation
- Investment buy-price validation
- Missing required fields
- Transaction summary calculations
- Category summary calculations
- Monthly summary calculations
- Investment summary calculations
- Django system checks

Django system check:

```bash
python manage.py check
```

Result:

```text
System check identified no issues.
```

---

## Future Improvements

- Automated unit and integration test coverage
- API documentation
- Production deployment
- Improved dashboard analytics
- Additional investment instruments
- Advanced reporting and filtering
- Improved portfolio analytics
- Production-ready configuration

---

## Author

**Tushar Patil**

GitHub: https://github.com/Tushar1212543
