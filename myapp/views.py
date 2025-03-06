from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, Labour, Booking,Review,UserProfile,Skill,History ,Payment# Ensure Skill and Labour models are 
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail,EmailMessage
from django.conf import settings
from .utils import render_to_pdf , generate_otp,send_otp # Import the utility function
from io import BytesIO
from django.db.models import Avg
import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
from .forms import ProfileForm



# Home view
def home(request):
    return render(request, 'home.html')

# Login view for users
def login(request):
    if request.method == 'POST':
        # Check if the user is trying to log in with a password
        if 'password' in request.POST:
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                auth_login(request, user)
                return redirect('home')  # Redirect to home page after successful login
            else:
                messages.error(request, 'Invalid username or password.')

        # Check if the user is requesting an OTP
        elif 'email' in request.POST:
            email = request.POST['email']
            try:
                user = User.objects.get(email=email)
                otp = generate_otp()
                request.session['otp'] = otp
                request.session['user_email'] = email

                # Send OTP to the user's email
                send_otp(email, otp)

                messages.success(request, 'An OTP has been sent to your email.')
                return redirect('otp_verification')  # Redirect to the OTP verification page
            except User.DoesNotExist:
                messages.error(request, 'No user associated with this email.')

    # For GET requests or if POST processing fails, render the login page
    return render(request, 'login.html')

def otp_verification(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        generated_otp = request.session.get('otp')

        if str(entered_otp) == str(generated_otp):
            # Fetch the user and log them in
            email = request.session.get('user_email')
            user = User.objects.get(email=email)
            auth_login(request, user)
            del request.session['otp']  # Clear OTP from session after successful login
            del request.session['user_email']  # Clear email from session
            return redirect('home')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')

    return render(request, 'otp_verification.html')

def request_otp(request):
    if request.method == 'POST':
        user_email = request.POST.get('email')  # Get email from user input
        try:
            user = User.objects.get(email=user_email)  # Ensure the user exists
            otp = generate_otp()  # Generate OTP
            request.session['otp'] = otp  # Save OTP in session
            request.session['user_email'] = user_email  # Save user email in session
            
            # Send OTP email
            send_otp(user_email, otp)

            messages.success(request, 'An OTP has been sent to your email.')
            return redirect('otp_verification')  # Redirect to the OTP verification page
        except User.DoesNotExist:
            messages.error(request, 'No user associated with this email.')

    return render(request, 'request_otp.html')  # Render the OTP request form
@login_required
def resend_otp(request):
    # Send OTP to the user
    send_otp(request.user)
    messages.success(request, "A new OTP has been sent to your email.")
    return redirect('otp_verification')  # Redirect back to the OTP verification page




from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.storage import default_storage
from .models import UserProfile

@login_required
def profile(request):
    # Fetch or create the UserProfile object for the logged-in user
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Debug: Print all POST data
        print("POST data:", request.POST)
        # Debug: Print all FILES data
        print("FILES data:", request.FILES)

        # Get form data
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()

        # Debug: Print phone and address
        print("Phone:", phone)
        print("Address:", address)

        # Update profile fields
        user_profile.phone = phone
        user_profile.address = address

        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            print("Profile picture uploaded:", request.FILES['profile_picture'])
            user_profile.profile_picture = request.FILES['profile_picture']

        # Save the updated profile
        user_profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')  # Redirect to the same profile page

    # Pass the user_profile and user objects to the template
    context = {
        'user_profile': user_profile,
        'user': request.user,
    }
    return render(request, 'profile.html', context)



def user_signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        # Check if all required fields are provided
        if not username or not email or not password1 or not password2:
            messages.error(request, "All fields are required.")
            return render(request, 'signup.html')

        # Check if passwords match
        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return render(request, 'signup.html')

        # Check if the email is already in use
        if User.objects.filter(email=email).exists():
            messages.error(request, "An account with this email already exists.")
            return render(request, 'signup.html')

        # Create the user if validations pass
        user = User.objects.create_user(username=username, email=email, password=password1)
        UserProfile.objects.create(user=user)  # Create profile
        auth_login(request, user)  # Log in the user after successful signup
        messages.success(request, "Signup successful. You are now logged in.")
        return redirect('login.html')  # Redirect to home or any other page after signup

    return render(request, 'signup.html')  # Render the form for GET requests

# Labour-specific login view
def labour_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user:
            if hasattr(user, 'labour_profile'):  # Checking if user has labour profile
                auth_login(request, user)
                return redirect('labour_dashboard')
            else:
                messages.error(request, 'You are not a registered labour.')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'labour_login.html')

