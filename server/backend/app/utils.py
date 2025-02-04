import boto3
import json
import base64
import os
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import uuid

logger = logging.getLogger('app')
bucket_name = "clustroai-s3-dev"
path = "generated-data/"


def create_presigned_fields(invocation_id, expiration=3600):
    object_name = path + invocation_id + '.png'
    s3_client = boto3.client('s3')
    fields = s3_client.generate_presigned_post(Bucket=bucket_name,
                                               Key=object_name,
                                               ExpiresIn=expiration)
    fields["Content-Type"] = "image/png"
    return base64.b64encode(json.dumps(fields).encode('utf-8')).decode()


def is_valid_uuid(s):
    try:
        uuid.UUID(s)
        return True
    except ValueError:
        return False


# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python

def send_verification_email(verification_link, email):
    message = Mail(
        from_email='admin@clustro.ai',
        to_emails=email,
        subject='ClustroAI verification',
        html_content='<strong>Click <a href="' + verification_link + '">here</a> to verify your email.</strong>')
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        return response
    except Exception as e:
        logger.error(str(e))
