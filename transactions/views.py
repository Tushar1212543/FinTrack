from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Sum, F, DecimalField, Value, Q
from decimal import Decimal
from django.shortcuts import render, redirect
from .market_api import get_current_price
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from .models import Transaction, Investment, Category
from .serializers import TransactionSerializer, InvestmentSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def transaction_list(request):
    transactions = Transaction.objects.filter(
        user=request.user
    )

    transaction_type = request.GET.get("type")

    if transaction_type:
        if transaction_type not in ["INCOME", "EXPENSE"]:
            return Response(
                {
                    "error": "Invalid transaction type. Use INCOME or EXPENSE."
                },
                status=400
            )

        transactions = transactions.filter(
            transaction_type=transaction_type
        )

    search = request.GET.get("search")

    if search:
        transactions = transactions.filter(
            description__icontains=search
        )

    sort = request.GET.get("sort")

    allowed_sort_fields = [
        "amount",
        "-amount",
        "date",
        "-date",
    ]

    if sort:
        if sort not in allowed_sort_fields:
            return Response(
                {
                    "error": "Invalid sort field. Use amount, -amount, date, or -date."
                },
                status=400
            )

        transactions = transactions.order_by(sort)

    page_number = request.GET.get("page", 1)
    page_size = request.GET.get("page_size", 10)

    try:
        page_size = int(page_size)

        if page_size < 1 or page_size > 100:
            return Response(
                {"error": "page_size must be between 1 and 100."},
                status=400
            )

    except ValueError:
        return Response(
            {"error": "page_size must be a valid number."},
            status=400
        )

    paginator = Paginator(transactions, page_size)

    try:
        page = paginator.page(page_number)
    except Exception:
        return Response(
            {"error": "Invalid page number."},
            status=400
        )

    serializer = TransactionSerializer(
        page.object_list,
        many=True
    )

    return Response({
        "count": paginator.count,
        "total_pages": paginator.num_pages,
        "current_page": page.number,
        "next_page": page.next_page_number() if page.has_next() else None,
        "previous_page": page.previous_page_number() if page.has_previous() else None,
        "results": serializer.data
    })

def transaction_page(request):
    if not request.user.is_authenticated:
        return redirect("/login-page/")

    transactions = Transaction.objects.filter(
        user=request.user
    ).order_by("-date")

    return render(
        request,
        "transactions.html",
        {
            "transactions": transactions
        }
    )

