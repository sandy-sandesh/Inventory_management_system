from django.contrib import admin
from .models import Category, Item, Transaction

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('SN', 'name', 'category', 'stock', 'price')
    list_filter = ('category',)
    search_fields = ('SN', 'name')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'item', 'amount', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('item__name',)
