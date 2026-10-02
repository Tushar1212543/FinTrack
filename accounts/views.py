from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import Profile
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.contrib.auth import login, logout
from transactions.models import Transaction, Investment
from django.db.models import Sum, Q
from decimal import Decimal
from transactions.market_api import get_current_price
from django.db.models.functions import TruncMonth
from django.views.decorators.csrf import ensure_csrf_cookie


@csrf_exempt
def register(request):
    if request.method != "POST":
        return JsonResponse(
            {"error": "Only POST requests are allowed"},
            status=405
        )

    username = request.POST.get("username")
    email = request.POST.get("email")
    password = request.POST.get("password")
    phone_number = request.POST.get("phone_number")
    currency = request.POST.get("currency", "INR")


    if not username or not email or not password:
        return JsonResponse(
            {"error": "Username, email and password are required"},
            status=400
        )

    if User.objects.filter(username=username).exists():
        return JsonResponse(
            {"error": "Username already exists"},
            status=400
        )

    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )

    profile = Profile.objects.create(
        user=user,
        phone_number=phone_number,
        currency=currency
    )

    return JsonResponse(
        {
            "message": "Registration successful",
            "username": user.username
        },
        status=201
    )

@csrf_exempt
def user_login(request):
    if request.method != "POST":
        return JsonResponse(
            {"error": "Only POST requests are allowed"},
            status=405
        )

    username = request.POST.get("username")
    password = request.POST.get("password")

    user = authenticate(
        username=username,
        password=password
    )


    if user is None:
        return JsonResponse(
            {"error": "Invalid username or password"},
            status=401
        )

    login(request, user)

    return JsonResponse(
        {
            "message": "Login successful",
            "username": user.username
        },
        status=200
    )


def login_page(request):
    return render(request, "login.html")


def web_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("/dashboard/")

        return render(request, "login.html", {
            "error": "Invalid username or password."
        })

    return render(request, "login.html")


def dashboard(request):
    if not request.user.is_authenticated:
        return redirect("/login-page/")

    transactions = Transaction.objects.filter(
        user=request.user
    )

    investments = Investment.objects.filter(
        user=request.user
    )

    # -------------------------
    # Income
    # -------------------------

    total_income = (
        transactions
        .filter(transaction_type="INCOME")
        .aggregate(total=Sum("amount"))["total"] or 0
    )

    # -------------------------
    # Expenses
    # -------------------------

    total_expenses = (
        transactions
        .filter(transaction_type="EXPENSE")
        .aggregate(total=Sum("amount"))["total"] or 0
    )

    # -------------------------
    # Balance
    # -------------------------

    balance = total_income - total_expenses

    # -------------------------
    # Investment calculations
    # -------------------------

    total_invested = sum(
        investment.quantity * investment.buy_price
        for investment in investments
    )

    total_current_value = Decimal("0")

    # Cache live prices so the same stock
    # isn't requested multiple times
    price_cache = {}

    for investment in investments:

        try:
            if investment.symbol not in price_cache:
                price_cache[investment.symbol] = get_current_price(
                    investment.symbol
                )

            current_price = price_cache[
                investment.symbol
            ]

            current_value = (
                investment.quantity * current_price
            )

            total_current_value += current_value

        except Exception:
            pass

    # -------------------------
    # Total Investment P/L
    # -------------------------

    total_profit_loss = (
        total_current_value - total_invested
    )

    # -------------------------
    # Recent transactions
    # -------------------------

    recent_transactions = transactions.order_by(
        "-date"
    )[:5]

    # -------------------------
    # Recent investments
    # -------------------------

    recent_investments = investments.order_by(
        "-purchase_date"
    )[:5]

    # Add live data to recent investments
    for investment in recent_investments:

        try:
            if investment.symbol not in price_cache:
                price_cache[investment.symbol] = get_current_price(
                    investment.symbol
                )

            current_price = price_cache[
                investment.symbol
            ]

            invested_value = (
                investment.quantity * investment.buy_price
            )

            current_value = (
                investment.quantity * current_price
            )

            profit_loss = (
                current_value - invested_value
            )

            return_percentage = (
                (profit_loss / invested_value) * 100
                if invested_value > 0
                else Decimal("0")
            )

            investment.current_price = current_price
            investment.current_value = current_value
            investment.profit_loss = profit_loss
            investment.return_percentage = return_percentage

        except Exception:

            investment.current_price = None
            investment.current_value = None
            investment.profit_loss = None
            investment.return_percentage = None

    # -------------------------
    # Monthly financial summary
    # -------------------------

    monthly_transactions = (
        transactions
        .annotate(
            month=TruncMonth("date")
        )
        .values("month")
        .annotate(
            income=Sum(
                "amount",
                filter=Q(
                    transaction_type="INCOME"
                )
            ),
            expenses=Sum(
                "amount",
                filter=Q(
                    transaction_type="EXPENSE"
                )
            ),
        )
        .order_by("-month")
    )

    monthly_summary = []

    for month in monthly_transactions:

        income = month["income"] or 0
        expenses = month["expenses"] or 0

        monthly_summary.append({
            "month": month["month"],
            "income": income,
            "expenses": expenses,
            "net": income - expenses,
        })

    # -------------------------
    # Expense category summary
    # -------------------------

    category_summary = (
        transactions
        .filter(
            transaction_type="EXPENSE"
        )
        .values(
            "category__name"
        )
        .annotate(
            total=Sum("amount")
        )
        .order_by("-total")
    )

    # -------------------------
    # Render dashboard
    # -------------------------

    return render(
        request,
        "dashboard.html",
        {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "balance": balance,

            "total_invested": total_invested,
            "total_current_value": total_current_value,
            "total_profit_loss": total_profit_loss,

            "recent_transactions": recent_transactions,
            "recent_investments": recent_investments,

            "monthly_summary": monthly_summary,

            "category_summary": category_summary,
        }
    )


