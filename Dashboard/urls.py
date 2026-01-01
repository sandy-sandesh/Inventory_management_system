from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    # auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    # items
    path('items/', views.ItemListView.as_view(), name='items_list'),
    path('low-stock/', views.LowStockItemsView.as_view(), name='low_stock'),
    path('item/add/', views.ItemCreateView.as_view(), name='item_add'),
    path('item/<int:pk>/edit/', views.ItemUpdateView.as_view(), name='item_edit'),
    path('item/<int:pk>/delete/', views.ItemDeleteView.as_view(), name='item_delete'),
    # transactions
    path('transaction/record/', views.record_transaction, name='record_transaction'),
    path('transactions/', views.transaction_list, name='transaction_list'),
    # analytics
    path('sales-data/', views.sales_data, name='sales_data'),
]
