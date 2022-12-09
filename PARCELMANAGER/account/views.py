from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import SignInForm, SignUpForm, EditNameForm, EditEmailForm, EditPasswordForm, EditUsernameForm
from django.contrib.auth.models import User

# Create your views here.


def sign_in_view(request):
    user_username = ""
    user_password = ""
    login_valid = True

    form = SignInForm()
    if request.method == "POST":
        form = SignInForm(request.POST)
        if form.is_valid():
            cleaned_form_data = form.cleaned_data
            user_username = cleaned_form_data['username']
            user_password = cleaned_form_data['password']

            user = authenticate(username=user_username, password=user_password)

            if user is not None:
                if user.is_active:
                    login(request, user)
                    # return HttpResponse('Authenticated successfully')
                    return redirect('homepage')

                else:
                    return HttpResponse('Disabled account')
                    # Will put the page to the disabled account here

            else:
                form = SignInForm(request.POST)
                login_valid = False

        else:
            form = SignInForm(request.POST)

    return render(request, 'account/sign_in.html',
                  {'form': form, 'login_valid': login_valid,
                   'username': user_username, 'password': user_password})


def sign_out_view(request):
    logout(request)
    return redirect('homepage')


def sign_up_view(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            cleaned_form_data = form.cleaned_data
            user_username = cleaned_form_data['username']
            user_email = cleaned_form_data['email']
            user_password1 = cleaned_form_data['password1']
            user_password2 = cleaned_form_data['password2']

            if user_password1 == user_password2:
                # Checking to see if the username exists
                old_user = authenticate(username=user_username, password=user_password1)

                if old_user:
                    return HttpResponse("Account with the username already exists")

                else:
                    try:
                        new_user = User.objects.create_user(
                            username=user_username, email=user_email, password=user_password1)
                        new_user.save()

                        # Logging in  the new user before redirecting to the homepage
                        login(request, new_user)

                        return redirect("homepage")

                    except:
                        return HttpResponse("Sorry Something went wrong")

            else:
                form = SignUpForm(request.POST)

        else:
            form = SignUpForm()

    return render(request, 'account/sign_up.html', {'form': form})


def account_settings_view(request):
    user = None
    if request.user.is_authenticated:
        user = User.objects.get(pk=request.user.id)

    return render(request, 'account/account_settings.html', {'user': user})


def edit_name_view(request):
    form = EditNameForm()
    if request.method == "POST":
        form = EditNameForm(request.POST)
        if form.is_valid():
            cleaned_form_data = form.cleaned_data
            user_firstname = cleaned_form_data['firstname']
            user_lastname = cleaned_form_data['lastname']

            if request.user.is_authenticated:
                user = User.objects.get(pk=request.user.id)
                user.first_name = user_firstname
                user.last_name = user_lastname
                user.save()

                # Logging in the user
                login(request, user)

                return redirect("account_settings")

        else:
            form = EditNameForm(request.POST)

    return render(request, "account/edit_name.html", {'form': form})


def edit_username_view(request):
    form = EditUsernameForm()
    if request.method == "POST":
        form = EditUsernameForm(request.POST)
        if form.is_valid():
            cleaned_form_data = form.cleaned_data
            user_username = cleaned_form_data['username']

            if request.user.username == user_username:
                if request.user.is_authenticated:
                    user = User.objects.get(pk=request.user.id)
                    user.username = user_username
                    user.save()

                    return redirect("account_settings")

            else:
                # Checking if the username exists
                if not User.objects.filter(username__exact=user_username).exists():
                    if request.user.is_authenticated:
                        user = User.objects.get(pk=request.user.id)
                        user.username = user_username
                        user.save()

                        # Logging in the user
                        login(request, user)

                        return redirect("account_settings")

                else:
                    return HttpResponse("Username already exists")

        else:
            form = EditUsernameForm(request.POST)

    return render(request, "account/edit_username.html", {'form': form})


def edit_email_view(request):
    form = EditEmailForm()
    if request.method == "POST":
        form = EditEmailForm(request.POST)
        if form.is_valid():
            cleaned_form_data = form.cleaned_data
            user_email = cleaned_form_data['email']

            if request.user.is_authenticated:
                user = User.objects.get(pk=request.user.id)
                user.email = user_email
                user.save()

                # Logging in the user
                login(request, user)

                return redirect("account_settings")

        else:
            form = EditEmailForm(request.POST)

    return render(request, "account/edit_email.html", {'form': form})


def edit_password_view(request):
    user_password1 = ""
    user_password2 = ""

    form = EditPasswordForm()
    if request.method == "POST":
        form = EditPasswordForm(request.POST)
        if form.is_valid():
            cleaned_form_data = form.cleaned_data
            user_password1 = cleaned_form_data['password1']
            user_password2 = cleaned_form_data['password2']

            if user_password1 == user_password2:
                if request.user.is_authenticated:
                    user = User.objects.get(pk=request.user.id)
                    user.set_password(user_password1)
                    user.save()

                    # Logging in the user after saving the password
                    login(request, user)

                    return redirect("account_settings")

            else:
                form = EditPasswordForm(request.POST)

        else:
            form = EditPasswordForm(request.POST)

    return render(request, "account/edit_password.html", {'form': form, 'password1': user_password1,
                                                          'password2': user_password2})


def contributors_view(request):
    return render(request, "account/contributors.html")