def user_logout(request):
    logout(request)
    return redirect("/login-page/")

@ensure_csrf_cookie
def signup_page(request):
    if request.method == "POST":

        response = register(request)

        if response.status_code == 201:
            return redirect("/login-page/")

        error = response.json().get(
            "error",
            "Registration failed."
        )

        return render(
            request,
            "signup.html",
            {
                "error": error
            }
        )

    return render(request, "signup.html")


def profile_page(request):

    if not request.user.is_authenticated:
        return redirect("/login-page/")

    profile = request.user.profile

    return render(
        request,
        "profile.html",
        {
            "user": request.user,
            "profile": profile,
        }
    )

def profile_edit(request):
    if not request.user.is_authenticated:
        return redirect("/login-page/")

    profile = request.user.profile

    if request.method == "POST":
        new_username = request.POST.get("username", "").strip()
        new_email = request.POST.get("email", "").strip()
        new_phone = request.POST.get("phone_number", "").strip()
        new_currency = request.POST.get("currency", "INR").strip().upper()

        # Basic validation
        if not new_username or not new_email:
            return render(
                request,
                "profile_edit.html",
                {
                    "user": request.user,
                    "profile": profile,
                    "error": "Username and email are required."
                }
            )

        # Username must be unique, except for the current user
        if User.objects.filter(username=new_username).exclude(
            id=request.user.id
        ).exists():
            return render(
                request,
                "profile_edit.html",
                {
                    "user": request.user,
                    "profile": profile,
                    "error": "That username is already taken."
                }
            )

        # Update user information
        request.user.username = new_username
        request.user.email = new_email
        request.user.save()

        # Update profile information
        profile.phone_number = new_phone
        profile.currency = new_currency

        # Update profile picture if a new one was uploaded
        if request.FILES.get("profile_picture"):
            profile.profile_picture = request.FILES.get("profile_picture")

        profile.save()

        return redirect("/profile/")

    return render(
        request,
        "profile_edit.html",
        {
            "user": request.user,
            "profile": profile
        }
    )

def delete_profile_picture(request):
    if not request.user.is_authenticated:
        return redirect("/login-page/")

    profile = request.user.profile

    if request.method == "POST":
        if profile.profile_picture:
            profile.profile_picture.delete(save=False)
            profile.profile_picture = None
            profile.save(update_fields=["profile_picture"])

        return redirect("/profile/edit/")

    return redirect("/profile/edit/")
