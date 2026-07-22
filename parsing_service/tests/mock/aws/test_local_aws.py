import boto3
import pytest
import os
import time

# The key is to provide the endpoint_url pointing to LocalStack (default: 4566)
ENDPOINT_URL = "http://localhost:4566"
AWS_ACCESS_KEY_ID = "testing"
AWS_SECRET_ACCESS_KEY = "testing"
AWS_DEFAULT_REGION = "us-east-1"

def test_localstack_read(localstack_service):
    # S3 example
    s3 = boto3.client(
        "s3",
        endpoint_url=ENDPOINT_URL,
        region_name=AWS_DEFAULT_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
    
    # Wait for bucket to be created by init script
    max_retries = 10
    for i in range(max_retries):
        buckets = s3.list_buckets()
        bucket_names = [b['Name'] for b in buckets['Buckets']]
        if "test-bucket" in bucket_names:
            break
        time.sleep(1)
    
    assert "test-bucket" in bucket_names, "test-bucket was not created by init script"
    print("S3 Buckets:", bucket_names)
    
    # EC2 example
    ec2 = boto3.client(
        "ec2",
        endpoint_url=ENDPOINT_URL,
        region_name=AWS_DEFAULT_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
    # Wait for instance
    for i in range(max_retries):
        instances = ec2.describe_instances()
        if len(instances['Reservations']) > 0:
            break
        time.sleep(1)
    assert len(instances['Reservations']) > 0
    print("EC2 Instances:", instances['Reservations'])

    # DynamoDB example
    ddb = boto3.client(
        "dynamodb",
        endpoint_url=ENDPOINT_URL,
        region_name=AWS_DEFAULT_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
    )
    # Wait for table
    for i in range(max_retries):
        tables = ddb.list_tables()
        if "TestTable" in tables['TableNames']:
            break
        time.sleep(1)
    assert "TestTable" in tables['TableNames']
    print("DynamoDB Tables:", tables['TableNames'])

if __name__ == "__main__":
    try:
        test_localstack_read()
    except Exception as e:
        print(f"Error connecting to LocalStack: {e}")
        print("Make sure LocalStack is running (docker-compose up -d)")
