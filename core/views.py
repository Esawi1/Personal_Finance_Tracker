from datetime import date
from django.shortcuts import render
from django.db.models import Sum, Case, When, DecimalField
from django.http import HttpResponse
from rest_framework import viewsets, permissions, decorators, response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import csv

from .models import Account, Category, Transaction, Budget
from .serializers import (
    AccountSerializer, CategorySerializer, TransactionSerializer, BudgetSerializer
)

# ---------- UI ----------
def dashboard(request):
    return render(request, 'dashboard.html')


# ---------- DRF base ----------
class BaseOwnedViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)


# ---------- ViewSets ----------
class AccountViewSet(BaseOwnedViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer


class CategoryViewSet(BaseOwnedViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TransactionViewSet(BaseOwnedViewSet):
    queryset = Transaction.objects.select_related('account', 'category').order_by('-date', '-id')
    serializer_class = TransactionSerializer

    # Filters & pagination support
    def get_queryset(self):
        qs = super().get_queryset()
        start = self.request.query_params.get('start')
        end = self.request.query_params.get('end')
        category = self.request.query_params.get('category')  # id or name

        if start:
            qs = qs.filter(date__gte=start)
        if end:
            qs = qs.filter(date__lte=end)
        if category:
            if str(category).isdigit():
                qs = qs.filter(category_id=int(category))
            else:
                qs = qs.filter(category__name__iexact=category)
        return qs

    @decorators.action(detail=False, methods=['get'])
    def monthly_summary(self, request):
        """
        Query param: month=YYYY-MM
        Returns: income, expense, by_category (sum + color), daily series (split),
                 and budget snapshot. DB-agnostic month filter.
        """
        month_str = request.query_params.get('month')  # e.g., "2025-08"
        qs = self.get_queryset()

        # Month window [start, next_start)
        start = next_start = None
        if month_str:
            try:
                y, m = map(int, month_str.split('-'))
                start = date(y, m, 1)
                next_start = date(y + (m // 12), (m % 12) + 1, 1)
                qs = qs.filter(date__gte=start, date__lt=next_start)
            except Exception:
                pass

        # Totals
        income_total = qs.filter(amount__gt=0).aggregate(total=Sum('amount'))['total'] or 0
        expense_total = -(qs.filter(amount__lt=0).aggregate(total=Sum('amount'))['total'] or 0)

        # By category with color
        by_cat = qs.values('category__name', 'category__color').annotate(total=Sum('amount')).order_by()

        # Daily series: split income & expense so both show even on same day
        daily_raw = qs.values('date').annotate(
            inc=Sum(Case(When(amount__gt=0, then='amount'), default=0, output_field=DecimalField())),
            exp=Sum(Case(When(amount__lt=0, then='amount'), default=0, output_field=DecimalField())),
        ).order_by('date')

        daily = [{
            'day': row['date'].strftime('%d'),
            'income': float(row['inc'] or 0),
            'expense': float(-(row['exp'] or 0)),  # positive number
        } for row in daily_raw]

        # Budget snapshot
        budget = None
        if start and next_start:
            b = Budget.objects.filter(owner=request.user, month__gte=start, month__lt=next_start).first()
            if b:
                budget = {'limit': float(b.total_limit), 'used': float(expense_total)}

        return response.Response({
            'income': float(income_total),
            'expense': float(expense_total),
            'by_category': list(by_cat),
            'daily': daily,
            'budget': budget,
        })

    # Export CSV for current filtered queryset
    @decorators.action(detail=False, methods=['get'])
    def export(self, request):
        """
        GET /api/transactions/export/?start=YYYY-MM-DD&end=YYYY-MM-DD&category=Rent
        Returns a CSV file of the filtered transactions.
        """
        qs = self.get_queryset().select_related('category', 'account')

        start = request.query_params.get('start') or ''
        end = request.query_params.get('end') or ''
        filename = "transactions.csv"
        if start and end:
            filename = f"transactions_{start}_to_{end}.csv"

        resp = HttpResponse(content_type='text/csv; charset=utf-8')
        resp['Content-Disposition'] = f'attachment; filename="{filename}"'

        # BOM so Excel opens UTF-8 cleanly
        resp.write('\ufeff')

        w = csv.writer(resp)
        w.writerow(['date', 'amount', 'description', 'category', 'account'])
        for t in qs:
            w.writerow([
                t.date,
                t.amount,
                t.description,
                getattr(t.category, 'name', ''),
                t.account.name
            ])
        return resp


class BudgetViewSet(BaseOwnedViewSet):
    queryset = Budget.objects.prefetch_related('items')
    serializer_class = BudgetSerializer


# ---------- Cards Summary Endpoint ----------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cards_summary(request):
    """
    GET /api/summary/cards?month=YYYY-MM
    Returns:
      - balance: sum of Account.balance for the user
      - income: total income in the month
      - expense: total expenses in the month (positive number)
      - budget: {limit, used, pct} if a Budget exists for the month
    """
    month_str = request.query_params.get('month')

    start = next_start = None
    if month_str:
        try:
            y, m = map(int, month_str.split('-'))
            start = date(y, m, 1)
            next_start = date(y + (m // 12), (m % 12) + 1, 1)
        except Exception:
            start = next_start = None

    balance_total = Account.objects.filter(owner=request.user).aggregate(
        total=Sum('balance')
    )['total'] or 0

    tx = Transaction.objects.filter(owner=request.user)
    if start and next_start:
        tx = tx.filter(date__gte=start, date__lt=next_start)

    income_total = tx.filter(amount__gt=0).aggregate(total=Sum('amount'))['total'] or 0
    expense_total = -(tx.filter(amount__lt=0).aggregate(total=Sum('amount'))['total'] or 0)

    budget_data = None
    if start and next_start:
        b = Budget.objects.filter(owner=request.user, month__gte=start, month__lt=next_start).first()
        if b:
            used = float(expense_total)
            limit = float(b.total_limit)
            pct = int(min(100, round((used / limit) * 100))) if limit > 0 else 0
            budget_data = {"limit": limit, "used": used, "pct": pct}

    return Response({
        "balance": float(balance_total),
        "income": float(income_total),
        "expense": float(expense_total),
        "budget": budget_data
    })


# ---------- Who am I (for JWT sanity check) ----------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    return Response({
        'username': request.user.username,
        'email': request.user.email,
    })
