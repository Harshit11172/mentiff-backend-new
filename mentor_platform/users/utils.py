from django.core.mail import send_mail

def send_otp_email(email, otp):
    subject = 'Your OTP Code'
    message = f'Your OTP code is {otp}.'
    send_mail(subject, message, 'from@example.com', [email])
