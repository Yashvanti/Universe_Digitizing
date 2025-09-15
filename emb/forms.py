from django import forms
from django.contrib.auth.models import User
from . import models


class CustomerUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), label="Password")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password']  

class CustomerForm(forms.ModelForm):
    class Meta:
        model = models.Customer
        fields = ['address', 'mobile']

    def save(self, commit=True, user=None):
        customer = super().save(commit=False)
        if user:
            customer.user = user  # ✅ Link customer to the user
        if commit:
            customer.save()
        return customer

class ProductForm(forms.ModelForm):
    class Meta:
        model=models.Product
        fields=['name','product_image']

#address of shipment
class AddressForm(forms.ModelForm):
    Email = forms.EmailField()
    Mobile= forms.IntegerField()
    Address = forms.CharField(max_length=500)

class FeedbackForm(forms.ModelForm):
    class Meta:
        model=models.Feedback
        fields=['name','feedback']

#for updating status of order
class OrderForm(forms.ModelForm):
    class Meta:
        model=models.Orders
        fields=['status']

#for contact us page

from django.core.mail import send_mail
from django.conf import settings

class ContactForm(forms.ModelForm):
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)
    email = forms.EmailField()

    def send_email(self):
        subject = self.cleaned_data['subject']
        message = self.cleaned_data['message']
        from_email = self.cleaned_data['email']
        to_email = [settings.EMAIL_RECEIVING_USER]

        send_mail(subject, message, from_email, to_email)


#Quote form

from .models import Quote  # Import your Quote model

class QuoteForm(forms.ModelForm):
    full_name = forms.CharField(max_length=100, label='Full Name')
    design_name = forms.CharField(max_length=255, label='Design Name')
    size = forms.ChoiceField(
        choices=[
            ('capfront', 'Cap Front'),
            ('leftchest', 'Left Chest'),
            ('jacketback', 'Jacket Back'),
            ('other', 'Other')
        ],
        label='Size'
    )
    phone_number = forms.CharField(max_length=15, label='Phone Number')
    email = forms.EmailField(label='Email')
    additional_info = forms.CharField(widget=forms.Textarea, required=False, label='Additional Information')

    class Meta:
        model = Quote
        fields = '__all__'  # ✅ Include all fields or specify a list

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')

        if email and '@' not in email:
            raise forms.ValidationError("Please enter a valid email address.")

        return cleaned_data

    



from .models import EmbroideryDetails

class EmbroideryForm(forms.ModelForm):
    class Meta:
        model = EmbroideryDetails
        fields = ('complexity', 'size', 'file_format', 'turnaround', 'additional_info', 'file_upload')

    

from django import forms
from .models import CheatSheet

class CheatSheetForm(forms.ModelForm):
    # keep the email if you still need it
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    # ← NEW: stitch_count field
    stitch_count = forms.IntegerField(
        label="Stitch Count",
        required=True,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '1',
            'min': '0'
        })
    )

    class Meta:
        model = CheatSheet
        fields = [
            'title',
            'stitch_count',   # ← include it here
            'file',
            'price',
            'turnaround',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'turnaround': forms.TextInput(attrs={'class': 'form-control'}),
            # you could also declare stitch_count here instead of above,
            # but since we already passed a widget on the field definition,
            # this is optional
            # 'stitch_count': forms.NumberInput(attrs={
            #     'class': 'form-control',
            #     'step': '1',
            #     'min': '0'
            # }),
        }




from django import forms
from .models import Payment

class PaymentForm(forms.ModelForm):
    payment_method = forms.ChoiceField(
        choices=[("card", "Card"), ("upi", "UPI"), ("qr", "QR Scanner")],
        widget=forms.RadioSelect
    )

    class Meta:
        model = Payment
        fields = ['payment_method']
