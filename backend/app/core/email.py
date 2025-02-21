

from typing import List, Optional
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import jinja2
import logging
from pathlib import Path
from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize Jinja2 environment for email templates
templates_path = Path(__file__).parent.parent / "templates" / "email"
template_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(str(templates_path)),
    autoescape=True
)

class EmailClient:
    def __init__(self):
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.username = settings.SMTP_USERNAME
        self.password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL
        self.use_tls = settings.SMTP_USE_TLS

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> bool:
        """Send email"""
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = self.from_email
            message["To"] = to_email

            if cc:
                message["Cc"] = ", ".join(cc)
            if bcc:
                message["Bcc"] = ", ".join(bcc)

            # Add content
            if text_content:
                message.attach(MIMEText(text_content, "plain"))
            message.attach(MIMEText(html_content, "html"))

            # Send email
            await aiosmtplib.send(
                message,
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                use_tls=self.use_tls
            )

            return True

        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return False

class EmailService:
    def __init__(self):
        self.client = EmailClient()

    async def send_welcome_email(self, email: str, full_name: str) -> bool:
        """Send welcome email"""
        try:
            template = template_env.get_template("welcome.html")
            html_content = template.render(
                name=full_name,
                login_url=f"{settings.FRONTEND_URL}/login",
                help_url=f"{settings.FRONTEND_URL}/help"
            )

            text_template = template_env.get_template("welcome.txt")
            text_content = text_template.render(
                name=full_name,
                login_url=f"{settings.FRONTEND_URL}/login",
                help_url=f"{settings.FRONTEND_URL}/help"
            )

            return await self.client.send_email(
                to_email=email,
                subject="Welcome to OPiN!",
                html_content=html_content,
                text_content=text_content
            )

        except Exception as e:
            logger.error(f"Error sending welcome email: {str(e)}")
            return False

    async def send_password_reset(self, email: str, reset_token: str) -> bool:
        """Send password reset email"""
        try:
            reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
            
            template = template_env.get_template("password_reset.html")
            html_content = template.render(reset_url=reset_url)

            text_template = template_env.get_template("password_reset.txt")
            text_content = text_template.render(reset_url=reset_url)

            return await self.client.send_email(
                to_email=email,
                subject="Reset Your Password",
                html_content=html_content,
                text_content=text_content
            )

        except Exception as e:
            logger.error(f"Error sending password reset email: {str(e)}")
            return False

    async def send_verification_email(self, email: str, verify_token: str) -> bool:
        """Send email verification"""
        try:
            verify_url = f"{settings.FRONTEND_URL}/verify-email?token={verify_token}"
            
            template = template_env.get_template("verify_email.html")
            html_content = template.render(verify_url=verify_url)

            text_template = template_env.get_template("verify_email.txt")
            text_content = text_template.render(verify_url=verify_url)

            return await self.client.send_email(
                to_email=email,
                subject="Verify Your Email",
                html_content=html_content,
                text_content=text_content
            )

        except Exception as e:
            logger.error(f"Error sending verification email: {str(e)}")
            return False

email_service = EmailService()


