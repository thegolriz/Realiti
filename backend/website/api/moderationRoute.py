import os
import re

import boto3
from better_profanity import profanity
from botocore.config import Config
import anthropic


def moderation_check(s3_object):
    if not s3_object:
        return True
    s3_bucket = os.getenv("S3_BUCKET")
    s3_region = os.getenv("S3_REGION")
    s3_client = boto3.client(
        "s3",
        region_name=s3_region,
        config=Config(signature_version="s3v4"),
    )

    session = boto3.Session()
    client = session.client("rekognition", region_name=s3_region)
    response = client.detect_moderation_labels(
        Image={"S3Object": {"Bucket": s3_bucket, "Name": s3_object}}
    )
    print("Detected labels for " + s3_object)
    for label in response["ModerationLabels"]:
        print(label["Name"] + " : " + str(label["Confidence"]))
        if label["Confidence"] > 70:
            s3_client.delete_object(Bucket=s3_bucket, Key=s3_object)
            return False
        # elif label['Confidence'] > 40 and label['Confidence'] < 70:
        #     return human_review
        print(label["ParentName"])

    return True


LEET_MAP = {
    "@": "a",
    "4": "a",
    "3": "e",
    "1": "i",
    "!": "i",
    "|": "i",
    "0": "o",
    "5": "s",
    "$": "s",
    "7": "t",
    "+": "t",
    "8": "b",
    "6": "g",
    "9": "g",
    "2": "z",
}


def normalize(text):
    leet_trans = str.maketrans(LEET_MAP)
    if text:
        text = text.translate(leet_trans)
    return text


REASON_INAPPROPRIATE = "inappropriate"
REASON_GUIDELINES = "guidelines"


def _classify(text):
    if not text:
        return None
    normalized = normalize(text)
    if re.search(r"([a-zA-Z]\s){3,}", normalized):
        return REASON_GUIDELINES
    if profanity.contains_profanity(text) or profanity.contains_profanity(normalized):
        # Leetspeak (text relies on substituted characters) is an evasion
        # attempt rather than plainly inappropriate content.
        if text != normalized:
            return REASON_GUIDELINES
        return REASON_INAPPROPRIATE
    return None


def regex_check(title, description):
    reasons = (_classify(title), _classify(description))
    if REASON_INAPPROPRIATE in reasons:
        return REASON_INAPPROPRIATE
    if REASON_GUIDELINES in reasons:
        return REASON_GUIDELINES
    if title:
        claude_text_check(title)
    return None


def claude_text_check(text):
    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1000,
        messages=[
            {
                "role": "user",
                "content": "I'm sending you test data, do you see the text: "+text,
            }
        ],
    )
    print(message.content)