def labour_signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        image = request.FILES.get('image')
        experience = request.POST.get('experience')
        skill_ids = request.POST.getlist('skills')

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'An account with this email already exists.')
        else:
            # Create the user and labour profile
            user = User.objects.create_user(username=username, password=password, email=email)
            labour = Labour.objects.create(
                user=user,
                phone=phone,
                image=image,
                email=email,
                experience=experience
            )
            # Assign selected skills to the labour profile
            skills = Skill.objects.filter(id__in=skill_ids)
            labour.skills.set(skills)
            auth_login(request, user)  # Log in the user after successful signup
            return redirect('labour_dashboard')

    # For GET request, provide the list of skills to the template
    skills = Skill.objects.all()
    return render(request, 'labour_signup.html', {'skills': skills})


# Dashboard for logged-in labours

@login_required
def labour_dashboard(request):
    if not hasattr(request.user, 'labour_profile'):
        return redirect('labour_signup')  # Redirect to signup if the user is not a labour

    labour = request.user.labour_profile
    skills = labour.skills.all()
    
    # Fetch the last 5 booking history
    booking_history = Booking.objects.filter(labour=labour).order_by('-booking_time')[:5]

    # Fetch payment history
    pending_payments = Payment.objects.filter(labour=labour, status="Pending")

    if request.method == 'POST':
        phone = request.POST.get('phone')
        experience = request.POST.get('experience')
        email = request.POST.get('email')
        price = request.POST.get('price')  # Get price from the form
        profile_image = request.FILES.get('image')  # Get uploaded image

        if len(phone) != 10:
            messages.error(request, "Phone number must be 10 digits.")
        elif '@' not in email:
            messages.error(request, "Invalid email format.")
        else:
            labour.phone = phone
            labour.experience = experience
            labour.email = email
            labour.price = price  # Update price

            # Update profile image if provided
            if profile_image:
                labour.image = profile_image

            # Update skills
            selected_skills = request.POST.getlist('skills', [])
            labour.skills.set(selected_skills)
            labour.save()

            messages.success(request, "Profile updated successfully.")
            return redirect('labour_dashboard')

    available_skills = Skill.objects.exclude(id__in=skills.values_list('id', flat=True))

    return render(request, 'labour_dashboard.html', {
        'labour': labour,
        'skills': skills,
        'booking_history': booking_history,
        'available_skills': available_skills,
        'pending_payments': pending_payments,
    })

# General read view to display users and labours
def read(request):
    users = User.objects.all()
    labours = Labour.objects.all()
    return render(request, 'read.html', {'users': users, 'labours': labours})

