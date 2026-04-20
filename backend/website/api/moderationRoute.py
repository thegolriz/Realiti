import os

import boto3
from botocore.config import Config


def moderation_check(s3_object):
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
