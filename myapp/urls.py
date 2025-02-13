from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('read/',views.read,name='read'),
    path('login/', views.login, name='login'),
    path('',views.home,name='home'),
    path('signup/',views.user_signup,name='signup'),
    path('services/',views.services,name='services'),
    path('book/<int:labour_id>/', views.book_labour, name='book_labour'),
    path('booking-success/<str:booking_id>/', views.booking_success, name='booking_success'),
    path('logout/', views.logout, name='logout'),
    path('labour/login/', labour_login, name='labour_login'),
    path('labour/dashboard/', labour_dashboard, name='labour_dashboard'),
    path('labour/signup/', labour_signup, name='labour_signup'),
    path('profile/',views.profile,name='profile'),
    path('contact/',views.contact,name='contact'),
    #path('booking_history/', booking_history, name='booking_history'),
    path('history/', booking_history, name='history'), 
    path('otp-verification/', views.otp_verification, name='otp_verification'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('request-otp/', views.request_otp, name='request_otp'),
    path('labour/<int:labour_id>/review/', review_labour, name='review_labour'),
    path('labour/<int:labour_id>/', views.labour_detail, name='labour_detail'),
    path('payment/<str:booking_id>/', views.payment_page, name='payment_page'),
    path('payment/success/<str:booking_id>/', views.payment_success, name='payment_success'),
    path('payment/failure/', views.payment_failure, name='payment_failure'),
    path('transaction/history/', views.transaction_history, name='transaction_history'),

]