# Logout view
@login_required
def logout(request):
    # Log the logout action if the user is authenticated
    History.objects.create(user=request.user, action_type="Logged out",details='User logged out.')
    
    # Log out the user
    auth_logout(request)

    # Redirect to the home page (or wherever you want after logout)
    return redirect('home')



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta, datetime
from .models import Labour, Booking, History
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@login_required
def book_labour(request, labour_id):
    labour = get_object_or_404(Labour, id=labour_id)

    # Check if the labour is available
    if not labour.is_available and labour.last_booking_time:
        time_since_last_booking = timezone.now() - labour.last_booking_time
        if time_since_last_booking < timedelta(hours=1):
            messages.error(request, f"This labourer is currently busy. They will be available in {60 - time_since_last_booking.seconds // 60} minutes.")
            return redirect('services')
    
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        expected_time_str = request.POST.get('expected_time')

        expected_time = timezone.now()
        if expected_time_str:
            try:
                expected_time = timezone.datetime.strptime(expected_time_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                messages.error(request, 'Invalid date format for expected time. Please use YYYY-MM-DD HH:MM:SS.')
                return render(request, 'book_labour.html', {'labour': labour})

        # Calculate the total amount based on labour's price
        total_amount = labour.price if labour.price else 0

        # Create a booking
        booking = Booking.objects.create(
            user=request.user,
            labour=labour,
            expected_time=expected_time,
            email=email,
            amount=total_amount,  # Set the amount
            status='pending',  # Set status to pending until payment is completed
        )

         # Update labour's availability status and last booking time
        labour.is_available = False
        labour.last_booking_time = timezone.now()
        labour.save()

        # Log the booking action to the history
        History.objects.create(
            user=request.user,
            action_type='Booking',
            service='Home Help Service',
            details=f"Booked {labour.user.username} for {booking.expected_time}"
        )

        # Redirect to the payment page
        return redirect('payment_page', booking_id=booking.booking_id)

    return render(request, 'book_labour.html', {'labour': labour})

from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.decorators import login_required
import razorpay
from .models import Booking

@login_required
def create_order(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id)
    labour = booking.labour

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    total_amount = booking.amount or (labour.price if labour and labour.price else 0)
    amount_in_paise = int(total_amount * 100)

    if amount_in_paise < 100:
        messages.error(request, "Amount must be at least ₹1.")
        return render(request, 'payment_page.html', {
            'booking': booking,
            'error': 'Amount must be at least ₹1.',
            'amount': total_amount,
        })

    try:
        razorpay_order = client.order.create({
            'amount': amount_in_paise,
            'currency': 'INR',
            'payment_capture': '1'
        })

        booking.razorpay_order_id = razorpay_order['id']
        booking.save()

        return render(request, 'payment_page.html', {
            'booking': booking,
            'razorpay_order_id': booking.razorpay_order_id,
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'amount': total_amount,
            'amount_in_paise': amount_in_paise,
        })

    except razorpay.errors.BadRequestError as e:
        messages.error(request, f"Bad request to Razorpay: {str(e)}")
    except razorpay.errors.ServerError as e:
        messages.error(request, f"Razorpay server error: {str(e)}")
    except Exception as e:
        messages.error(request, f"An unexpected error occurred: {str(e)}")

    return render(request, 'payment_page.html', {
        'booking': booking,
        'error': 'Unable to initialize payment. Please try again later.',
        'amount': total_amount,
    })

@csrf_exempt
def payment_success(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id)

    if request.method == 'POST':
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_signature = request.POST.get('razorpay_signature')

        try:
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature,
            })

            # Update booking status
            booking.razorpay_payment_id = razorpay_payment_id
            booking.status = 'successful'
            booking.save()

            # Update labour's availability
            labour = booking.labour
            labour.is_available = False
            labour.last_booking_time = timezone.now()
            labour.save()

            # Send confirmation email
            pdf_content = render_to_pdf('booking_success.html', {
                'booking_id': booking.booking_id,
                'service': 'Home Labour Service',
                'labour': booking.labour.user.username,
                'estimated_arrival': booking.expected_time,
                'skills': booking.labour.skills.all(),
                'payment_method': 'Razorpay',
                'amount_paid': booking.amount,
                'transaction_id': razorpay_payment_id,
                'user_name': booking.user.username,
                'user_email': booking.user.email,
                'booking_date': booking.booking_time.strftime('%Y-%m-%d %H:%M:%S'),
                'is_email': False,
            })
            send_booking_email(booking, pdf_content, amount=booking.amount)

            # Log the payment action
            History.objects.create(
                user=request.user,
                action_type='Payment',
                service='Home Help Service',
                details=f"Payment of ₹{booking.amount} for Booking ID {booking.booking_id} was successful."
            )

            messages.success(request, 'Payment successful!')
            return redirect('booking_success', booking_id=booking.booking_id)

        except razorpay.errors.SignatureVerificationError as e:
            messages.error(request, 'Payment verification failed. Please try again.')
            return redirect('payment_failure', booking_id=booking.booking_id)

        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('payment_failure', booking_id=booking.booking_id)

    return render(request, 'payment_failure.html', {'booking_id': booking_id})


