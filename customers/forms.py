from django import forms
from .models import SavedAddress


class SavedAddressForm(forms.ModelForm):
    class Meta:
        model = SavedAddress
        fields = ["label", "zone", "street_address", "is_default"]
