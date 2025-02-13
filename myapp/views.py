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
@login_required
def profile(request):
    user = request.user
    user_profile = user.profile  # Assuming OneToOne relationship with UserProfile

    # Redirect to labor dashboard if the user is a laborer
    if hasattr(user, 'labour_profile'):
        return redirect('labour_dashboard')

    # Handle profile update when the request method is POST
    if request.method == 'POST':
        # Get data from the form
        phone = request.POST.get('phone', user_profile.phone)  # Default to existing phone if not provided
        address = request.POST.get('address', user_profile.address)  # Default to existing address if not provided
        profile_picture = request.FILES.get('profile_picture')  # Get uploaded file, if any

        # Only update the user_profile fields if the data is provided or changed
        if phone != user_profile.phone:
            user_profile.phone = phone

        if address != user_profile.address:
            user_profile.address = address

        if profile_picture:  # If there's a new profile picture
            user_profile.profile_picture = profile_picture

        user_profile.save()  # Save the UserProfile model

        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')  # Redirect to the profile view after saving

    return render(request, 'profile.html', {
        'user': user,
        'user_profile': user_profile,  # Pass user profile to the template
    })

def user_signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        profile_photo = request.FILES.get('profile_photo')

        # Check if email is provided
        if not email:
            messages.error(request, "Email is required.")
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
        UserProfile.objects.create(user=user, profile_photo=profile_photo if profile_photo else None)  # Create profile
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

    # Fetch the last booking history (if any)
    booking_history = Booking.objects.filter(labour=labour).order_by('-booking_time')[:5]

    # Handle profile update
    if request.method == 'POST':
        phone = request.POST.get('phone')
        experience = request.POST.get('experience')
        email = request.POST.get('email')

        # Validate phone and email
        if len(phone) != 10:  # Example phone validation
            messages.error(request, "Phone number must be 10 digits.")
        elif not '@' in email:  # Example email validation
            messages.error(request, "Invalid email format.")
        else:
            labour.phone = phone
            labour.experience = experience
            labour.email = email

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

@login_required
def book_labour(request, labour_id):

    labour = get_object_or_404(Labour, id=labour_id)
    
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

        # Create a booking
        booking = Booking.objects.create(
            user=request.user,
            labour=labour,
            expected_time=expected_time,
            email=email,
            status='pending',  # Set status to pending until payment is completed
        )

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