def payment_failure(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id)
    return render(request, 'payment_failure.html', {
        'message': 'Unfortunately, your payment could not be processed. Please try again or contact support.',
        'booking': booking,
    })
def send_booking_email(booking, pdf_content, amount):
    subject = 'Booking Confirmation'
    message = f'Dear {booking.user.username},\n\nYour booking has been confirmed.\nBooking ID: {booking.booking_id}\nAmount Paid: ₹{amount}\n\nThank you for choosing our service!'

    email = EmailMessage(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [booking.email]
    )
    
    # Attach the PDF content
    email.attach(f'booking_success_{booking.booking_id}.pdf', pdf_content, 'application/pdf')

    try:
        email.send()
        print('Email sent successfully.')
    except Exception as e:
        print(f'Error sending email: {e}')

@login_required
def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id)

    context = {
        'booking_id': booking.booking_id,
        'service': 'Home Labour Service',
        'labour': booking.labour.user.username,
        'estimated_arrival': booking.expected_time.strftime('%Y-%m-%d %H:%M:%S'),
        'skills': booking.labour.skills.all(),
        'payment_method': 'Razorpay',
        'amount_paid': booking.amount,
        # 'transaction_id': razorpay_payment_id,
        'user_name': booking.user.username,
        'user_email': booking.user.email,
        'booking_date': booking.booking_time.strftime('%Y-%m-%d %H:%M:%S'),
        'is_email': False,  # Indicates this is for browser rendering
    }

    return render(request, 'booking_success.html', context)

from django.utils import timezone
from datetime import timedelta
from django.core.paginator import Paginator
from django.db.models import Avg, Q
from django.shortcuts import render
from .models import Labour, Review

def services(request):
    query = request.GET.get('query', '')
    
    # Filter labours based on skills or name (case-insensitive search)
    if query:
        labours = Labour.objects.filter(
            Q(skills__name__icontains=query) | Q(user__username__icontains=query)
        ).distinct()
    else:
        labours = Labour.objects.all()

    # Prefetch related reviews to optimize database queries
    labours = labours.prefetch_related('reviews')

    # Calculate average rating and availability status for each labour
    for labour in labours:
        # Calculate average rating
        avg_rating = labour.reviews.aggregate(Avg('rating'))['rating__avg']
        labour.avg_rating = round(avg_rating, 1) if avg_rating is not None else 'N/A'

        # Calculate availability status
        if not labour.is_available and labour.last_booking_time:
            time_since_last_booking = timezone.now() - labour.last_booking_time
            if time_since_last_booking < timedelta(hours=1):
                labour.availability_message = f"Available in {60 - time_since_last_booking.seconds // 60} minutes"
            else:
                labour.is_available = True  # Mark as available if 1 hour has passed
                labour.save()
        else:
            labour.availability_message = "Available"

    # Pagination: Show 4 labours per page
    paginator = Paginator(labours, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'services.html', {
        'page_obj': page_obj,
        'query': query,
    })



@login_required
def profile(request):
    return render(request,'profile.html')
def contact(request):
    return render(request,'contact.html')
