# from django.core.mail import send_mail

# def send_otp_email(email, otp):
#     subject = 'Your OTP Code'
#     message = f'Your OTP code is {otp}.'
#     send_mail(subject, message, 'from@example.com', [email])




from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags




def send_verification_email(email, verification_link, user_name=None):
    """
    Send email verification with modern HTML design
    
    Args:
        email (str): Recipient email address
        verification_link (str): Verification URL
        user_name (str, optional): User's name for personalization
    """
    
    subject = 'Verify Your Mentiff Account'
    
    # HTML email template with modern card design
    html_message = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Verify Your Account</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                line-height: 1.6;
                color: #333;
                background-color: #f8fafc;
                padding: 20px;
            }}
            
            .email-container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: #ffffff;
                border-radius: 16px;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
                overflow: hidden;
            }}
            
            .header {{
                background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
                padding: 40px 30px;
                text-align: center;
                color: white;
            }}
            
            .header h1 {{
                font-size: 28px;
                font-weight: 700;
                margin-bottom: 8px;
            }}
            
            .header p {{
                font-size: 16px;
                opacity: 0.9;
            }}
            
            .content {{
                padding: 40px 30px;
                text-align: center;
            }}
            
            .greeting {{
                font-size: 18px;
                color: #4a5568;
                margin-bottom: 30px;
            }}
            
            .welcome-message {{
                font-size: 16px;
                color: #2d3748;
                margin-bottom: 30px;
                line-height: 1.6;
            }}
            
            .verification-card {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 12px;
                padding: 30px;
                margin: 30px 0;
                box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
            }}
            
            .verification-card h3 {{
                color: white;
                font-size: 18px;
                font-weight: 600;
                margin-bottom: 20px;
            }}
            
            .verify-button {{
                display: inline-block;
                background-color: #ffffff;
                color: #667eea;
                font-size: 16px;
                font-weight: 600;
                padding: 15px 30px;
                text-decoration: none;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                transition: all 0.3s ease;
                margin: 10px 0;
            }}
            
            .verify-button:hover {{
                background-color: #f7fafc;
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
            }}
            
            .alternative-link {{
                margin-top: 20px;
                padding: 20px;
                background-color: #f7fafc;
                border-radius: 8px;
                border-left: 4px solid #4facfe;
            }}
            
            .alternative-link h4 {{
                color: #2d3748;
                font-size: 14px;
                font-weight: 600;
                margin-bottom: 10px;
            }}
            
            .alternative-link p {{
                color: #4a5568;
                font-size: 13px;
                line-height: 1.4;
                word-break: break-all;
            }}
            
            .alternative-link a {{
                color: #4facfe;
                text-decoration: none;
            }}
            
            .info-section {{
                background-color: #e6fffa;
                border: 1px solid #81e6d9;
                border-radius: 8px;
                padding: 20px;
                margin: 30px 0;
                text-align: left;
            }}
            
            .info-section h3 {{
                color: #234e52;
                font-size: 16px;
                font-weight: 600;
                margin-bottom: 15px;
            }}
            
            .info-section ul {{
                color: #285e61;
                font-size: 14px;
                padding-left: 20px;
                line-height: 1.6;
            }}
            
            .info-section li {{
                margin-bottom: 8px;
            }}
            
            .security-notice {{
                background-color: #fef5e7;
                border: 1px solid #f6ad55;
                border-radius: 8px;
                padding: 16px;
                margin: 20px 0;
            }}
            
            .security-notice p {{
                color: #c05621;
                font-size: 13px;
                margin: 0;
            }}
            
            .footer {{
                background-color: #f7fafc;
                padding: 30px;
                text-align: center;
                border-top: 1px solid #e2e8f0;
            }}
            
            .footer p {{
                color: #718096;
                font-size: 13px;
                margin-bottom: 8px;
            }}
            
            .footer a {{
                color: #4facfe;
                text-decoration: none;
                font-weight: 500;
            }}
            
            .footer a:hover {{
                text-decoration: underline;
            }}
            
            .company-logo {{
                font-size: 24px;
                font-weight: 700;
                color: #4facfe;
                margin-bottom: 10px;
            }}
            
            @media (max-width: 600px) {{
                .email-container {{
                    margin: 10px;
                    border-radius: 12px;
                }}
                
                .header, .content, .footer {{
                    padding: 25px 20px;
                }}
                
                .verify-button {{
                    padding: 12px 24px;
                    font-size: 15px;
                }}
                
                .verification-card {{
                    padding: 20px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <h1>Mentiff</h1>
                <p>Account Verification</p>
            </div>
            
            <div class="content">
                <div class="greeting">
                    {"Welcome " + user_name + "!" if user_name else "Welcome!"}
                </div>
                
                <div class="welcome-message">
                    Thank you for joining Mentiff! To complete your account setup and ensure the security of your account, please verify your email address.
                </div>
                
                <div class="verification-card">
                    <h3>Verify Your Email Address</h3>
                    <a href="{verification_link}" class="verify-button">Verify My Account</a>
                </div>
                
                <div class="alternative-link">
                    <h4>Button not working?</h4>
                    <p>Copy and paste this link into your browser:</p>
                    <p><a href="{verification_link}">{verification_link}</a></p>
                </div>
                
                <div class="info-section">
                    <h3>What happens after verification?</h3>
                    <ul>
                        <li>Your account will be fully activated</li>
                        <li>You'll gain access to all Mentiff features</li>
                        <li>You can start connecting with mentees and other mentors</li>
                        <li>Your profile will become visible to other users</li>
                    </ul>
                </div>
                
                <div class="security-notice">
                    <p><strong>Security Note:</strong> This verification link will expire in 24 hours. If you didn't create a Mentiff account, you can safely ignore this email.</p>
                </div>
                
                <p style="color: #718096; font-size: 14px; margin-top: 30px;">
                    Having trouble? Our support team is here to help. Contact us at <a href="mailto:support@mentiff.com" style="color: #4facfe;">support@mentiff.com</a>
                </p>
            </div>
            
            <div class="footer">
                <div class="company-logo">Mentiff</div>
                <p>This email was sent from a notification-only address that cannot accept incoming email.</p>
                <p>Need help? Visit our <a href="https://mentiff.com/support">Support Center</a> or contact us at <a href="mailto:support@mentiff.com">support@mentiff.com</a></p>
                <p style="margin-top: 15px;">
                    <a href="https://mentiff.com">mentiff.com</a> | 
                    <a href="https://mentiff.com/privacy">Privacy Policy</a> | 
                    <a href="https://mentiff.com/terms">Terms of Service</a>
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Plain text version for email clients that don't support HTML
    plain_message = f"""
    Welcome{"" if not user_name else " " + user_name}!
    
    Thank you for joining Mentiff! To complete your account setup, please verify your email address by clicking the link below:
    
    {verification_link}
    
    What happens after verification?
    - Your account will be fully activated
    - You'll gain access to all Mentiff features
    - You can start connecting with mentors and mentees
    - Your profile will become visible to other users
    
    This verification link will expire in 24 hours.
    
    If you didn't create a Mentiff account, you can safely ignore this email.
    
    Need help? Contact us at support@mentiff.com
    
    Best regards,
    The Mentiff Team
    https://mentiff.com
    """
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email='mentiff5@gmail.com',  # Update with your actual from email
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        # Log the error in production
        print(f"Failed to send verification email: {e}")
        return False




def send_otp_email(email, otp, user_name=None):
    """
    Send OTP email with modern HTML design
    
    Args:
        email (str): Recipient email address
        otp (str): OTP code to send
        user_name (str, optional): User's name for personalization
    """
    
    subject = 'Your Mentiff Verification Code'
    
    # HTML email template with modern card design
    html_message = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Your Verification Code</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                line-height: 1.6;
                color: #333;
                background-color: #f8fafc;
                padding: 20px;
            }}
            
            .email-container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: #ffffff;
                border-radius: 16px;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
                overflow: hidden;
            }}
            
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 40px 30px;
                text-align: center;
                color: white;
            }}
            
            .header h1 {{
                font-size: 28px;
                font-weight: 700;
                margin-bottom: 8px;
            }}
            
            .header p {{
                font-size: 16px;
                opacity: 0.9;
            }}
            
            .content {{
                padding: 40px 30px;
                text-align: center;
            }}
            
            .greeting {{
                font-size: 18px;
                color: #4a5568;
                margin-bottom: 30px;
            }}
            
            .otp-card {{
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                border-radius: 12px;
                padding: 30px;
                margin: 30px 0;
                box-shadow: 0 8px 20px rgba(240, 147, 251, 0.3);
            }}
            
            .otp-label {{
                color: white;
                font-size: 14px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 10px;
                opacity: 0.9;
            }}
            
            .otp-code {{
                color: white;
                font-size: 36px;
                font-weight: 700;
                letter-spacing: 8px;
                font-family: 'Courier New', monospace;
                text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
            }}
            
            .instructions {{
                background-color: #f7fafc;
                border-radius: 8px;
                padding: 20px;
                margin: 30px 0;
                border-left: 4px solid #667eea;
            }}
            
            .instructions h3 {{
                color: #2d3748;
                font-size: 16px;
                font-weight: 600;
                margin-bottom: 10px;
            }}
            
            .instructions p {{
                color: #4a5568;
                font-size: 14px;
                line-height: 1.5;
            }}
            
            .security-notice {{
                background-color: #fed7d7;
                border: 1px solid #feb2b2;
                border-radius: 8px;
                padding: 16px;
                margin: 20px 0;
            }}
            
            .security-notice p {{
                color: #c53030;
                font-size: 13px;
                margin: 0;
            }}
            
            .footer {{
                background-color: #f7fafc;
                padding: 30px;
                text-align: center;
                border-top: 1px solid #e2e8f0;
            }}
            
            .footer p {{
                color: #718096;
                font-size: 13px;
                margin-bottom: 8px;
            }}
            
            .footer a {{
                color: #667eea;
                text-decoration: none;
                font-weight: 500;
            }}
            
            .footer a:hover {{
                text-decoration: underline;
            }}
            
            .company-logo {{
                font-size: 24px;
                font-weight: 700;
                color: #667eea;
                margin-bottom: 10px;
            }}
            
            @media (max-width: 600px) {{
                .email-container {{
                    margin: 10px;
                    border-radius: 12px;
                }}
                
                .header, .content, .footer {{
                    padding: 25px 20px;
                }}
                
                .otp-code {{
                    font-size: 28px;
                    letter-spacing: 4px;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <h1>Mentiff</h1>
                <p>Secure Verification</p>
            </div>
            
            <div class="content">
                <div class="greeting">
                    {"Hello " + user_name + "!" if user_name else "Hello!"}
                </div>
                
                <p style="font-size: 16px; color: #4a5568; margin-bottom: 20px;">
                    You've requested a verification code for your Mentiff account. Please use the code below to complete your verification:
                </p>
                
                <div class="otp-card">
                    <div class="otp-label">Your Verification Code</div>
                    <div class="otp-code">{otp}</div>
                </div>
                
                <div class="instructions">
                    <h3>How to use this code:</h3>
                    <p>1. Return to the Mentiff verification page<br>
                    2. Enter the 6-digit code above<br>
                    3. Click "Verify" to complete the process</p>
                </div>
                
                <div class="security-notice">
                    <p><strong>Security Notice:</strong> This code will expire in 10 minutes. Never share this code with anyone. Mentiff will never ask for your verification code via phone or email.</p>
                </div>
                
                <p style="color: #718096; font-size: 14px; margin-top: 30px;">
                    If you didn't request this code, please ignore this email or contact our support team if you have concerns.
                </p>
            </div>
            
            <div class="footer">
                <div class="company-logo">Mentiff</div>
                <p>This email was sent from a notification-only address that cannot accept incoming email.</p>
                <p>Need help? Visit our <a href="https://mentiff.com/support">Support Center</a> or contact us at <a href="mailto:support@mentiff.com">support@mentiff.com</a></p>
                <p style="margin-top: 15px;">
                    <a href="https://mentiff.com">mentiff.com</a> | 
                    <a href="https://mentiff.com/privacy">Privacy Policy</a> | 
                    <a href="https://mentiff.com/terms">Terms of Service</a>
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Plain text version for email clients that don't support HTML
    plain_message = f"""
    Hello{"" if not user_name else " " + user_name}!
    
    Your Mentiff verification code is: {otp}
    
    This code will expire in 10 minutes. Please enter it on the verification page to complete your process.
    
    If you didn't request this code, please ignore this email.
    
    For support, visit mentiff.com/support or email support@mentiff.com
    
    Best regards,
    The Mentiff Team
    https://mentiff.com
    """
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email='mentiff5@gmail.com',  # Update with your actual from email
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        # Log the error in production
        print(f"Failed to send OTP email: {e}")
        return False