import datetime
from django.utils import timezone
from django.db.models import Sum, Count, F, Q
from django.db.models.functions import TruncDay, TruncMonth

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from .models import Product, Category, Sale, Expense ,Customer
from .forms import ProductForm, CategoryForm, SaleForm, ExpenseForm ,CustomerForm

# --- TRAFFIC CONTROLLER ---
def login_redirect_view(request):
    if request.user.is_superuser:
        return redirect('/admin/')
    else:
        return redirect('home')

# --- DASHBOARD / HOME ---
@login_required
def home(request):
    today = timezone.now().date()
    todays_sales_data = Sale.objects.filter(sale_date__date=today).aggregate(Sum('total_price'), Count('id'))
    todays_sales = todays_sales_data['total_price__sum'] or 0
    todays_orders = todays_sales_data['id__count'] or 0
    
    total_products = Product.objects.count()
    total_value_data = Product.objects.aggregate(total=Sum(F('price') * F('stock_quantity')))
    total_value = total_value_data['total'] or 0
    
    low_stock_products = Product.objects.filter(stock_quantity__lt=5)
    low_stock_count = low_stock_products.count()
    
    dates = []
    sales_counts = []
    for i in range(6, -1, -1):
        date = today - datetime.timedelta(days=i)
        dates.append(date.strftime("%a"))
        day_sales = Sale.objects.filter(sale_date__date=date).aggregate(Sum('total_price'))['total_price__sum'] or 0
        sales_counts.append(float(day_sales))
        
    recent_sales = Sale.objects.select_related('product', 'sold_by').order_by('-sale_date')[:5]

    context = {
        'todays_sales': todays_sales,
        'todays_orders': todays_orders,
        'total_products': total_products,
        'total_value': total_value,
        'low_stock_count': low_stock_count,
        'chart_dates': dates,
        'chart_sales': sales_counts,
        'low_stock_products': low_stock_products[:5],
        'recent_sales': recent_sales,
    }
    return render(request, 'core/home.html', context)

# --- DAILY SALES VIEW (Updated) ---
@login_required
def daily_sales_view(request):
    today = timezone.now().date()
    
    # Filter sales for today only
    sales_today = Sale.objects.filter(sale_date__date=today).order_by('-sale_date')
    
    # Calculate totals
    total_revenue = sales_today.aggregate(Sum('total_price'))['total_price__sum'] or 0
    total_items = sales_today.aggregate(Sum('quantity'))['quantity__sum'] or 0

    context = {
        'sales': sales_today,
        'total_revenue': total_revenue,
        'total_items': total_items,
        'today': today,
    }
    return render(request, 'core/daily_sales.html', context)

# --- ADD PRODUCT ---
@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.cost_price = request.POST.get('cost_price', 0)
            product.save()
            messages.success(request, "Product added successfully!")
            return redirect('inventory')
    else:
        form = ProductForm()
    return render(request, 'core/add_product.html', {'form': form})

# --- EDIT PRODUCT ---
@login_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            prod = form.save(commit=False)
            cost = request.POST.get('cost_price')
            if cost:
                prod.cost_price = cost
            prod.save()
            return redirect('inventory')
    else:
        form = ProductForm(instance=product)
    return render(request, 'core/add_product.html', {'form': form})


# --- DELETE PRODUCT ---
@login_required
def delete_product(request, pk):
    if not request.user.is_superuser:
        raise PermissionDenied  
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    messages.success(request, "Product deleted.")
    return redirect('inventory')


# --- CATEGORY MANAGEMENT ---
@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('add_product')
    else:
        form = CategoryForm()
    return render(request, 'core/add_category.html', {'form': form})