# Booking and history for logged-in users
@login_required
def booking_history(request):
    # Fetch bookings for the logged-in user
    bookings = Booking.objects.filter(user=request.user).prefetch_related('labour__skills').order_by('-expected_time')

    # Fetch user history (actions like bookings, transactions, etc.)
    histories = History.objects.filter(user=request.user).order_by('-timestamp')

    # Fetch payment history for the user
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')

    # Fetch reviews for each labour associated with the bookings
    for booking in bookings:
        booking.reviews = Review.objects.filter(labour=booking.labour, user=request.user)

    # Render booking, history, and payment history in the same template
    return render(request, 'history.html', {
        'username': request.user.username,
        'bookings': bookings,
        'histories': histories,
        'payments': payments
    })
@login_required
def review_labour(request, labour_id):
    labour = get_object_or_404(Labour, id=labour_id)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        # Create a new review instance
        Review.objects.create(
            labour=labour,
            user=request.user,
            rating=rating,
            comment=comment
        )
        messages.success(request, 'Your review has been submitted successfully!')
        return redirect('labour_detail', labour_id=labour.id)  # Redirect to a labour detail page

    return render(request, 'review_labour.html', {
        'labour': labour,
    })

@login_required
def labour_detail(request, labour_id):
    labour = get_object_or_404(Labour, id=labour_id)
    return render(request, 'labour_detail.html', {'labour': labour, 'is_available': labour.is_available,})






def transaction_history(request):
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'payments': payments
    }
    return render(request, 'transaction_history.html', context)



from django.core.mail import send_mail
from django.conf import settings

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        # phone = request.POST.get('phone')
        message = request.POST.get('message')

        # Send email
        subject = f"New Contact Form Submission from {name}"
        email_message = f"""
        Name: {name}
        Email: {email}
        Message: {message}
        """
        send_mail(
            subject,
            email_message,
            settings.EMAIL_HOST_USER,  # From email
            [settings.EMAIL_HOST_USER],  # To email
            fail_silently=False,
        )

        # Optionally, you can add a success message
        messages.success(request, 'Your message has been sent successfully!')
        return redirect('contact')  # Redirect to the same page after submission

    return render(request, 'contact.html')

def about(request):
    return render(request, 'about.html')


# Custom Admin Panel


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Labour, Booking, User, History
from .forms import LabourForm, BookingForm

@login_required
def dashboard(request):
    context = {
        'total_labours': Labour.objects.count(),
        'total_bookings': Booking.objects.count(),
        'total_users': User.objects.count(),
        'recent_history': History.objects.order_by('-timestamp')[:10],  # Last 10 activities
    }
    print(context)
    return render(request, 'admin/Custom_admin_dashboard.html', context)

@login_required
def manage_users(request):
    users = User.objects.all()
    return render(request, 'admin/Custom_admin_dashboard.html', {'users': users, 'active_tab': 'users'})

@login_required
def manage_labours(request):
    labours = Labour.objects.all()
    return render(request, 'admin/Custom_admin_dashboard.html', {'labours': labours, 'active_tab': 'labours'})

@login_required
def manage_bookings(request):
    bookings = Booking.objects.all()
    return render(request, 'admin/Custom_admin_dashboard.html', {'bookings': bookings, 'active_tab': 'bookings'})

@login_required
def add_labour(request):
    if request.method == 'POST':
        form = LabourForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('manage_labours')
    else:
        form = LabourForm()
    return render(request, 'admin/Custom_admin_dashboard.html', {'form': form, 'active_tab': 'labours'})

@login_required
def edit_labour(request, labour_id):
    labour = get_object_or_404(Labour, id=labour_id)
    if request.method == 'POST':
        form = LabourForm(request.POST, request.FILES, instance=labour)
        if form.is_valid():
            form.save()
            return redirect('manage_labours')
    else:
        form = LabourForm(instance=labour)
    return render(request, 'admin/Custom_admin_dashboard.html', {'form': form, 'active_tab': 'labours'})

@login_required
def delete_labour(request, labour_id):
    labour = get_object_or_404(Labour, id=labour_id)
    labour.delete()
    return redirect('manage_labours')
