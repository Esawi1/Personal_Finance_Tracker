import csv
from decimal import Decimal, InvalidOperation
from datetime import datetime, date
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from core.models import Account, Category, Transaction

DATE_FORMATS = [
    "%Y-%m-%d",     # 2025-08-10
    "%d/%m/%Y",     # 10/08/2025
    "%m/%d/%Y",     # 08/10/2025
    "%d-%m-%Y",     # 10-08-2025
    "%Y/%m/%d",     # 2025/08/10
]

def parse_date(s: str) -> date:
    s = (s or "").strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unsupported date format: {s!r}")

def parse_amount(s: str) -> Decimal:
    s = (s or "").strip().replace(",", "")
    try:
        return Decimal(s)
    except (InvalidOperation, TypeError):
        raise ValueError(f"Invalid amount: {s!r}")

class Command(BaseCommand):
    help = (
        "Import transactions from a CSV file.\n\n"
        "Required columns:\n"
        "  date, amount\n"
        "Optional columns:\n"
        "  description, category, type (INCOME|EXPENSE), account, currency\n\n"
        "Amount sign rule:\n"
        "  Positive amounts are treated as INCOME, negative as EXPENSE, unless 'type' column is provided."
    )

    def add_arguments(self, parser):
        parser.add_argument("username", help="Owner username for created transactions")
        parser.add_argument("csv_path", help="Path to CSV file")
        parser.add_argument("--delimiter", default=",", help="CSV delimiter (default: ,)")
        parser.add_argument("--dry-run", action="store_true", help="Parse only; do not write to DB")

    def handle(self, *args, **opts):
        username = opts["username"]
        path = opts["csv_path"]
        delim = opts["delimiter"]
        dry = opts["dry_run"]

        User = get_user_model()
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f"User {username!r} not found. Create it first.")

        required = {"date", "amount"}
        optional = {"description", "category", "type", "account", "currency"}

        created_count = 0
        skipped_count = 0
        errors = 0

        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f, delimiter=delim)
            headers = set(h.strip().lower() for h in reader.fieldnames or [])

            if not required.issubset(headers):
                missing = required - headers
                raise CommandError(f"CSV missing required columns: {', '.join(missing)}")

            for i, row in enumerate(reader, start=2):  # header is line 1
                try:
                    # normalize keys -> lower
                    row = { (k or "").strip().lower(): (v or "").strip() for k, v in row.items() }
                    d = parse_date(row.get("date"))
                    amt = parse_amount(row.get("amount"))

                    desc = row.get("description", "")
                    cat_name = row.get("category") or ("Income" if amt > 0 else "Uncategorized")
                    acc_name = row.get("account") or "Wallet"
                    currency = row.get("currency") or "USD"

                    # decide category type
                    type_col = row.get("type", "").upper()
                    if type_col in ("INCOME", "EXPENSE"):
                        cat_type = type_col
                    else:
                        cat_type = "INCOME" if amt > 0 else "EXPENSE"

                    # get/create account and category
                    account, _ = Account.objects.get_or_create(
                        owner=user, name=acc_name,
                        defaults={"currency": currency}
                    )
                    category, _ = Category.objects.get_or_create(
                        owner=user, name=cat_name, type=cat_type
                    )

                    if dry:
                        self.stdout.write(f"[DRY] {d} {amt} {cat_name}/{cat_type} {acc_name} {desc[:30]}")
                        created_count += 1
                        continue

                    Transaction.objects.create(
                        owner=user,
                        account=account,
                        category=category,
                        date=d,
                        amount=amt,
                        description=desc
                    )
                    created_count += 1

                except Exception as e:
                    errors += 1
                    skipped_count += 1
                    self.stderr.write(f"Line {i}: {e}")

        msg = f"Imported {created_count} row(s). Skipped {skipped_count}. Errors {errors}."
        if dry:
            msg = "[DRY RUN] " + msg
        self.stdout.write(self.style.SUCCESS(msg))
