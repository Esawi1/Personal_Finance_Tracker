from django.conf import settings
from django.db import models

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True

class Account(TimeStampedModel):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    institution = models.CharField(max_length=100, blank=True)
    currency = models.CharField(max_length=10, default='USD')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    def __str__(self):
        return f"{self.name} ({self.currency})"

class Category(TimeStampedModel):
    TYPE_CHOICES = (('INCOME','INCOME'), ('EXPENSE','EXPENSE'))
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=7, default='#4f46e5')  # NEW: hex color like #AABBCC

    class Meta:
        unique_together = ('owner', 'name', 'type')

    def __str__(self):
        return f"{self.name} - {self.type}"


class Transaction(TimeStampedModel):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)  # +income, -expense
    description = models.CharField(max_length=255, blank=True)
    is_transfer = models.BooleanField(default=False)
    class Meta:
        ordering = ['-date', '-id']

class Budget(TimeStampedModel):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    month = models.DateField(help_text='Use first day of month, e.g., 2025-08-01')
    total_limit = models.DecimalField(max_digits=12, decimal_places=2)
    class Meta:
        unique_together = ('owner', 'month')

class BudgetItem(TimeStampedModel):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='items')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    limit = models.DecimalField(max_digits=12, decimal_places=2)
    
    

