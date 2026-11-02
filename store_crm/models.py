from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Имя и Фамилия")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    email = models.EmailField(blank=True, null=True, verbose_name="Почта")
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name="Город")
    street = models.CharField(max_length=255, blank=True, null=True, verbose_name="Улица")
    district = models.CharField(max_length=100, blank=True, null=True, verbose_name="Район")
    house = models.CharField(max_length=50, blank=True, null=True, verbose_name="Дом")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders', verbose_name="Клиент")
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Общая стоимость", default=0)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"Заказ #{self.pk} ({self.customer.name})"

class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название товара")
    rrp = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="РРЦ", blank=True, null=True)
    quantity = models.IntegerField(default=0, verbose_name="Количество")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Заказ")
    name = models.CharField(max_length=255, verbose_name="Название товара")

    def __str__(self):
        return self.name
