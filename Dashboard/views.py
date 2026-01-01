from django.shortcuts import render
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView
from django.db.models import F, Sum
from django.db.models.functions import TruncDay, TruncMonth, TruncYear
from django.utils import timezone
from django.http import JsonResponse
from .models import Item, Category, Transaction
from .forms import ItemForm, TransactionForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm, LoginForm

@login_required(login_url='dashboard:login')
def index(request):
    # Get real data from database for logged-in user only
    low_stock_items = Item.objects.filter(user=request.user, stock__lt=20)
    categories = Category.objects.filter(user=request.user)
    
    metrics = {
        'total_items': Item.objects.filter(user=request.user).count(),
        'categories': Category.objects.filter(user=request.user).count(),
        'low_stock': low_stock_items.count(),
        'total_value': Item.objects.filter(user=request.user).aggregate(total=Sum(F('stock') * F('price')))['total'] or 0
    }
    
    context = {
        'title': 'Dashboard',
        'low_stock_items': low_stock_items,
        'metrics': metrics,
        'categories': categories,
    }
    return render(request, 'Dashboard/index.html', context)

class ItemCreateView(CreateView):
    model = Item
    form_class = ItemForm
    success_url = reverse_lazy('dashboard:index')
    template_name = 'Dashboard/item_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add New Item'
        
        # Calculate and show next SN for this user
        user_items = Item.objects.filter(user=self.request.user).order_by('-sn')
        if user_items.exists():
            try:
                last_sn = int(user_items.first().sn)
                next_sn = last_sn + 1
            except (ValueError, TypeError):
                next_sn = 1
        else:
            next_sn = 1
        
        context['next_sn'] = next_sn
        return context
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        
        # Auto-generate SN for this user (per-user sequence: 1, 2, 3, 4...)
        user_items = Item.objects.filter(user=self.request.user).order_by('-sn')
        if user_items.exists():
            # Get the highest numeric SN for this user and add 1
            try:
                last_sn = int(user_items.first().sn)
                new_sn = last_sn + 1
            except (ValueError, TypeError):
                new_sn = 1
        else:
            # First item for this user gets SN 1
            new_sn = 1
        
        form.instance.sn = str(new_sn)
        response = super().form_valid(form)
        messages.success(self.request, f'Item added successfully! (SN: {new_sn})')
        return response
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('dashboard:login')
        return super().dispatch(request, *args, **kwargs)

class ItemListView(ListView):
    model = Item
    template_name = 'Dashboard/items_list.html'
    context_object_name = 'items'
    paginate_by = 20
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('dashboard:login')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = Item.objects.filter(user=self.request.user).order_by('sn')
        # Add total_value as a property on each item
        for item in queryset:
            item.total_value = item.stock * item.price
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'All Items'
        return context

class LowStockItemsView(ListView):
    model = Item
    template_name = 'Dashboard/items_list.html'
    context_object_name = 'items'
    paginate_by = 20
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('dashboard:login')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = Item.objects.filter(user=self.request.user, stock__lt=20).order_by('sn')
        # Add total_value as a property on each item
        for item in queryset:
            item.total_value = item.stock * item.price
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Low Stock Items'
        return context

class ItemUpdateView(UpdateView):
    model = Item
    form_class = ItemForm
    success_url = reverse_lazy('dashboard:index')
    template_name = 'Dashboard/item_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('dashboard:login')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return Item.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Item'
        return context
    
    def form_valid(self, form):
        # Get the original item to compare stock
        original_item = Item.objects.get(pk=self.object.pk)
        original_stock = original_item.stock
        new_stock = form.cleaned_data.get('stock')
        stock_difference = original_stock - new_stock
        
        # If stock decreased, create a transaction record
        if stock_difference > 0:
            transaction_amount = stock_difference * original_item.price
            Transaction.objects.create(
                item=original_item,
                amount=transaction_amount
            )
            messages.success(self.request, f'Item updated! Sold {stock_difference} units. Transaction recorded: Rs. {transaction_amount}')
        else:
            messages.success(self.request, 'Item updated successfully!')
        
        response = super().form_valid(form)
        return response

