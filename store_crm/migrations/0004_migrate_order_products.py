from django.db import migrations

def move_products_to_items(apps, schema_editor):
    Order = apps.get_model('store_crm', 'Order')
    OrderItem = apps.get_model('store_crm', 'OrderItem')

    for order in Order.objects.all():
        if order.product:
            OrderItem.objects.create(order=order, name=order.product)

def reverse_products_to_items(apps, schema_editor):
    Order = apps.get_model('store_crm', 'Order')

    for order in Order.objects.all():
        first_item = order.items.first()
        if first_item:
            order.product = first_item.name
            order.save()

class Migration(migrations.Migration):

    dependencies = [
        ('store_crm', '0003_order_total_cost_alter_order_product_orderitem'),
    ]

    operations = [
        migrations.RunPython(move_products_to_items, reverse_products_to_items),
    ]