@login_required
def manage_categories(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_categories')
    else:
        form = CategoryForm()
    return render(request, 'core/manage_categories.html', {'categories': categories, 'form': form})


@login_required
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    return redirect('manage_categories')


# --- SELL PRODUCT ---
@login_required
def sell_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            quantity_sold = form.cleaned_data['quantity']
            if product.stock_quantity >= quantity_sold:
                product.stock_quantity -= quantity_sold
                product.save()
                
                sale = form.save(commit=False)
                sale.product = product
                sale.total_price = product.price * quantity_sold
                sale.sold_by = request.user
                sale.save()
                
                messages.success(request, f"Sold {quantity_sold} of {product.name}!")
                return redirect('daily_sales') # Updated redirect
            else:
                messages.error(request, "Not enough stock!")
    else:
        form = SaleForm()
    return render(request, 'core/sell_product.html', {'product': product, 'form': form})


# --- INVENTORY VIEW ---
@login_required
def inventory_view(request):
    query = request.GET.get('q')
    if query:
        products = Product.objects.filter(Q(name__icontains=query) | Q(category__name__icontains=query))
    else:
        products = Product.objects.all()
    return render(request, 'core/inventory.html', {'products': products})



# --- PROFIT & LOSS VIEW ---
@login_required
def profit_loss_view(request):
    today = timezone.now().date()
    current_year = today.year
    monthly_report = []
    
    total_revenue_year = 0
    total_cogs_year = 0
    total_opex_year = 0
    
    for m in range(1, 13):
        if m > today.month: break # Don't show future months
        
        monthly_sales = Sale.objects.filter(sale_date__year=current_year, sale_date__month=m)
        revenue = monthly_sales.aggregate(Sum('total_price'))['total_price__sum'] or 0
        
        cogs = sum((s.product.cost_price * s.quantity) for s in monthly_sales)
        
        monthly_expenses = Expense.objects.filter(date_added__year=current_year, date_added__month=m)
        opex = monthly_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
        
        gross_profit = revenue - cogs
        net_profit = gross_profit - opex
        
        total_revenue_year += revenue
        total_cogs_year += cogs
        total_opex_year += opex
        
        month_name = datetime.date(current_year, m, 1).strftime('%b')
        monthly_report.append({
            'month': month_name, 'revenue': revenue, 'cogs': cogs,
            'gross_profit': gross_profit, 'expenses': opex, 'net_profit': net_profit
        })

    total_gross_profit = total_revenue_year - total_cogs_year
    total_net_profit = total_gross_profit - total_opex_year
    profit_margin = (total_net_profit / total_revenue_year * 100) if total_revenue_year > 0 else 0

    context = {
        'current_year': current_year,
        'monthly_report': monthly_report,
        'total_revenue': total_revenue_year,
        'total_expenses': total_opex_year, 
        'gross_profit': total_gross_profit,
        'net_profit': total_net_profit,
        'profit_margin': profit_margin,
    }
    return render(request, 'core/profit_loss.html', context)



# --- EXPENSES VIEW ---
@login_required
def expenses_view(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.added_by = request.user
            expense.save()
            messages.success(request, "Expense added!")
            return redirect('expenses')
    else:
        form = ExpenseForm()
    expenses = Expense.objects.all().order_by('-date_added')
    return render(request, 'core/expenses.html', {'form': form, 'expenses': expenses})

@login_required
def delete_expense(request, pk):
    get_object_or_404(Expense, pk=pk).delete()
    return redirect('expenses')

# --- PLACEHOLDERS ---
@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'core/product_detail.html', {'product': product})

@login_required
def sales_history(request):
    sales = Sale.objects.all().order_by('-sale_date')
    return render(request, 'core/sales_history.html', {'sales': sales})

@login_required
def profile(request):
    return render(request, 'core/profile.html')

@login_required
def reports_view(request): return render(request, 'core/reports.html')


@login_required
def customers_view(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Customer added successfully!")
            return redirect('customers')
    else:
        form = CustomerForm()
    
    customers = Customer.objects.all().order_by('-date_added')
    return render(request, 'core/customers.html', {'form': form, 'customers': customers})

@login_required
def staff_view(request): return render(request, 'core/staff.html')
@login_required
def suppliers_view(request): return render(request, 'core/suppliers.html')
@login_required
def invoice_view(request): return render(request, 'core/invoice.html')