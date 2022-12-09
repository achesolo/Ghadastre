from django import forms


class SignInForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class SignUpForm(forms.Form):
    username = forms.CharField()
    email = forms.EmailField()
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)


class EditEmailForm(forms.Form):
    email = forms.EmailField()


class EditNameForm(forms.Form):
    firstname = forms.CharField()
    lastname = forms.CharField()


class EditUsernameForm(forms.Form):
    username = forms.CharField()


class EditPasswordForm(forms.Form):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
