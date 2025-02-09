from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from allauth.account.forms import SignupForm
from .models import CustomUser, StudentVerification
from django.contrib.auth.hashers import make_password


class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label='First Name')
    last_name = forms.CharField(max_length=30, label='Last Name')
    business_name = forms.CharField(max_length=200, required=False, label='Business Name')

    def save(self, request):
        user = super().save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.business_name = self.cleaned_data.get('business_name')
                # Ensure the password is hashed
        if not user.password.startswith("pbkdf2_sha256$"):
            user.password = make_password(user.password)
        user.save()

        return user
    

class CustomUserCreationForm(UserCreationForm):
    business_name = forms.CharField(max_length=200, required=False)
    business_type = forms.ChoiceField(choices=CustomUser.BUSINESS_TYPE_CHOICES, required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2', 'business_name', 'business_type']

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'business_name', 'business_type', 'phone_number']

class StudentVerificationForm(forms.ModelForm):
    class Meta:
        model = StudentVerification
        fields = ['institution', 'student_id', 'verification_document']
        widgets = {
            'verification_document': forms.FileInput()
        }
'''class CustomSignupForm(SignupForm):
    business_name = forms.CharField(max_length=200, required=False)
    business_type = forms.ChoiceField(choices=CustomUser.BUSINESS_TYPE_CHOICES, required=False)

    def save(self, request):
        user = super().save(request)
        user.business_name = self.cleaned_data.get('business_name')
        user.business_type = self.cleaned_data.get('business_type')
        user.save()
        return user'''
