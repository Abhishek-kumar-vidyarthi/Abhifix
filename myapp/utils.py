# your_app/utils.py

from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO
from django.core.mail import send_mail
import random

def render_to_pdf(template_src, context_dict):
    # Render the template with the context
    html = render_to_string(template_src, context_dict)
    
    # Create a BytesIO buffer to hold the PDF data
    result = BytesIO()
    
    # Convert HTML to PDF
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    
    # Check for errors during PDF generation
    if pdf.err:
        return None  # or raise an exception
    
    return result.getvalue()  # Return the PDF as a byte string

def generate_otp():
    return random.randint(100000, 999999) 


def send_otp(email, otp):
    subject = 'Your OTP for Login Verification'
    message = f"Your OTP code is: {otp}. It is valid for 10 minutes."

    email_from = 'settings.DEFAULT_FROM_EMAIL'
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)