
from django.urls import path
from . import views

urlpatterns = [
    # Home and Authentication
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('signup/', views.user_signup, name='signup'),
    path('otp-verification/', views.otp_verification, name='otp_verification'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('request-otp/', views.request_otp, name='request_otp'),
    path('read/',views.read,name='read'),


    # Labour-specific URLs
    path('labour/login/', views.labour_login, name='labour_login'),
    path('labour/dashboard/', views.labour_dashboard, name='labour_dashboard'),
    path('labour/signup/', views.labour_signup, name='labour_signup'),



    # Booking and Payment
    path('book/<int:labour_id>/', views.book_labour, name='book_labour'),
    path('payment/<str:booking_id>/', views.create_order, name='payment_page'),
    path('payment/success/<str:booking_id>/', views.payment_success, name='payment_success'),
    path('payment/failure/<str:booking_id>/', views.payment_failure, name='payment_failure'),
    path('booking-success/<str:booking_id>/', views.booking_success, name='booking_success'),

    # Services and Labour Details
    path('services/',views.services,name='services'),
    path('labour/<int:labour_id>/', views.labour_detail, name='labour_detail'),

    # User Profile and History
    path('profile/',views.profile,name='profile'),
    path('history/', views.booking_history, name='history'),
    path('transaction/history/', views.transaction_history, name='transaction_history'),
    path('labour/<int:labour_id>/review/', views.review_labour, name='review_labour'),
    

    # Contact
    path('contact/',views.contact,name='contact'),
    path('about/',views.about,name='about'),


    # Custom  Admin Panel 
    path('dashboard/', views.dashboard, name='dashboard'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('manage-labours/', views.manage_labours, name='manage_labours'),
    path('manage-bookings/', views.manage_bookings, name='manage_bookings'),
    path('add-labour/', views.add_labour, name='add_labour'),
    path('edit-labour/<int:labour_id>/', views.edit_labour, name='edit_labour'),
    path('delete-labour/<int:labour_id>/', views.delete_labour, name='delete_labour'),
]