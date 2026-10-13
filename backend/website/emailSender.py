import os

import boto3
from botocore.exceptions import BotoCoreError, ClientError


def send_verification_email(to, link):
    client = boto3.client("sesv2", region_name=os.getenv("S3_REGION"))
    CHARSET = "UTF-8"
    try:
        client.send_email(
            Destination={
                "ToAddresses": [to],
            },
            # Replies go to the support inbox instead of the noreply sender.
            ReplyToAddresses=["support@realiti.dev"],
            Content={
                "Simple": {
                    "Body": {
                        "Text": {
                            "Charset": CHARSET,
                            "Data": (
                                "Hi,\n\n"
                                "We received a request to verify your Realiti account "
                                "as a real estate agent. To confirm your email and "
                                "submit your application for review, open this "
                                "link:\n\n"
                                f"{link}\n\n"
                                "This link expires in 24 hours.\n\n"
                                "After you confirm, we check your license against your "
                                "state's licensing records. This usually takes 1 to 3 "
                                "days, sometimes longer. Once approved, your posts and "
                                'profile will show a "Real estate agent" label.\n\n'
                                "Didn't request this? Don't open the link. Change your "
                                "password and contact support@realiti.dev, since "
                                "someone else may have access to your account.\n\n"
                                "The Realiti team"
                            ),
                        }
                    },
                    "Subject": {
                        "Charset": CHARSET,
                        "Data": "Confirm your real estate agent verification",
                    },
                },
            },
            FromEmailAddress=os.getenv("SES_SENDER"),
        )
    except (ClientError, BotoCoreError) as e:
        print(f"SES failed to send verification email to {to}: {e}")
        return False
    return True
