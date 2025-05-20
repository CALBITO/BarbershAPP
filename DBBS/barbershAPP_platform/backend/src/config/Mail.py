"""Mail configuration module"""
from flask_mail import Mail

# Initialize mail instance
mail = Mail()

# Mail configuration class
class MailConfig:
    """Mail configuration settings"""
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    MAIL_DEFAULT_SENDER = None
    MAIL_MAX_EMAILS = None
    MAIL_ASCII_ATTACHMENTS = False