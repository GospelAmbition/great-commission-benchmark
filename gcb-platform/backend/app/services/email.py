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
            <p><a href="https://greatcommissionbenchmark.ai/dashboard/tests/{test_id}" style="background-color: #a11824; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Results</a></p>
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
            <p><a href="https://greatcommissionbenchmark.ai/dashboard/tests/{test_id}" style="background-color: #a11824; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Test Details</a></p>
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
            <p><a href="https://greatcommissionbenchmark.ai/tests/{test_id}/payment" style="background-color: #a11824; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Retry Payment</a></p>
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
            <p><a href="https://greatcommissionbenchmark.ai/leaderboard" style="background-color: #a11824; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Leaderboard</a></p>
            <hr>
            <p style="color: #666; font-size: 12px;">Great Commission Benchmark</p>
        </body>
        </html>
        """
        return await EmailService.send_email(user_email, subject, html)
    
    @staticmethod
    async def send_submission_payment_confirmed_email(
        user_email: str,
        submission_id: str,
        model_name: str
    ) -> bool:
        """Send submission payment confirmation notification"""
        subject = f"Payment confirmed for {model_name} submission"
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #a11824;">Payment Confirmed</h1>
            <p>Your payment for the submission of <strong>{model_name}</strong> has been confirmed.</p>
            <p>Your submission is now queued for moderator review. You'll receive an email once the review is complete.</p>
            <p><a href="https://greatcommissionbenchmark.ai/dashboard" style="background-color: #a11824; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Dashboard</a></p>
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
            <p><a href="https://greatcommissionbenchmark.ai/dashboard/submissions/{submission_id}" style="background-color: #a11824; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Submission</a></p>
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
            <p><a href="https://greatcommissionbenchmark.ai/tests/new" style="background-color: #a11824; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Run Your First Test</a></p>
            <hr>
            <p style="color: #666; font-size: 12px;">Great Commission Benchmark</p>
        </body>
        </html>
        """
        return await EmailService.send_email(user_email, subject, html)
    
    @staticmethod
    async def send_sponsorship_assigned_email(
        moderator_email: str,
        moderator_name: str,
        model_name: str,
        sponsorship_id: str,
        request_type: str
    ) -> bool:
        """Send email notification when a sponsorship request is assigned to a moderator"""
        request_type_label = "Sponsorship Request" if request_type == "sponsorship" else "Model Request"
        subject = f"New {request_type_label} Assigned: {model_name}"
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #a11824;">New {request_type_label} Assigned</h1>
            <p>Hello {moderator_name},</p>
            <p>A new {request_type_label.lower()} for <strong>{model_name}</strong> has been assigned to you for review.</p>
            <p>Please review the request and run the model test when ready.</p>
            <p><a href="https://greatcommissionbenchmark.ai/moderator/sponsorship/{sponsorship_id}" style="background-color: #a11824; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Review Request</a></p>
            <hr>
            <p style="color: #666; font-size: 12px;">Great Commission Benchmark</p>
        </body>
        </html>
        """
        return await EmailService.send_email(moderator_email, subject, html)
    
    @staticmethod
    async def send_test_email(
        to_email: str,
        user_name: Optional[str] = None
    ) -> bool:
        """Send a test email to verify email service is working"""
        from datetime import datetime
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        name = user_name or "there"
        subject = "Great Commission Benchmark - Email Service Test"
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #a11824;">Email Service Test</h1>
            <p>Hello {name},</p>
            <p>This is a test email from the Great Commission Benchmark platform to verify that the email service is working correctly.</p>
            <p><strong>Test Timestamp:</strong> {timestamp}</p>
            <p>If you received this email, the email service is configured and functioning properly.</p>
            <hr>
            <p style="color: #666; font-size: 12px;">Great Commission Benchmark</p>
        </body>
        </html>
        """
        return await EmailService.send_email(to_email, subject, html)
    
    @staticmethod
    async def send_contact_notification_email(
        admin_email: str,
        contact_name: str,
        contact_email: str,
        subject: str,
        message: str,
        submission_id: str
    ) -> bool:
        """Send notification email when someone submits the contact form"""
        email_subject = f"New Contact Form Submission: {subject.title()}"
        # Truncate message for preview
        message_preview = message[:500] + "..." if len(message) > 500 else message
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #a11824;">New Contact Form Submission</h1>
            <p>Someone has submitted the contact form on the Great Commission Benchmark website.</p>
            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #eee; font-weight: bold;">Name:</td>
                    <td style="padding: 10px; border-bottom: 1px solid #eee;">{contact_name}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #eee; font-weight: bold;">Email:</td>
                    <td style="padding: 10px; border-bottom: 1px solid #eee;"><a href="mailto:{contact_email}">{contact_email}</a></td>
                </tr>
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #eee; font-weight: bold;">Subject:</td>
                    <td style="padding: 10px; border-bottom: 1px solid #eee;">{subject.title()}</td>
                </tr>
            </table>
            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <strong>Message:</strong>
                <p style="white-space: pre-wrap;">{message_preview}</p>
            </div>
            <p><a href="https://greatcommissionbenchmark.ai/admin/contacts" style="background-color: #a11824; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View in Admin</a></p>
            <hr>
            <p style="color: #666; font-size: 12px;">Great Commission Benchmark</p>
        </body>
        </html>
        """
        return await EmailService.send_email(admin_email, email_subject, html)
    
    @staticmethod
    async def send_volunteer_notification_email(
        admin_email: str,
        applicant_name: str,
        applicant_email: str,
        role: str,
        background: Optional[str] = None,
        motivation: Optional[str] = None
    ) -> bool:
        """Send notification email when someone applies to volunteer"""
        subject = f"New Volunteer Application: {role.title()}"
        background_preview = (background[:300] + "..." if background and len(background) > 300 else background) or "Not provided"
        motivation_preview = (motivation[:300] + "..." if motivation and len(motivation) > 300 else motivation) or "Not provided"
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #a11824;">New Volunteer Application</h1>
            <p>Someone has applied to volunteer for the Great Commission Benchmark.</p>
            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #eee; font-weight: bold;">Name:</td>
                    <td style="padding: 10px; border-bottom: 1px solid #eee;">{applicant_name}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #eee; font-weight: bold;">Email:</td>
                    <td style="padding: 10px; border-bottom: 1px solid #eee;"><a href="mailto:{applicant_email}">{applicant_email}</a></td>
                </tr>
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #eee; font-weight: bold;">Role:</td>
                    <td style="padding: 10px; border-bottom: 1px solid #eee;">{role.title()}</td>
                </tr>
            </table>
            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <strong>Background & Experience:</strong>
                <p style="white-space: pre-wrap;">{background_preview}</p>
            </div>
            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <strong>Motivation:</strong>
                <p style="white-space: pre-wrap;">{motivation_preview}</p>
            </div>
            <p><a href="https://greatcommissionbenchmark.ai/admin/volunteers" style="background-color: #a11824; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Review Application</a></p>
            <hr>
            <p style="color: #666; font-size: 12px;">Great Commission Benchmark</p>
        </body>
        </html>
        """
        return await EmailService.send_email(admin_email, subject, html)
    
    @staticmethod
    async def send_sponsorship_request_notification_email(
        admin_email: str,
        requester_name: str,
        requester_email: str,
        model_name: str,
        request_type: str,
        message: Optional[str] = None,
        sponsorship_id: str = ""
    ) -> bool:
        """Send notification email when someone submits a sponsorship or model request"""
        request_type_label = "Sponsorship Request" if request_type == "sponsorship" else "Model Request"
        subject = f"New {request_type_label}: {model_name}"
        message_section = ""
        if message:
            message_preview = message[:500] + "..." if len(message) > 500 else message
            message_section = f"""
            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <strong>Message from Requester:</strong>
                <p style="white-space: pre-wrap;">{message_preview}</p>
            </div>
            """
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #a11824;">New {request_type_label}</h1>
            <p>A new {request_type_label.lower()} has been submitted for review.</p>
            <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #eee; font-weight: bold;">Requested By:</td>
                    <td style="padding: 10px; border-bottom: 1px solid #eee;">{requester_name}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #eee; font-weight: bold;">Email:</td>
                    <td style="padding: 10px; border-bottom: 1px solid #eee;"><a href="mailto:{requester_email}">{requester_email}</a></td>
                </tr>
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #eee; font-weight: bold;">Model:</td>
                    <td style="padding: 10px; border-bottom: 1px solid #eee;">{model_name}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #eee; font-weight: bold;">Type:</td>
                    <td style="padding: 10px; border-bottom: 1px solid #eee;">{request_type_label}</td>
                </tr>
            </table>
            {message_section}
            <p><a href="https://greatcommissionbenchmark.ai/admin/sponsorships" style="background-color: #a11824; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Review Request</a></p>
            <hr>
            <p style="color: #666; font-size: 12px;">Great Commission Benchmark</p>
        </body>
        </html>
        """
        return await EmailService.send_email(admin_email, subject, html)