def transaction_create_page(request):
    if not request.user.is_authenticated:
        return redirect("/login-page/")

    categories = Category.objects.filter(
        Q(user=request.user) | Q(user__isnull=True)
    ).order_by("name")

    if request.method == "POST":
        serializer = TransactionSerializer(
            data=request.POST,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save(user=request.user)
            return redirect("/transactions-page/")

        return render(
            request,
            "transaction_create.html",
            {
                "categories": categories,
                "errors": serializer.errors,
            }
        )

    return render(
        request,
        "transaction_create.html",
        {
            "categories": categories
        }
    )

def transaction_delete_page(request, transaction_id):
    if not request.user.is_authenticated:
        return redirect("/login-page/")

    if request.method == "POST":
        transaction = get_object_or_404(
            Transaction,
            id=transaction_id,
            user=request.user
        )

        transaction.delete()

        return redirect("/transactions-page/")

    return redirect("/transactions-page/")

def transaction_edit_page(request, transaction_id):
    if not request.user.is_authenticated:
        return redirect("/login-page/")

    transaction = get_object_or_404(
        Transaction,
        id=transaction_id,
        user=request.user
    )

    categories = Category.objects.all()

    if request.method == "POST":
        serializer = TransactionSerializer(
            transaction,
            data=request.POST,
            partial=True,
            context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()
            return redirect("/transactions-page/")

        return render(
            request,
            "transaction_edit.html",
            {
                "transaction": transaction,
                "categories": categories,
                "errors": serializer.errors,
            }
        )

    return render(
        request,
        "transaction_edit.html",
        {
            "transaction": transaction,
            "categories": categories,
        }
    )

def investment_page(request):
    if not request.user.is_authenticated:
        return redirect("/login-page/")

    investments = Investment.objects.filter(
        user=request.user
    ).order_by("-purchase_date")

    investment_data = []

    total_invested = Decimal("0")
    total_current_value = Decimal("0")

    for investment in investments:
        try:
            current_price = get_current_price(investment.symbol)

            invested_value = investment.quantity * investment.buy_price
            current_value = investment.quantity * current_price
            profit_loss = current_value - invested_value
            total_invested += invested_value
            total_current_value += current_value

            return_percentage = (
                ((profit_loss / invested_value) * 100).quantize(
                    Decimal("0.01")
                )
                if invested_value > 0
                else Decimal("0.00")
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

        investment_data.append(investment)

    total_profit_loss = total_current_value - total_invested

    overall_return_percentage = (
        ((total_profit_loss / total_invested) * 100).quantize(
            Decimal("0.01")
        )
        if total_invested > 0
        else Decimal("0.00")
    )

    return render(
        request,
        "investments.html",
        {
            "investments": investment_data,
            "total_invested": total_invested,
            "total_current_value": total_current_value,
            "total_profit_loss": total_profit_loss,
            "overall_return_percentage": overall_return_percentage,
        }
    )

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def transaction_create(request):
    serializer = TransactionSerializer(
        data=request.data,
        context={"request": request}
    )

    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)



@api_view(["GET"])
@permission_classes([IsAuthenticated])
def transaction_detail(request, transaction_id):
    transaction = get_object_or_404(
        Transaction,
        id=transaction_id,
        user=request.user
    )

    serializer = TransactionSerializer(transaction)

    return Response(serializer.data)


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def transaction_update(request, transaction_id):
    transaction = get_object_or_404(
        Transaction,
        id=transaction_id,
        user=request.user
    )

    serializer = TransactionSerializer(
        transaction,
        data=request.data,
        partial=request.method == "PATCH",
        context={"request": request}
    )

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=400)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def transaction_delete(request, transaction_id):
    transaction = get_object_or_404(
        Transaction,
        id=transaction_id,
        user=request.user
    )

    transaction.delete()

    return Response(status=204)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def transaction_summary(request):
    transactions = Transaction.objects.filter(
        user=request.user
    )

    total_income = transactions.filter(
        transaction_type="INCOME"
    ).aggregate(
        total=Sum("amount")
    )["total"] or 0

    total_expenses = transactions.filter(
            transaction_type="EXPENSE"
        ).aggregate(
            total=Sum("amount")
        )["total"] or 0

    current_balance = total_income - total_expenses

    return Response({
        "total_income": total_income,
        "total_expenses": total_expenses,
        "current_balance": current_balance
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def category_summary(request):
    expenses = Transaction.objects.filter(
        user=request.user,
        transaction_type="EXPENSE"
    )

    category_totals = expenses.values(
        "category__name"
    ).annotate(
        total=Sum("amount")
    )

    return Response(category_totals)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def investment_list(request):
    investments = Investment.objects.filter(
        user=request.user
    )

    serializer = InvestmentSerializer(
        investments,
        many=True
    )

    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def investment_create(request):
    serializer = InvestmentSerializer(
        data=request.data
    )

    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(
            serializer.data,
            status=201
        )

    return Response(
        serializer.errors,
        status=400
    )

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def investment_summary(request):
    investments = Investment.objects.filter(user=request.user)

    total_invested = investments.annotate(
        invested_value=F("quantity") * F("buy_price")
    ).aggregate(
        total=Sum("invested_value")
    )["total"] or Decimal("0")

    investment_details = []
    total_current_value = Decimal("0")

    for investment in investments:
        try:
            current_price = get_current_price(investment.symbol)
        except Exception as e:
            return Response({
                "error": f"Could not fetch current price for {investment.symbol}.",
                "details": str(e)
            }, status=502)

        invested_value = investment.quantity * investment.buy_price
        current_value = investment.quantity * current_price
        investment_profit_loss = current_value - invested_value

        investment_return_percentage = (
            ((investment_profit_loss / invested_value) * 100).quantize(
                Decimal("0.01")
            )
            if invested_value > 0
            else Decimal("0.00")
        )

        total_current_value += current_value

        investment_details.append({
            "id": investment.id,
            "symbol": investment.symbol,
            "quantity": investment.quantity,
            "buy_price": investment.buy_price,
            "current_price": current_price,
            "invested_value": invested_value,
            "current_value": current_value,
            "profit_loss": investment_profit_loss,
            "return_percentage": investment_return_percentage,
        })

    profit_loss = total_current_value - total_invested

    overall_return_percentage = (
        ((profit_loss / total_invested) * 100).quantize(
            Decimal("0.01")
        )
        if total_invested > 0
        else Decimal("0.00")
    )

    return Response({
        "total_invested": total_invested,
        "total_current_value": total_current_value,
        "profit_loss": profit_loss,
        "return_percentage": overall_return_percentage,
        "investments": investment_details,
    })


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def investment_detail(request, investment_id):
    investment = get_object_or_404(
        Investment,
        id=investment_id,
        user=request.user
    )

    serializer = InvestmentSerializer(investment)

    return Response(serializer.data)


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def investment_update(request, investment_id):
    investment = get_object_or_404(
        Investment,
        id=investment_id,
        user=request.user
    )

    serializer = InvestmentSerializer(
        investment,
        data=request.data,
        partial=request.method == "PATCH"
    )

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(
        serializer.errors,
        status=400
    )

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def investment_delete(request, investment_id):
    investment = get_object_or_404(
        Investment,
        id=investment_id,
        user=request.user
    )

    investment.delete()

    return Response(status=204)

def investment_create_page(request):
    if not request.user.is_authenticated:
        return redirect("/login-page/")

    if request.method == "POST":
        symbol = request.POST.get("symbol", "").strip().upper()
        quantity = request.POST.get("quantity")
        buy_price = request.POST.get("buy_price")

        investment = InvestmentSerializer(
            data={
                "symbol": symbol,
                "quantity": quantity,
                "buy_price": buy_price,
            }
        )

        if investment.is_valid():
            investment.save(user=request.user)
            return redirect("/investments-page/")

        return render(
            request,
            "investment_create.html",
            {
                "errors": investment.errors,
                "form_data": request.POST,
            }
        )

    return render(request, "investment_create.html")

def investment_delete_page(request, investment_id):
    if not request.user.is_authenticated:
        return redirect("/login-page/")

    investment = get_object_or_404(
        Investment,
        id=investment_id,
        user=request.user
    )

    if request.method == "POST":
        investment.delete()
        return redirect("/investments-page/")

    return redirect("/investments-page/")

def investment_edit_page(request, investment_id):
    if not request.user.is_authenticated:
        return redirect("/login-page/")

    investment = get_object_or_404(
        Investment,
        id=investment_id,
        user=request.user
    )

    if request.method == "POST":
        serializer = InvestmentSerializer(
            investment,
            data={
                "symbol": request.POST.get("symbol", "").strip().upper(),
                "quantity": request.POST.get("quantity"),
                "buy_price": request.POST.get("buy_price"),
            }
        )

        if serializer.is_valid():
            serializer.save()
            return redirect("/investments-page/")

        return render(
            request,
            "investment_edit.html",
            {
                "investment": investment,
                "errors": serializer.errors,
            }
        )

    return render(
        request,
        "investment_edit.html",
        {
            "investment": investment,
        }
    )

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def monthly_summary(request):

    transactions = Transaction.objects.filter(
        user=request.user
    )

    monthly_data = (
        transactions
        .annotate(month=TruncMonth("date"))
        .values("month")
        .annotate(
            income=Sum(
                "amount",
                filter=Q(transaction_type="INCOME")
            ),
            expenses=Sum(
                "amount",
                filter=Q(transaction_type="EXPENSE")
            ),
        )
        .order_by("-month")
    )

    result = []

    for month in monthly_data:

        income = month["income"] or 0
        expenses = month["expenses"] or 0

        result.append({
            "month": month["month"],
            "income": income,
            "expenses": expenses,
            "net": income - expenses,
        })

    return Response(result)

def category_create_page(request):
    if not request.user.is_authenticated:
        return redirect("/login-page/")

    next_url = request.GET.get(
        "next",
        "/transactions/create-page/"
    )

    # Only allow local URLs
    if not next_url.startswith("/") or next_url.startswith("//"):
        next_url = "/transactions/create-page/"

    if request.method == "POST":
        name = request.POST.get("name", "").strip()

        if not name:
            return render(
                request,
                "category_create.html",
                {
                    "error": "Category name is required.",
                    "next_url": next_url,
                }
            )

        if Category.objects.filter(
            user=request.user,
            name__iexact=name
        ).exists():
            return render(
                request,
                "category_create.html",
                {
                    "error": "You already have a category with this name.",
                    "next_url": next_url,
                }
            )

        Category.objects.create(
            user=request.user,
            name=name
        )

        return redirect(next_url)

    return render(
        request,
        "category_create.html",
        {
            "next_url": next_url
        }
    )