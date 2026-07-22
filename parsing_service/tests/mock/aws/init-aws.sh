#!/bin/bash
# Initialize S3
awslocal s3 mb s3://test-bucket
awslocal s3 cp /etc/hosts s3://test-bucket/sample-file.txt

# Initialize DynamoDB
awslocal dynamodb create-table \
    --table-name TestTable \
    --key-schema AttributeName=id,KeyType=HASH \
    --attribute-definitions AttributeName=id,AttributeType=S \
    --billing-mode PAY_PER_REQUEST

# Initialize EC2 (Mock instance)
awslocal ec2 run-instances --image-id ami-12345678 --count 1 --instance-type t2.micro

echo "LocalStack initialized with sample services!"
