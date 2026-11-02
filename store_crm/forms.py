from django import forms
from .models import Customer, Order

class OrderForm(forms.ModelForm):
    # Дополнительные поля для создания клиента
    customer_name = forms.CharField(max_length=255, label="Имя и Фамилия", required=True)
    customer_phone = forms.CharField(max_length=20, label="Телефон", required=True)
    customer_email = forms.EmailField(label="Почта", required=False)
    customer_city = forms.CharField(max_length=100, label="Город", required=False)
    customer_street = forms.CharField(max_length=255, label="Улица", required=False)
    customer_district = forms.CharField(max_length=100, label="Район", required=False)
    customer_house = forms.CharField(max_length=50, label="Дом", required=False)

    class Meta:
        model = Order
        fields = ['total_cost']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Убираем подсказки
        for field in self.fields:
            self.fields[field].help_text = None

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'phone', 'email', 'city', 'street', 'district', 'house']

class BroadcastForm(forms.Form):
    subject = forms.CharField(max_length=255, label="Тема письма", required=True)
    message = forms.CharField(widget=forms.Textarea, label="Сообщение", required=True)

from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'rrp', 'quantity']

from django.forms import inlineformset_factory
from .models import OrderItem

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['name', 'price']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название товара'}),
            'price': forms.NumberInput(attrs={'class': 'form-control price-input', 'placeholder': 'Цена'})
        }

OrderItemFormSet = inlineformset_factory(
    Order, OrderItem, form=OrderItemForm,
    extra=1, can_delete=True
)
