from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, Labour, Booking,Review,UserProfile,Skill,History # Ensure Skill and Labour models are correctly imported
from django.utils import timezone
from django.core.mail import send_mail,EmailMessage
from django.conf import settings
from .utils import render_to_pdf , generate_otp,send_otp # Import the utility function
from io import BytesIO
from django.db.models import Avg



# Home view
def home(request):
    return render(request, 'home.html')

# Login view for users
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            # Check if the email is registered
            if not user.email:  # Email is missing
                messages.error(request, 'Email is not registered. Please update your profile.')
                return redirect('profile')  # Redirect to profile update page
        
        if user:
            otp = generate_otp()  # Generate OTP
            request.session['otp'] = otp  # Store OTP in session
            request.session['username'] = username  # Store username in session
            
            send_otp(user.email, otp)  # Send OTP via email
            
            return redirect('otp_verification')  # Redirect to OTP verification page
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'login.html')

def otp_verification(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        generated_otp = request.session.get('otp')
        
        if str(entered_otp) == str(generated_otp):
            # Log in the user
            username = request.session.get('username')
            user = User.objects.get(username=username)
            if user:
                auth_login(request, user)  # Log the user in
                return redirect('home')  # Redirect to home page
        else:
            messages.error(request, 'Invalid OTP')
    
    return render(request, 'otp_verification.html')

@login_required
def resend_otp(request):
    # Send OTP to the user
    send_otp(request.user)
    messages.success(request, "A new OTP has been sent to your email.")
    return redirect('otp_verification')  # Redirect back to the OTP verification page
@login_required
def profile(request):
    user = request.user
    user_profile = user.profile  # Assuming a OneToOne relationship with UserProfile

    # Redirect to labor dashboard if the user is a laborer
    if hasattr(user, 'labour_profile'):
        return redirect('labour_dashboard')
    # Handle profile update
    if request.method == 'POST':
        # Get data from the form
        email = request.POST.get('email', user.email)
        username = request.POST.get('username', user.username)
        phone = request.POST.get('phone', user_profile.phone)
        address = request.POST.get('address', user_profile.address)

        # Update user details
        user.email = email
        user.username = username
        user_profile.phone = phone
        user_profile.address = address
        
        user.save()
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
        auth_login(request, user)  # Log in the user after successful signup
        messages.success(request, "Signup successful. You are now logged in.")
        return redirect('home')  # Redirect to home or any other page after signup

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
            status='successful',  # Set status to successful
            # booking_id=str(uuid.uuid4()),  # Example for unique booking_id
        )

        # Generate PDF for booking confirmation
        pdf_content = render_to_pdf('booking_success.html', {
            'booking_id': booking.booking_id,
            'service': 'Home Labour Service',
            'labour': labour.user.username,
            'estimated_arrival': booking.expected_time,
            'skills': labour.skills.all(),
        })

        # Send confirmation email with PDF attachment
        send_booking_email(booking, pdf_content)


        # Log the booking action to the history
        History.objects.create(
            user=request.user,
            action_type='Booking',
            service='Home Labour Service',
            details=f"Booked {labour.user.username} for {booking.expected_time}"
        )

        # Redirect to a success page with the booking ID
        return redirect('booking_success', booking_id=booking.booking_id)

    return render(request, 'book_labour.html', {'labour': labour})


def send_booking_email(booking, pdf_content):
    subject = 'Booking Confirmation'
    message = f'Dear {booking.user.username},\n\nYour booking has been confirmed.\nBooking ID: {booking.booking_id}'

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
    booking = get_object_or_404(Booking, booking_id=booking_id)  # Use booking_id if it's a custom field

    context = {
        'booking_id': booking.booking_id,  # Assuming this is the correct field
        'service': 'Home Labour Service',  # Static value or fetched from another model
        'labour': booking.labour.user.username,  # Assuming `labour` has a `user` with `username`
        'estimated_arrival': booking.expected_time,
        'skills': booking.labour.skills.all(),  # Fetching related skills
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
        labour.avg_rating = labour.reviews.aggregate(Avg('rating'))['rating__avg'] or 'N/A'
    
    return render(request, 'services.html', {'labours': labours, 'query': query}) 

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

def labour_detail(request, labour_id):
    labour = get_object_or_404(Labour, id=labour_id)
    return render(request, 'labour_detail.html', {'labour': labour})