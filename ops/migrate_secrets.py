#!/usr/bin/env python3
"""One-off migration: copy the backend's secrets from the files on this host
(sprog_auth.py, praw.ini) into AWS Secrets Manager, so the files can then be
deleted.

Run on the host (it uses the instance's IAM role — no credentials needed):
    python3 ops/migrate_secrets.py

Prints only the secret ARN and the key names it stored — never any value.
The static AWS keys and the FCM key are deliberately NOT copied: the S3
upload now uses the IAM role, and the FCM step has been removed.
"""
import configparser
import importlib.util
import json

import boto3

SECRET_NAME = "sprog"
REGION = "eu-west-1"

SPROG_DIR = "/home/ec2-user/sprog"


def main():
    spec = importlib.util.spec_from_file_location(
        "sprog_auth", SPROG_DIR + "/sprog_auth.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    passwords = module.passwords

    praw_ini = configparser.ConfigParser()
    praw_ini.read(SPROG_DIR + "/praw.ini")

    secret = {
        "NAMECHEAP_SERVER": passwords["NAMECHEAP_SERVER"],
        "NAMECHEAP_USERNAME": passwords["NAMECHEAP_USERNAME"],
        "NAMECHEAP_PASSWORD": passwords["NAMECHEAP_PASSWORD"],
        "NAMECHEAP_PORT": passwords["NAMECHEAP_PORT"],
        "PRAW_CLIENT_ID": praw_ini["DEFAULT"]["client_id"],
        "PRAW_CLIENT_SECRET": praw_ini["DEFAULT"]["client_secret"],
        "PRAW_USER_AGENT": praw_ini["DEFAULT"]["user_agent"],
    }

    client = boto3.client("secretsmanager", region_name=REGION)
    try:
        response = client.create_secret(
            Name=SECRET_NAME, SecretString=json.dumps(secret))
    except client.exceptions.ResourceExistsException:
        print("Secret", SECRET_NAME, "already exists — not overwriting.")
        return
    print("Created secret:", response["ARN"])
    print("Stored keys:", ", ".join(sorted(secret)))


if __name__ == "__main__":
    main()
