from django import forms
from django.core.validators import MaxValueValidator
from .models import CartItem


class AddToCartForm(forms.Form):
    size_id = forms.IntegerField(required=False)
    quantity = forms.IntegerField(min_value=1, initial=1)

    def __init__(self, *args, product=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.product = product
        if product:
            sizez = product.product_sizes.filter(stock__gt=0)

            if sizez.exists():
                self.fields["size_id"] = forms.ChoiceField(
                    choices=[
                        (
                            product_size.id,
                            product_size.size.name,
                        )
                        for product_size in sizez
                    ],
                    required=True,
                    initial=sizez.first().id,
                )


class UpdateCartItemForm(forms.ModelForm):
    class Meta:
        model = CartItem
        fields = ["quantity"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.product_size:
            # Додаємо валідатор автоматично
            self.fields["quantity"].validators.append(
                MaxValueValidator(self.instance.product_size.stock)
            )
