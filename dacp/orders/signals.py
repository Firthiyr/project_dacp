from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Order

# Використовуємо signals для того, щоб була при поверненні товару і вибору у адмінці статусу Cancelled, кількість товару що була замовлена, повернулась до бд


@receiver(pre_save, sender=Order)
def restore_stock_on_cancel(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old_order = Order.objects.get(pk=instance.pk)
    except Order.DoesNotExist:
        return

    # ЕсЯкщо статус змінився на Cancelled
    if instance.status == "cancelled" and old_order.status != "cancelled":
        # Якщо товар уже був списаний до цього (статус був processing, shipped)
        if old_order.status in ["processing", "shipped", "delivered"]:
            print(f"Restoring stock for Order #{instance.id}...")

            for item in instance.items.all():
                product_size = item.size

                product_size.stock += item.quantity
                product_size.save()

                print(
                    f"Returned {item.quantity} of {item.product.name} ({product_size.size.name}) to stock."
                )
