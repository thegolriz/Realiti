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


def regex_check(title, description):
    description = normalize(description)
    if title:
        title = normalize(title)
        if profanity.contains_profanity(title) or profanity.contains_profanity(
            description
        ):
            return False
        if re.search(r"([a-zA-Z]\s){3,}", title):
            return False
        if re.search(r"([a-zA-Z]\s){3,}", description):
            return False
        # at this point we send data to claude
        claude_text_check(title)
        return True
    else:
        if profanity.contains_profanity(description):
            return False
        if re.search(r"([a-zA-Z]\s){3,}", description):
            return False
        return True


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
