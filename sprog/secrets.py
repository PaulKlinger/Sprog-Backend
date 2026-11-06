import json

import boto3


SECRET_NAME = "sprog"
REGION = "eu-west-1"


def load_passwords():
    """Load the backend's secrets from AWS Secrets Manager.

    The secret holds one JSON object with the keys sprog_auth.py used to
    hold (NAMECHEAP_*, PRAW_*, plus GITHUB_TOKEN and R2_* once the R2 upload
    is enabled). The instance reads it with its IAM role, so no secret ever
    lives on disk.
    """
    client = boto3.client("secretsmanager", region_name=REGION)
    response = client.get_secret_value(SecretId=SECRET_NAME)
    return json.loads(response["SecretString"])
