from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.mail import send_mail
from .models import Customer, Order
from .forms import OrderForm, CustomerForm, BroadcastForm

@login_required
def dashboard(request):
    return render(request, 'store_crm/dashboard.html')

@login_required
def order_list(request):
    orders = Order.objects.all().order_by('-created_at')

    product_filter = request.GET.get('product')
    customer_filter = request.GET.get('customer')

    if product_filter:
        orders = orders.filter(product__icontains=product_filter)
    if customer_filter:
        orders = orders.filter(customer__name__icontains=customer_filter)

    return render(request, 'store_crm/order_list.html', {'orders': orders})

@login_required
def order_create(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Извлекаем данные клиента
            name = form.cleaned_data['customer_name']
            phone = form.cleaned_data['customer_phone']
            email = form.cleaned_data['customer_email']
            city = form.cleaned_data['customer_city']
            street = form.cleaned_data['customer_street']
            district = form.cleaned_data['customer_district']
            house = form.cleaned_data['customer_house']

            # Получаем или создаем клиента
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

            # Создаем заказ
            order = form.save(commit=False)
            order.customer = customer
            order.save()

            messages.success(request, 'Заказ успешно создан!')
            return redirect('order_list')
    else:
        form = OrderForm()

    return render(request, 'store_crm/order_form.html', {'form': form, 'title': 'Добавить заказ'})

@login_required
def order_edit(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        # В режиме редактирования, для простоты, редактируем только продукт.
        # Если нужно менять клиента, лучше делать это через профиль клиента.
        order.product = request.POST.get('product', order.product)
        order.save()
        messages.success(request, 'Заказ успешно обновлен!')
        return redirect('order_list')
    return render(request, 'store_crm/order_edit.html', {'order': order})

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
        customers = customers.filter(orders__product__icontains=product_filter).distinct()

    if request.method == 'POST':
        selected_customer_ids = request.POST.getlist('customers')
        form = BroadcastForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            selected_customers = Customer.objects.filter(id__in=selected_customer_ids)
            emails = [c.email for c in selected_customers if c.email]

            if emails:
                send_mail(
                    subject,
                    message,
                    'from@example.com', # Заменить на реальный отправитель
                    [],
                    fail_silently=False,
                    bcc=emails
                )
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
