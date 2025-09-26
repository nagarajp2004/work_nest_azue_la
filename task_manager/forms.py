from django import forms
from django.contrib.auth.models import User
from .models import Profile

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    designation_level = forms.IntegerField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            # Save profile with designation level
            profile, created = Profile.objects.get_or_create(user=user)
            profile.designation_level = self.cleaned_data['designation_level']
            profile.save()
        return user
