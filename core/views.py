import datetime
from django.utils import timezone
from django.db.models import Sum, Count, F, Q
from django.db.models.functions import TruncDay ,TruncMonth

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from .models import Product, Category, Sale , Expense
from .forms import ProductForm, CategoryForm, SaleForm ,ExpenseForm



# --- TRAFFIC CONTROLLER ---
def login_redirect_view(request):
    if request.user.is_superuser:
        return redirect('/admin/')
    else:
        return redirect('home')

# --- DASHBOARD / HOME (Inventory Main Page) ---
@login_required
def home(request):
    today = timezone.now().date()

    # A. Today's Sales
    todays_sales_data = Sale.objects.filter(sale_date__date=today).aggregate(Sum('total_price'), Count('id'))
    todays_sales = todays_sales_data['total_price__sum'] or 0
    todays_orders = todays_sales_data['id__count'] or 0

    # B. Total Stock Value & Count
    total_products = Product.objects.count()
    # Calculates Selling Price Value (Revenue Potential)
    total_value_data = Product.objects.aggregate(total=Sum(F('price') * F('stock_quantity')))
    total_value = total_value_data['total'] or 0
    
    # C. Low Stock
    low_stock_products = Product.objects.filter(stock_quantity__lt=5)
    low_stock_count = low_stock_products.count()

    # D. Chart Data (Weekly Sales - Last 7 Days)
    dates = []
    sales_counts = []
    
    for i in range(6, -1, -1):
        date = today - datetime.timedelta(days=i)
        dates.append(date.strftime("%a")) # Mon, Tue, Wed...
        
        # Sum sales for this specific day
        day_sales = Sale.objects.filter(sale_date__date=date).aggregate(Sum('total_price'))['total_price__sum'] or 0
        sales_counts.append(float(day_sales)) # Convert to float for JSON

    # E. Recent Sales (Bottom Right Widget)
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


# --- ADD PRODUCT (Updated for Cost Price) ---
@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            # Manually save the cost_price from the HTML input
            product.cost_price = request.POST.get('cost_price', 0)
            product.save()
            messages.success(request, "Product added successfully!")
            return redirect('inventory') # Go to inventory list
    else:
        form = ProductForm()
    return render(request, 'core/add_product.html', {'form': form})


# --- EDIT PRODUCT (Updated for Cost Price) ---
@login_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            prod = form.save(commit=False)
            # Update cost price if provided
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
    if request.method == 'GET': # Changed to GET for the simple link, or use POST form in HTML
        product.delete()
        messages.success(request, "Product deleted.")
        return redirect('inventory')
    return redirect('inventory')



# --- ADD CATEGORY ---
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


# --- MANAGE CATEGORIES ---
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
    return render(request, 'core/manage_categories.html', {
        'categories': categories,
        'form': form
    })



@login_required
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    return redirect('manage_categories')


# --- PRODUCT DETAIL ---
@login_required
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'core/product_detail.html', {'product': product})


# --- SELL PRODUCT ---
@login_required
def sell_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            quantity_sold = form.cleaned_data['quantity']
            
            # Check if we have enough stock
            if product.stock_quantity >= quantity_sold:
                # 1. Deduct stock
                product.stock_quantity -= quantity_sold
                product.save()
                
                # 2. Save the Sale Record
                sale = form.save(commit=False)
                sale.product = product
                sale.total_price = product.price * quantity_sold
                sale.sold_by = request.user
                sale.save()
                
                messages.success(request, f"Successfully sold {quantity_sold} units of {product.name}!")
                return redirect('daily_sales') # Redirect to Daily Sales to see the transaction
            else:
                messages.error(request, f"Error: Not enough stock! Only {product.stock_quantity} available.")
    else:
        form = SaleForm()

    return render(request, 'core/sell_product.html', {
        'product': product,
        'form': form
    })


# --- SALES HISTORY ---
@login_required
def sales_history(request):
    sales = Sale.objects.all().order_by('-sale_date')
    return render(request, 'core/sales_history.html', {'sales': sales})


# --- USER PROFILE ---
@login_required
def profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
        
    return render(request, 'core/profile.html')

