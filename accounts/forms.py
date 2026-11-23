from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class SignUpForm(UserCreationForm):
    SIGNUP_ROLES = [
        (User.Role.CUSTOMER, User.Role.CUSTOMER.label),
        (User.Role.OWNER, User.Role.OWNER.label),
        (User.Role.COURIER, User.Role.COURIER.label),
    ]
    role = forms.ChoiceField(choices=SIGNUP_ROLES)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "role")
