import boto3
import json
import sys
import os

from policy_generator import generate_lifecycle_policy_json

bucket_name = 'idops-lambda-ecr-repos-policies'
policy_file_name = 'ecr_lifecycle_policy.json'
versions = os.environ.get('ecr_versions')


def lambda_handler():
    # Initialize AWS SDK client for Elastic Container Registry
    client = boto3.client('ecr')

    # Get the available repositories from ECR
    repos = client.describe_repositories()
    print(f'Found {len(repos.get("repositories"))} repositories.')

    # Generate the JSON data
    policy_json = generate_lifecycle_policy_json(versions)

    # With the generated JSON file, create the policies on all the available repos
    for repo in repos.get('repositories'):
        try:
            client.put_lifecycle_policy(
                registryId=repo.get('registryId'),
                repositoryName=repo.get('repositoryName'),
                lifecyclePolicyText=json.dumps(policy_json)
            )
            print(f'Lifecycle policies updated for repo "{repo.get("repositoryName")}".')

        except client.exceptions.ServerException:
            print('Server exception, policies not created.')
            sys.exit(1)
        except client.exceptions.InvalidParameterException:
            print('Invalid parameter passed into lifecycle policy creation.')
            sys.exit(1)
        except client.exceptions.RepositoryNotFoundException:
            print('The provided repository was not found, please provide a valid repository.')
            sys.exit(1)


if __name__ == '__main__':
    lambda_handler()
