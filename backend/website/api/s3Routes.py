import datetime
import logging
import os

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

s3Routes = Blueprint("s3Routes", __name__)


def create_presigned_url(bucket_name, object_name, region_name, expiration=3600):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param region_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Generate a presigned URL for the S3 object
    s3_client = boto3.client(
        "s3",
        region_name=region_name,
        config=Config(signature_version="s3v4"),
    )
    try:
        response = s3_client.generate_presigned_url(
            "put_object",
            Params={"Bucket": bucket_name, "Key": object_name},
            ExpiresIn=expiration,
        )
    except ClientError as e:
        logging.error(e)
        return None

    # The response contains the presigned URL
    return response


@s3Routes.route("/upload", methods=["POST"])
@jwt_required()
def s3_api():
    s3_bucket = os.getenv("S3_BUCKET")
    s3_region = os.getenv("S3_REGION")
    data = request.get_json()
    if not data:
        return jsonify({"error": "empty field"}), 400
    if "filename" not in data:
        return jsonify({"error": "docuemnt has no name"}), 400
    filename = data["filename"]
    user_id = get_jwt_identity()
    fileId = str(user_id) + "_" + datetime.datetime.now().isoformat() + "_" + filename
    url = create_presigned_url(s3_bucket, fileId, s3_region)
    if url is None:
        return jsonify({"error": "Failed to create s3 url"}), 400
    return jsonify({"s3_url": url}), 200
