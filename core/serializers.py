from rest_framework import serializers
from .models import Account, Category, Transaction, Budget, BudgetItem

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'
        read_only_fields = ('owner',)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ('owner',)

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ('owner',)

class BudgetItemSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    class Meta:
        model = BudgetItem
        fields = ['id', 'category', 'category_name', 'limit']

class BudgetSerializer(serializers.ModelSerializer):
    items = BudgetItemSerializer(many=True)
    class Meta:
        model = Budget
        fields = ['id', 'owner', 'month', 'total_limit', 'items']
        read_only_fields = ('owner',)

    def create(self, validated_data):
        items = validated_data.pop('items', [])
        budget = Budget.objects.create(**validated_data)
        for item in items:
            BudgetItem.objects.create(budget=budget, **item)
        return budget

    def update(self, instance, validated_data):
        items = validated_data.pop('items', [])
        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()
        if items:
            instance.items.all().delete()
            for item in items:
                BudgetItem.objects.create(budget=instance, **item)
        return instance
