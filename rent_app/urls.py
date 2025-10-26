from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'rent_app'

urlpatterns = [
    # Authentication
    path('', auth_views.LoginView.as_view(template_name='rent_app/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('password_change/', auth_views.PasswordChangeView.as_view(
        template_name='rent_app/password_change.html',
        success_url='/password_change_done/'
    ), name='password_change'),
    path('password_change_done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='rent_app/password_change_done.html'
    ), name='password_change_done'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Rent management
    path('rent/', views.rent_status, name='rent_status'),

    # Utility bills
    path('utilities/', views.utility_bills, name='utility_bills'),
    path('utilities/<int:bill_id>/download/', views.download_bill, name='download_bill'),

    # Meter readings
    path('meters/', views.meter_readings, name='meter_readings'),
    path('meters/submit/', views.submit_meter_reading, name='submit_meter_reading'),
]
