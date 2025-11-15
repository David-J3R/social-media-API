import logging

import httpx

from socialapi.config import config

logger = logging.getLogger(__name__)


# Create APIResponse error
class APIResponseError(Exception):
    # inherit from Exception
    pass


async def send_simple_email(to: str, subject: str, body: str):
    # Log the email details for debugging purposes
    # The [:3] and [:20] slices are to avoid logging sensitive or overly long information
    logger.debug(f"Sending email to '{to[:3]}' with subject '{subject[:20]}'")

    async with httpx.AsyncClient() as client:
        try:
            # Send the email using Mailgun API
            response = await client.post(
                f"https://api.mailgun.net/v3/{config.MAILGUN_DOMAIN}/messages",
                auth=("api", config.MAILGUN_API_KEY),
                data={
                    "from": f"SocialAPI <mailgun@{config.MAILGUN_DOMAIN}>",
                    "to": [to],
                    "subject": subject,
                    "text": body,
                },
            )
            # Raise an exception for HTTP errors
            response.raise_for_status()

            logger.debug(response.content)

            return response

        except httpx.HTTPStatusError as err:
            raise APIResponseError(
                f"Mailgun API returned an error: {err.response.status_code} - {err.response.text}"
            ) from err


# Send confirmation email
async def send_user_registration_email(email: str, confirmation_url: str):
    """ "Send user registration confirmation email"""
    return await send_simple_email(
        email,
        "Successfully signed up",
        (
            f"Hi {email}! You have successfully signed up to SocialAPI.\n"
            "Please confirm your email by clicking the link below:\n"
            f"{confirmation_url}\n\n"
            "If you did not sign up for this account, please ignore this email."
        ),
    )
