from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Category, Transactions
from django.contrib.auth.decorators import login_required


# change format of date and time to shamsi
def format_date_time(transaction):
    Tr_date,Tr_time = transaction.transaction_date,transaction.transaction_time
    if Tr_date:
        transaction.transaction_date = Tr_date.strftime('%Y/%m/%d')
    if Tr_time:
        transaction.transaction_time = Tr_time.strftime('%H:%M')
    return transaction


@login_required(login_url='login')
# category view 
def show_category(request):
    context = {}
    if request.user.is_authenticated:
        if request.method == 'POST':
            category_name = request.POST.get('cat_name')
            user_id = request.POST.get('user_id')
            
            if not category_name:
                messages.error(request, 'Category name cannot be empty.')
            elif Category.objects.filter(category_name=category_name, user_id=user_id).exists():
                messages.error(request, 'You have already created this category.')
            else:
                category = Category(category_name=category_name, user_id=user_id)
                category.save()
                return redirect('add_category')
        
        category_list = Category.objects.filter(user_id=0)
        category_user_add = Category.objects.filter(user_id=request.user.id)
        context = {
            'category': category_list,
            'category_user': category_user_add
        }
    
    return render(request, 'transactions/category.html', context)


@login_required(login_url='login')
# transaction view
def transaction(request):
    context = {}
    if request.user.is_authenticated:
        if request.method == 'POST':
            amount = request.POST.get('amount')
            transaction_type = request.POST.get('transactionType')
            transaction_date = request.POST.get('transactionDate')
            transaction_time = request.POST.get('transactionTime')
            transaction_category = request.POST.get('category')
            user_id = request.POST.get('user_id')
            description = request.POST.get('description')

            print(amount,transaction_type,transaction_date,transaction_time,transaction_category,user_id,description)
            if amount and transaction_type and transaction_date and transaction_time and transaction_category:
                transaction_date = transaction_date.replace('/', '-')
                transaction = Transactions(
                    amount=amount,
                    transaction_type=transaction_type,
                    transaction_date=transaction_date,
                    transaction_time=transaction_time,
                    category_id= Category.objects.get(id=transaction_category, user_id__in=[user_id, 0]),
                    user_id=user_id,
                    description=description
                )
                transaction.save()
                return redirect('transactions')
            else:
                messages.error(request, 'All fields are required.')
        
        transaction_outcome = Transactions.objects.order_by('-transaction_date','-transaction_time').filter(user_id=request.user.id, transaction_type='outcome')
        transaction_income = Transactions.objects.order_by('-transaction_date','-transaction_time').filter(user_id=request.user.id, transaction_type='income')
        category_list = Category.objects.filter(user_id=0) | Category.objects.filter(user_id=request.user.id)

       # Format dates and times for display
        transaction_outcome = [format_date_time(txn) for txn in transaction_outcome]
        transaction_income = [format_date_time(txn) for txn in transaction_income]

        context = {
            'transaction_outcome': transaction_outcome,
            'transaction_income': transaction_income,
            'category': category_list,
        }

    return render(request, 'transactions/transactions.html', context)
