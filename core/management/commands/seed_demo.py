from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from datetime import date
from random import randint, choice
from decimal import Decimal
from core.models import Account, Category, Transaction, Budget

class Command(BaseCommand):
    help = "Seed demo data: python manage.py seed_demo <username>"

    def add_arguments(self, parser):
        parser.add_argument("username")

    def handle(self, *args, **opts):
        U = get_user_model()
        u, _ = U.objects.get_or_create(username=opts["username"], defaults={"is_active": True})
        u.set_password("DemoPass123"); u.save()
        acc, _ = Account.objects.get_or_create(owner=u, name="Main Account", defaults={"balance": 2000})

        income = [("Salary","INCOME","#7c3aed"), ("Freelance","INCOME","#0ea5e9")]
        expense = [("Rent","EXPENSE","#ef4444"), ("Groceries","EXPENSE","#22c55e"),
                   ("Transport","EXPENSE","#f59e0b"), ("Dining","EXPENSE","#06b6d4")]

        def cat(name, t, color):
            return Category.objects.get_or_create(owner=u, name=name, type=t, defaults={"color": color})[0]

        inc = [cat(*x) for x in income]
        exp = [cat(*x) for x in expense]

        y, m = 2025, 8
        Budget.objects.get_or_create(owner=u, month=date(y,m,1), defaults={"total_limit": 3000})

        # salary days + random expenses
        Transaction.objects.get_or_create(owner=u, account=acc, category=inc[0], date=date(y,m,1), amount=Decimal("5000"))
        Transaction.objects.get_or_create(owner=u, account=acc, category=inc[1], date=date(y,m,20), amount=Decimal("1500"))
        for d in [5, 7, 10, 12, 15, 18, 23, 27]:
            c = choice(exp)
            amt = Decimal(str(-randint(20, 200)))
            Transaction.objects.get_or_create(owner=u, account=acc, category=c, date=date(y,m,d), amount=amt)

        self.stdout.write(self.style.SUCCESS("Seeded demo user. Login: {} / DemoPass123".format(u.username)))
