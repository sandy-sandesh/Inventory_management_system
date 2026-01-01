from django import forms
from .models import Item, Category, Transaction

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.username = self.cleaned_data["email"]  # Use email as username
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput)

class ItemForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.none(),
        required=False,
        empty_label="--- Select Category ---",
        widget=forms.Select(attrs={
            'class': 'form-control',
            'data-bs-toggle': 'tooltip',
            'title': 'Select a category for the item (optional)'
        })
    )

    class Meta:
        model = Item
        fields = ['name', 'category', 'stock', 'price']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
    
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter categories to only the current user's categories
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)
        else:
            self.fields['category'].queryset = Category.objects.none()
class TransactionForm(forms.ModelForm):
    item = forms.ModelChoiceField(
        queryset=Item.objects.none(),
        required=True,
        label="Select Item"
    )
    
    class Meta:
        model = Transaction
        fields = ['item', 'amount']
        widgets = {
            'item': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Sale amount in Rs.'
            }),
        }
    
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            # Only show items for this user
            self.fields['item'].queryset = Item.objects.filter(user=user)
        self.fields['item'].label = "Item Sold"
        self.fields['amount'].label = "Sale Amount (Rs.)"