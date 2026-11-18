from django import forms

from .models import FoodCategory, FoodProduct


class FoodProductForm(forms.ModelForm):
    class Meta:
        model = FoodProduct
        fields = [
            "name",
            "description",
            "category",
            "price",
            "image",
            "is_vegetarian",
        ]

    def __init__(self, *args, restaurant, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = FoodCategory.objects.filter(
            restaurant=restaurant
        ).order_by("name")
        self.fields["category"].required = False
