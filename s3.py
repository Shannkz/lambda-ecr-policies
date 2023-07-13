import boto3
import json
import ex

client = boto3.client('s3')


def create_bucket(bucket_name: str) -> None:
    try:
        create_bucket_response = client.create_bucket(
            ACL='private',
            Bucket=bucket_name,
            CreateBucketConfiguration={
                'LocationConstraint': 'eu-central-1'
            }
        )
        print(f'Bucket "{bucket_name}" has been created.')
    except client.exceptions.BucketAlreadyExists:
        print('Bucket already exists, skipping creation.')
    except client.exceptions.BucketAlreadyOwnedByYou:
        print('Bucket already exists, skipping creation.')


def put_json_object_in_bucket(bucket_name: str, policy_file_name: str) -> None:
    ex.generate_lifecycle_policy_json()

    put_object_response = client.put_object(
        Body=json.dumps(ex.LIFECYCLE_POLICY_TEMPLATE),
        Bucket=bucket_name,
        Key=policy_file_name
    )


def delete_bucket(bucket_name: str) -> None:
    delete_bucket_response = client.delete_bucket(
        Bucket=bucket_name
    )
