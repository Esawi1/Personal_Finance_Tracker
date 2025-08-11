from django.contrib import admin
from .models import Account, Category, Transaction, Budget, BudgetItem

admin.site.register(Account)
admin.site.register(Category)
admin.site.register(Transaction)
admin.site.register(Budget)
admin.site.register(BudgetItem)
