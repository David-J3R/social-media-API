import logging
from json import JSONDecodeError

import httpx
from databases import Database

from socialapi.config import config
from socialapi.database import post_table

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


# ----- Interacting with DeepAI API for image generation -----
# The "_" prefix indicates that this function is for background/internal use
async def _generate_cute_creature_api(prompt: str):
    logger.debug("Generating cute creature image with DeepAI API")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://api.deepai.org/api/cute-creature-generator",
                data={"text": prompt},
                headers={"api-key": config.DEEPAI_API_KEY},
                timeout=60,  # Set timeout to 60 seconds
            )
            logger.debug(f"DeepAI API response status: {response.status_code}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as err:
            raise APIResponseError(
                f"DeepAI API returned an error: {err.response.status_code}"
            ) from err
        except (JSONDecodeError, TypeError) as err:
            raise APIResponseError("Error parsing DeepAI API response") from err


# Background task to generate image
async def generate_and_add_to_post(
    email: str,
    post_id: int,
    post_url: str,
    database: Database,
    prompt: str = "A blue cartoonish mexican cat is sitting on a colorful piñata",
):
    # Generate image using DeepAI API
    try:
        response = await _generate_cute_creature_api(prompt)
    except APIResponseError:
        return await send_simple_email(
            email,
            "Error generating image",
            (
                f"Hi {email}! Unfortunately, there was an error generating the image"
                " for your post :()"
            ),
        )

    logger.debug("Connecting to database to update post")

    # Update the post with the generated image URL
    query = (
        post_table.update()
        .where(post_table.c.id == post_id)
        .values(image_url=response["output_url"])
    )

    logger.debug(f"Executing query: {query}")
    await database.execute(query)

    logger.debug("Database connection closed after updating post")

    # Send email to user with the post URL
    await send_simple_email(
        email,
        "Image generation completed",
        (
            f"Hi {email}! The image for your post has been generated. "
            f"Please click on the following link to view it: {post_url}"
        ),
    )
    return response
