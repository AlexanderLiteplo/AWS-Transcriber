# Test script to list files in your S3 bucket
import boto3

s3 = boto3.client('s3', region_name='us-east-1')
bucket_name = 'sagemaker-studio-9457123102-m10offqm0g'

try:
    contents = s3.list_objects(Bucket=bucket_name)['Contents']
    for file in contents:
        print(file['Key'])
except Exception as e:
    print(e)
