#!/bin/bash
echo "Creating S3 buckets in LocalStack..."
awslocal s3 mb s3://factorymind-raw-dev
awslocal s3 mb s3://factorymind-datasets-dev
awslocal s3 mb s3://factorymind-models-dev
awslocal s3 mb s3://factorymind-exports-dev
echo "Buckets created."