@login_required
def payment_page(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id)
    labour = booking.labour

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    total_amount = booking.amount or (labour.price if labour and labour.price else 0)

    if request.method == 'POST':
        amount_in_paise = int(total_amount * 100)
        try:
            # Create Razorpay order
            razorpay_order = client.order.create({
                'amount': amount_in_paise,
                'currency': 'INR',
                'payment_capture': '1'  # Auto-capture payment
            })
            print(f"Razorpay Order: {razorpay_order}")  # Debug API response

            # Save Razorpay order ID to the booking
            booking.razorpay_order_id = razorpay_order['id']
            booking.save()
            print(f"Saved Razorpay Order ID: {booking.razorpay_order_id}")  # Debug saved ID

            # Define razorpay_order_id for the template
            razorpay_order_id = razorpay_order['id']
            print(f"Order ID Passed to Template: {razorpay_order_id}")  # Debug

            # Render the payment page with Razorpay details
            return render(request, 'payment_page.html', {
                'booking': booking,
                'razorpay_order_id': razorpay_order_id,  # Pass the order ID
                'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                'amount': total_amount,
            })

        except razorpay.errors.BadRequestError as e:
            print(f"Razorpay Bad Request Error: {str(e)}")  # Debug errors
            messages.error(request, f"Bad request to Razorpay: {str(e)}")
        except razorpay.errors.ServerError as e:
            print(f"Razorpay Server Error: {str(e)}")  # Debug errors
            messages.error(request, f"Razorpay server error: {str(e)}")
        except Exception as e:
            print(f"Unexpected Error: {str(e)}")  # Debug errors
            messages.error(request, f"An unexpected error occurred: {str(e)}")

        # If there's an error, redirect back to the payment page with an error message
        return render(request, 'payment_page.html', {
            'booking': booking,
            'error': 'Unable to initialize payment. Please try again later.',
            'amount': total_amount,
        })

    # For GET requests, render the payment page
    return render(request, 'payment_page.html', {
        'booking': booking,
        'razorpay_order_id': booking.razorpay_order_id,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
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
            # Verify Razorpay payment
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

            print(f"Order ID Passed to Template: {razorpay_order['id']}")

            # Generate PDF receipt
            pdf_content = render_to_pdf('booking_success.html', {
                'booking_id': booking.booking_id,
                'labour': booking.labour.user.username,
                'expected_time': booking.expected_time,
                'amount': booking.labour.price,
            })

            # Send confirmation email with PDF receipt
            send_booking_email(booking, pdf_content, amount=booking.labour.price)

            # Log payment in history
            History.objects.create(
                user=request.user,
                action_type='Payment',
                service='Home Help Service',
                details=f"Payment of ₹{booking.labour.price} for Booking ID {booking.booking_id} was successful."
            )

            messages.success(request, 'Payment successful!')
            return redirect('booking_success', booking_id=booking.booking_id)

        except razorpay.errors.SignatureVerificationError:
            messages.error(request, 'Payment verification failed. Please try again.')
            return redirect('payment_failure')

        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('payment_failure')

    return render(request, 'payment_failure.html')



def payment_failure(request):
    return render(request, 'payment_failure.html', {
        'message': 'Unfortunately, your payment could not be processed. Please try again or contact support.',
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
    # Fetch the booking using the booking_id (assuming it's a string field in the model)
    booking = get_object_or_404(Booking, booking_id=booking_id)

    context = {
        'booking_id': booking.booking_id,
        'service': 'Home Labour Service',
        'labour': booking.labour.user.username,
        'estimated_arrival': booking.expected_time,
        'skills': booking.labour.skills.all(),
    }

    if request.GET.get('download') == 'pdf':
        return render_to_pdf('booking_success.html', context)  # Render PDF if requested
    
    return render(request, 'booking_success.html', context)  # Render normal template


def services(request):
    query = request.GET.get('query', '')
    
    if query:
        # Filter the labours based on their skills (case-insensitive search)
        labours = Labour.objects.filter(skills__name__icontains=query).distinct()
    else:
        # If no search query, retrieve all labour records
        labours = Labour.objects.all()
     # Calculate average rating for each labour
    
    for labour in labours:
        avg_rating = labour.reviews.aggregate(Avg('rating'))['rating__avg']
        # Check if avg_rating is not None and round it to one decimal place
        labour.avg_rating = round(avg_rating, 1) if avg_rating is not None else 'N/A'

    return render(request, 'services.html', {'labours': labours, 'query': query}) 

@login_required
def profile(request):
    return render(request,'profile.html')
def contact(request):
    return render(request,'contact.html')
# Booking and history for logged-in users
@login_required
def booking_history(request):
    # Fetch bookings and prefetch related labour and skills
    bookings = Booking.objects.filter(user=request.user).prefetch_related('labour__skills').order_by('-expected_time')

    # Fetch user history
    histories = History.objects.filter(user=request.user).order_by('-timestamp')
     # Fetch reviews for each booking
    # for booking in bookings:
    #     booking.reviews = Review.objects.filter(booking=booking)
    # Render booking and history in the same template
    return render(request, 'history.html', {
        'username': request.user.username,
        'bookings': bookings,
        'histories': histories
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
    return render(request, 'labour_detail.html', {'labour': labour})






def transaction_history(request):
    payments = Payment.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'payments': payments
    }
    return render(request, 'transaction_history.html', context)


