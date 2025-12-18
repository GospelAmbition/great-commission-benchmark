"""Email notification service"""
import resend
from typing import Optional
from app.core.config import settings

# Initialize Resend
if settings.RESEND_API_KEY:
    resend.api_key = settings.RESEND_API_KEY


class EmailService:
    """Service for sending email notifications"""
    
    @staticmethod
    async def send_email(
        to: str,
        subject: str,
        html_content: str,
        from_email: Optional[str] = None
    ) -> bool:
        """
        Send an email via Resend
        
        Args:
            to: Recipient email address
            subject: Email subject
            html_content: HTML email content
            from_email: From email address (defaults to settings)
        
        Returns:
            True if sent successfully, False otherwise
        """
        if not settings.RESEND_API_KEY:
            # Email service not configured - log but don't fail
            print(f"Email not sent (service not configured): {to} - {subject}")
            return False
        
        try:
            resend.Emails.send({
                "from": from_email or settings.EMAIL_FROM,
                "to": [to],
                "subject": subject,
                "html": html_content
            })
            return True
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False
    
    @staticmethod
    async def send_test_completed_email(
        user_email: str,
        test_id: str,
        model_name: str,
        overall_score: float
    ) -> bool:
        """Send test completion notification"""
        subject = f"Your benchmark test for {model_name} is complete!"
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #a11824;">Test Complete!</h1>
            <p>Your benchmark test for <strong>{model_name}</strong> has been completed.</p>
            <p><strong>Overall Score:</strong> {overall_score:.1f}%</p>
            <p><a href="https://gcb.app/dashboard/tests/{test_id}" style="background-color: #a11824; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Results</a></p>
            <hr>
            <p style="color: #666; font-size: 12px;">Great Commission Benchmark</p>
        </body>
        </html>
        """
        return await EmailService.send_email(user_email, subject, html)
    
    @staticmethod
    async def send_test_failed_email(
        user_email: str,
        test_id: str,
        error_message: str
    ) -> bool:
        """Send test failure notification"""
        subject = "Your benchmark test encountered an error"
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #a11824;">Test Failed</h1>
            <p>Unfortunately, your benchmark test encountered an error:</p>
            <p style="background-color: #fee9e8; padding: 10px; border-radius: 5px;">{error_message}</p>
            <p>Please contact support if this issue persists.</p>
            <p><a href="https://gcb.app/dashboard/tests/{test_id}" style="background-color: #a11824; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Test Details</a></p>
            <hr>
            <p style="color: #666; font-size: 12px;">Great Commission Benchmark</p>
        </body>
        </html>
        """
        return await EmailService.send_email(user_email, subject, html)
    
    @staticmethod
    async def send_payment_failed_email(
        user_email: str,
        test_id: str
    ) -> bool:
        """Send payment failure notification"""
        subject = "Payment failed for your benchmark test"
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #a11824;">Payment Failed</h1>
            <p>Your payment for the benchmark test could not be processed.</p>
            <p>Please check your payment method and try again.</p>
            <p><a href="https://gcb.app/tests/{test_id}/payment" style="background-color: #a11824; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Retry Payment</a></p>
            <hr>
            <p style="color: #666; font-size: 12px;">Great Commission Benchmark</p>
        </body>
        </html>
        """
        return await EmailService.send_email(user_email, subject, html)
    
    @staticmethod
    async def send_submission_approved_email(
        user_email: str,
        submission_id: str,
        model_name: str
    ) -> bool:
        """Send submission approval notification"""
        subject = f"Your submission for {model_name} has been approved!"
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #a11824;">Submission Approved</h1>
            <p>Great news! Your community submission for <strong>{model_name}</strong> has been reviewed and approved.</p>
            <p>It will now appear on the public leaderboard.</p>
            <p><a href="https://gcb.app/research" style="background-color: #a11824; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Leaderboard</a></p>
            <hr>
            <p style="color: #666; font-size: 12px;">Great Commission Benchmark</p>
        </body>
        </html>
        """
        return await EmailService.send_email(user_email, subject, html)
    
    @staticmethod
    async def send_submission_rejected_email(
        user_email: str,
        submission_id: str,
        model_name: str,
        reviewer_notes: Optional[str] = None
    ) -> bool:
        """Send submission rejection notification"""
        subject = f"Submission for {model_name} needs revision"
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #a11824;">Submission Review</h1>
            <p>Your community submission for <strong>{model_name}</strong> was reviewed but needs revision.</p>
            {f'<p style="background-color: #fee9e8; padding: 10px; border-radius: 5px;">{reviewer_notes}</p>' if reviewer_notes else ''}
            <p>Please review the feedback and resubmit if needed.</p>
            <p><a href="https://gcb.app/dashboard/submissions/{submission_id}" style="background-color: #a11824; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Submission</a></p>
            <hr>
            <p style="color: #666; font-size: 12px;">Great Commission Benchmark</p>
        </body>
        </html>
        """
        return await EmailService.send_email(user_email, subject, html)
    
    @staticmethod
    async def send_welcome_email(user_email: str, user_name: Optional[str] = None) -> bool:
        """Send welcome email to new users"""
        subject = "Welcome to Great Commission Benchmark!"
        name = user_name or "there"
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #a11824;">Welcome, {name}!</h1>
            <p>Thank you for joining the Great Commission Benchmark platform.</p>
            <p>You can now:</p>
            <ul>
                <li>Run benchmark tests on AI models</li>
                <li>View detailed results and comparisons</li>
                <li>Submit community results</li>
                <li>Contribute to the benchmark</li>
            </ul>
            <p><a href="https://gcb.app/tests/new" style="background-color: #a11824; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Run Your First Test</a></p>
            <hr>
            <p style="color: #666; font-size: 12px;">Great Commission Benchmark</p>
        </body>
        </html>
        """
        return await EmailService.send_email(user_email, subject, html)
