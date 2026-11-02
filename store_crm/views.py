from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.mail import EmailMessage
from .models import Customer, Order, OrderItem
from .forms import OrderForm, CustomerForm, BroadcastForm, OrderItemFormSet

@login_required
def dashboard(request):
    return render(request, 'store_crm/dashboard.html')

@login_required
def order_list(request):
    orders = Order.objects.all().order_by('-created_at')

    product_filter = request.GET.get('product')
    customer_filter = request.GET.get('customer')

    if product_filter:
        orders = orders.filter(items__name__icontains=product_filter).distinct()
    if customer_filter:
        orders = orders.filter(customer__name__icontains=customer_filter)

    return render(request, 'store_crm/order_list.html', {'orders': orders})

@login_required
def order_create(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        formset = OrderItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            name = form.cleaned_data['customer_name']
            phone = form.cleaned_data['customer_phone']
            email = form.cleaned_data['customer_email']
            city = form.cleaned_data['customer_city']
            street = form.cleaned_data['customer_street']
            district = form.cleaned_data['customer_district']
            house = form.cleaned_data['customer_house']

            customer, created = Customer.objects.get_or_create(
                name=name,
                defaults={
                    'phone': phone,
                    'email': email,
                    'city': city,
                    'street': street,
                    'district': district,
                    'house': house
                }
            )

            order = form.save(commit=False)
            order.customer = customer
            order.save()

            formset.instance = order
            formset.save()

            messages.success(request, 'Заказ успешно создан!')
            return redirect('order_list')
    else:
        form = OrderForm()
        formset = OrderItemFormSet()

    return render(request, 'store_crm/order_form.html', {'form': form, 'formset': formset, 'title': 'Добавить заказ'})

@login_required
def order_edit(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        formset = OrderItemFormSet(request.POST, instance=order)
        if form.is_valid() and formset.is_valid():
            # Обновляем профиль клиента
            customer = order.customer
            customer.name = form.cleaned_data['customer_name']
            customer.phone = form.cleaned_data['customer_phone']
            customer.email = form.cleaned_data['customer_email']
            customer.city = form.cleaned_data['customer_city']
            customer.street = form.cleaned_data['customer_street']
            customer.district = form.cleaned_data['customer_district']
            customer.house = form.cleaned_data['customer_house']
            customer.save()

            form.save()
            formset.save()
            messages.success(request, 'Заказ успешно обновлен!')
            return redirect('order_list')
    else:
        form = OrderForm(instance=order, initial={
            'customer_name': order.customer.name,
            'customer_phone': order.customer.phone,
            'customer_email': order.customer.email,
            'customer_city': order.customer.city,
            'customer_street': order.customer.street,
            'customer_district': order.customer.district,
            'customer_house': order.customer.house,
        })
        formset = OrderItemFormSet(instance=order)
    return render(request, 'store_crm/order_edit.html', {'form': form, 'formset': formset, 'order': order})

@login_required
def order_delete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        order.delete()
        messages.success(request, 'Заказ успешно удален!')
        return redirect('order_list')
    return render(request, 'store_crm/order_confirm_delete.html', {'order': order})

@login_required
def customer_list(request):
    customers = Customer.objects.all().order_by('-created_at')

    search = request.GET.get('search')
    if search:
        customers = customers.filter(name__icontains=search)

    return render(request, 'store_crm/customer_list.html', {'customers': customers})

@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    return render(request, 'store_crm/customer_detail.html', {'customer': customer})

@login_required
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль клиента успешно обновлен!')
            return redirect('customer_detail', pk=customer.pk)
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'store_crm/customer_form.html', {'form': form, 'title': 'Редактировать клиента'})

@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.delete()
        messages.success(request, 'Клиент успешно удален!')
        return redirect('customer_list')
    return render(request, 'store_crm/customer_confirm_delete.html', {'customer': customer})

@login_required
def broadcast(request):
    customers = Customer.objects.exclude(email__isnull=True).exclude(email__exact='')

    product_filter = request.GET.get('product')
    if product_filter:
        # Фильтруем клиентов, у которых есть заказы с данным товаром
        customers = customers.filter(orders__items__name__icontains=product_filter).distinct()

    if request.method == 'POST':
        selected_customer_ids = request.POST.getlist('customers')
        form = BroadcastForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            selected_customers = Customer.objects.filter(id__in=selected_customer_ids)
            emails = [c.email for c in selected_customers if c.email]

            if emails:
                email = EmailMessage(
                    subject,
                    message,
                    None, # None будет использовать DEFAULT_FROM_EMAIL или переопределится SMTP сервером
                    [], # кому (пусто, чтобы не видели друг друга)
                    bcc=emails, # скрытая копия
                )
                email.send(fail_silently=False)
                messages.success(request, f'Письма успешно отправлены ({len(emails)} шт.)!')
            else:
                messages.warning(request, 'Не выбрано ни одного клиента с валидным email.')
            return redirect('broadcast')
    else:
        form = BroadcastForm()

    return render(request, 'store_crm/broadcast.html', {'customers': customers, 'form': form})

@login_required
def api_get_customer(request):
    name = request.GET.get('name', '')
    if name:
        try:
            customer = Customer.objects.get(name__iexact=name)
            data = {
                'found': True,
                'phone': customer.phone,
                'email': customer.email or '',
                'city': customer.city or '',
                'street': customer.street or '',
                'district': customer.district or '',
                'house': customer.house or '',
            }
            return JsonResponse(data)
        except Customer.DoesNotExist:
            pass
    return JsonResponse({'found': False})

from .models import Product
from .forms import ProductForm

@login_required
def product_list(request):
    query = request.GET.get('q', '')
    if query:
        products = Product.objects.filter(name__icontains=query).order_by('-created_at')
    else:
        products = Product.objects.all().order_by('-created_at')
    return render(request, 'store_crm/product_list.html', {'products': products, 'query': query})

@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Товар успешно добавлен.')
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'store_crm/product_form.html', {'form': form, 'title': 'Добавить товар'})

@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Товар успешно обновлен.')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'store_crm/product_form.html', {'form': form, 'title': 'Редактировать товар', 'product': product})

@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Товар удален.')
        return redirect('product_list')
    return render(request, 'store_crm/product_confirm_delete.html', {'product': product})
