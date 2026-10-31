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
    product = models.CharField(max_length=255, verbose_name="Товар")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"Заказ: {self.product} ({self.customer.name})"
