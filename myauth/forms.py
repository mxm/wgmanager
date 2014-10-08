from myauth.models import MyUser
from django.forms import ModelForm

"""
This form is a custom signup form for allauth. See
ACCOUNT_SIGNUP_FORM_CLASS in docs and settings.
"""
class SignupForm(ModelForm):

    class Meta:
        model = MyUser
        fields = ['first_name', 'last_name', 'email']

    def signup(self, request, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.save()
