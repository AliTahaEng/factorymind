#!/usr/bin/env python3
"""Rotate JWT secret in AWS Secrets Manager."""
import argparse, boto3, secrets, json, sys, logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def rotate(secret_name: str, region: str, dry_run: bool = False) -> str:
    new_secret = secrets.token_urlsafe(64)
    if dry_run:
        logger.info("[DRY RUN] Would update: %s", secret_name)
        return new_secret
    client = boto3.client("secretsmanager", region_name=region)
    try:
        client.put_secret_value(SecretId=secret_name, SecretString=json.dumps({"jwt_secret_key": new_secret}))
        logger.info("Rotated: %s", secret_name)
    except client.exceptions.ResourceNotFoundException:
        client.create_secret(Name=secret_name, SecretString=json.dumps({"jwt_secret_key": new_secret}))
        logger.info("Created: %s", secret_name)
    return new_secret

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--secret-name", default="factorymind/jwt-secret")
    p.add_argument("--region", default="us-east-1")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    try:
        rotate(args.secret_name, args.region, args.dry_run)
        sys.exit(0)
    except Exception as exc:
        logger.error("Failed: %s", exc); sys.exit(1)
