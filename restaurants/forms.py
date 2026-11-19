from django import forms

from .models import FoodCategory, FoodProduct, OpeningHour


class FoodProductForm(forms.ModelForm):
    class Meta:
        model = FoodProduct
        fields = (
            "name",
            "description",
            "category",
            "price",
            "image",
            "is_vegetarian",
        )

    def __init__(self, *args, restaurant, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = FoodCategory.objects.filter(
            restaurant=restaurant
        ).order_by("name")
        self.fields["category"].required = False


class OpeningHoursForm(forms.Form):
    def __init__(self, *args, opening_hours=None, **kwargs):
        super().__init__(*args, **kwargs)
        existing = {hour.day_of_week: hour for hour in (opening_hours or [])}
        self.day_rows = []
        self.day_prefixes = []

        for day_value, day_label in OpeningHour.DayOfWeek.choices:
            prefix = day_label.lower()
            hour = existing.get(day_value)
            closed_name = f"{prefix}_is_closed"
            open_name = f"{prefix}_open_time"
            close_name = f"{prefix}_close_time"

            self.fields[closed_name] = forms.BooleanField(
                required=False,
                label="Closed all day",
                initial=hour.is_closed if hour else False,
            )
            self.fields[open_name] = forms.TimeField(
                required=False,
                label="Opens",
                input_formats=["%H:%M"],
                widget=forms.TimeInput(format="%H:%M", attrs={"type": "time"}),
                initial=hour.open_time if hour else None,
            )
            self.fields[close_name] = forms.TimeField(
                required=False,
                label="Closes",
                input_formats=["%H:%M"],
                widget=forms.TimeInput(format="%H:%M", attrs={"type": "time"}),
                initial=hour.close_time if hour else None,
            )
            self.day_prefixes.append((day_value, prefix))
            self.day_rows.append(
                {
                    "label": day_label,
                    "is_closed": self[closed_name],
                    "open_time": self[open_name],
                    "close_time": self[close_name],
                }
            )

    def clean(self):
        cleaned_data = super().clean()
        for _, prefix in self.day_prefixes:
            if cleaned_data.get(f"{prefix}_is_closed"):
                continue
            if not cleaned_data.get(f"{prefix}_open_time"):
                self.add_error(f"{prefix}_open_time", "Enter an opening time or mark the day closed.")
            if not cleaned_data.get(f"{prefix}_close_time"):
                self.add_error(f"{prefix}_close_time", "Enter a closing time or mark the day closed.")
        return cleaned_data