# --- INVENTORY PAGE ---
@login_required
def inventory_view(request):
    query = request.GET.get('q')
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(category__name__icontains=query)
        )
    else:
        products = Product.objects.all()

    context = {'products': products}
    return render(request, 'core/inventory.html', context)

# --- DAILY SALES VIEW ---
@login_required
def daily_sales_view(request):
    today = timezone.now().date()
    
    # Filter sales for today only
    daily_sales = Sale.objects.filter(sale_date__date=today).order_by('-sale_date')
    
    # Calculate total revenue for today
    total_sales_income = daily_sales.aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    # Count total items sold today
    total_items_sold = daily_sales.aggregate(Sum('quantity'))['quantity__sum'] or 0

    context = {
        'sales': daily_sales,
        'total_sales_income': total_sales_income,
        'total_items_sold': total_items_sold,
        'date_today': today,
    }
    return render(request, 'core/daily_sales.html', context)



# --- PROFIT & LOSS VIEW  ---
@login_required
def profit_loss_view(request):
    today = timezone.now().date()
    current_year = today.year
    
    # Initialize containers for the report
    monthly_report = []
    months_labels = []
    
    # Global Totals for the Top Cards (Year to Date)
    total_revenue_year = 0
    total_cogs_year = 0      # Cost of Goods Sold
    total_opex_year = 0      # Operating Expenses (Rent, etc.)
    
    # Loop through months 1 to 12 to build the report
    for m in range(1, 13):
        # 1. Sales for this specific month
        monthly_sales = Sale.objects.filter(sale_date__year=current_year, sale_date__month=m)
        revenue = monthly_sales.aggregate(Sum('total_price'))['total_price__sum'] or 0
        
        # 2. Calculate COGS (Product Cost) for this month
        cogs = 0
        for sale in monthly_sales:
            cogs += (sale.product.cost_price * sale.quantity)
            
        # 3. Operating Expenses (Bills/Rent) for this month
        monthly_expenses = Expense.objects.filter(date_added__year=current_year, date_added__month=m)
        opex = monthly_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
        
        # 4. Profit Calculations
        gross_profit = revenue - cogs
        net_profit = gross_profit - opex
        
        # Add to Yearly Totals
        total_revenue_year += revenue
        total_cogs_year += cogs
        total_opex_year += opex
        
        # Only add to list if it's a past or current month (don't show future empty months yet)
        if m <= today.month:
            month_name = datetime.date(current_year, m, 1).strftime('%b') # Jan, Feb...
            months_labels.append(month_name)
            
            monthly_report.append({
                'month': month_name,
                'revenue': float(revenue),
                'cogs': float(cogs),
                'gross_profit': float(gross_profit),
                'expenses': float(opex),
                'net_profit': float(net_profit)
            })

    # Final Card Calculations
    total_gross_profit = total_revenue_year - total_cogs_year
    total_net_profit = total_gross_profit - total_opex_year
    
    # Calculate Margin %
    if total_revenue_year > 0:
        profit_margin = (total_net_profit / total_revenue_year) * 100
    else:
        profit_margin = 0

    context = {
        'current_year': current_year,
        'monthly_report': monthly_report, # For the Table
        
        # For the Top Cards
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
    # 1. Handle Form Submission (Adding a Bill)
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.added_by = request.user
            expense.save()
            messages.success(request, "Expense added successfully!")
            return redirect('expenses')
    else:
        form = ExpenseForm()

    # 2. Get Expense List (Newest first)
    expenses = Expense.objects.all().order_by('-date_added')

    context = {
        'form': form,
        'expenses': expenses,
    }
    return render(request, 'core/expenses.html', context)

# --- DELETE EXPENSE ---
@login_required
def delete_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk)
    expense.delete()
    messages.success(request, "Expense deleted.")
    return redirect('expenses')


@login_required
def reports_view(request):
    return render(request, 'core/reports.html')

@login_required
def customers_view(request):
    return render(request, 'core/customers.html')

@login_required
def staff_view(request):
    return render(request, 'core/staff.html')

@login_required
def suppliers_view(request):
    return render(request, 'core/suppliers.html')

@login_required
def invoice_view(request):
    return render(request, 'core/invoice.html')