class ItemDeleteView(DeleteView):
    model = Item
    success_url = reverse_lazy('dashboard:index')
    template_name = 'Dashboard/item_confirm_delete.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('dashboard:login')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return Item.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Item deleted successfully!')
        return super().delete(request, *args, **kwargs)


@login_required(login_url='dashboard:login')
def record_transaction(request):
    """Record a new sales transaction."""
    if request.method == 'POST':
        form = TransactionForm(user=request.user, data=request.POST)
        if form.is_valid():
            transaction = form.save()
            messages.success(request, f'Transaction recorded: Rs. {transaction.amount}')
            return redirect('dashboard:index')
    else:
        form = TransactionForm(user=request.user)
    
    context = {
        'form': form,
        'title': 'Record Sale'
    }
    return render(request, 'Dashboard/transaction_form.html', context)


@login_required(login_url='dashboard:login')
def transaction_list(request):
    """View all transactions for the logged-in user."""
    transactions = Transaction.objects.filter(item__user=request.user).order_by('-created_at')
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(transactions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'transactions': page_obj,
        'title': 'Sales Transactions'
    }
    return render(request, 'Dashboard/transaction_list.html', context)


def sales_data(request):
    """Return JSON sales data for requested period.

    Accepts GET parameter 'period' with values: weekly, monthly, yearly.
    Aggregates amounts from the Transaction model. If no data exists,
    returns zero-filled series for the selected period.
    """
    from django.db.models import FloatField
    from django.db.models.functions import Cast
    
    period = request.GET.get('period', 'monthly')
    now = timezone.now()

    if period == 'weekly':
        # last 7 days - filter by user's transactions
        end = now.date()
        start = end - timezone.timedelta(days=6)
        qs = Transaction.objects.filter(item__user=request.user, created_at__date__gte=start, created_at__date__lte=end)
        # annotate by day
        daily = qs.annotate(day=TruncDay('created_at')).values('day').annotate(total=Sum(Cast('amount', FloatField()))).order_by('day')
        # build map date->total
        totals_map = {entry['day'].date(): entry['total'] or 0.0 for entry in daily}
        labels = []
        data = []
        for i in range(7):
            d = start + timezone.timedelta(days=i)
            labels.append(d.strftime('%a'))
            data.append(totals_map.get(d, 0.0))
        return JsonResponse({'labels': labels, 'data': data})

    if period == 'monthly':
        # current year months 1..12 - filter by user's transactions
        year = now.year
        qs = Transaction.objects.filter(item__user=request.user, created_at__year=year)
        monthly = qs.annotate(month=TruncMonth('created_at')).values('month').annotate(total=Sum(Cast('amount', FloatField()))).order_by('month')
        totals_map = {entry['month'].date().month: entry['total'] or 0.0 for entry in monthly}
        labels = [timezone.datetime(year, m, 1).strftime('%b') for m in range(1, 13)]
        data = [totals_map.get(m, 0.0) for m in range(1, 13)]
        return JsonResponse({'labels': labels, 'data': data})

    # yearly - filter by user's transactions
    years = [now.year - i for i in range(4, -1, -1)]
    qs = Transaction.objects.filter(item__user=request.user, created_at__year__in=years)
    yearly = qs.annotate(y=TruncYear('created_at')).values('y').annotate(total=Sum(Cast('amount', FloatField()))).order_by('y')
    totals_map = {entry['y'].date().year: entry['total'] or 0.0 for entry in yearly}
    labels = [str(y) for y in years]
    data = [totals_map.get(y, 0.0) for y in years]
    return JsonResponse({'labels': labels, 'data': data})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created. Please log in.')
            return redirect('dashboard:login')
        else:
            messages.error(request, 'Registration failed. Please check the errors below.')
    else:
        form = RegistrationForm()
    return render(request, 'Dashboard/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user)
                return redirect('dashboard:index')
            messages.error(request, 'Invalid email or password')
    else:
        form = LoginForm()
    return render(request, 'Dashboard/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('dashboard:login')
