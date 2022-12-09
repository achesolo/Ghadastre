from django.urls import path
from . views import sign_in_view, sign_out_view, sign_up_view, account_settings_view, \
    edit_name_view, edit_username_view, edit_email_view, edit_password_view, \
    contributors_view

urlpatterns = [
    path('signin/', sign_in_view, name='signin'),
    path('signout/', sign_out_view, name='signout'),
    path('signup/', sign_up_view, name='signup'),
    path('accountsettings/', account_settings_view, name='accountsettings'),
    path('editname/', edit_name_view, name='editname'),
    path('editusername/', edit_username_view, name='editusername'),
    path('editemail/', edit_email_view, name='editemail'),
    path('editpassword/', edit_password_view, name='editpassword'),
    path('contributors/', contributors_view, name='contributors'),
]