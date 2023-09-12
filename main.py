import os
import traceback

import boto3
import json
import sys

from policy_generator import generate_lifecycle_policy_json


def lambda_handler():
    # Initialize AWS SDK ecr_client for Elastic Container Registry
    # boto3.setup_default_session(profile_name='events')
    ecr_client = boto3.client('ecr')
    ssm_client = boto3.client('ssm')

    # Get the ECR repositories versions
    ssm_response = ssm_client.get_parameter(
        Name=os.environ.get('parameter_name')
    )
    versions = ssm_response.get('Parameter').get('Value').split(',')
    versions = ['1.1.0.i1', '1.2.0.i1', '1.3.0.i1']

    # Get the available repositories from ECR
    repos = ecr_client.describe_repositories()
    print(f'Found {len(repos.get("repositories"))} repositories.')

    # Generate the JSON data
    policy_json = generate_lifecycle_policy_json(versions, 30)

    # With the generated JSON file, create the policies on all the available repos
    for repo in repos.get('repositories'):
        # Get the alpha versions and delete them
        alpha_versions = []
        response = ecr_client.list_images(
            registryId=repo.get('registryId'),
            repositoryName=repo.get('repositoryName'),
        )

        for img in response.get('imageIds'):
            alpha_image_tag = img.get('imageTag')
            for version in versions:
                if 'alpha' in alpha_image_tag and version in alpha_image_tag:
                    alpha_versions.append(alpha_image_tag)
        print(alpha_versions)

        try:
            for aver in alpha_versions:
                ecr_client.batch_delete_image(
                    registryId=repo.get('registryId'),
                    repositoryName=repo.get('repositoryName'),
                    imageIds=[
                        {
                            'imageTag': aver
                        },
                    ]
                )
        except:
            pass

        # Add the normal policies
        try:
            ecr_client.put_lifecycle_policy(
                registryId=repo.get('registryId'),
                repositoryName=repo.get('repositoryName'),
                lifecyclePolicyText=json.dumps(policy_json)
            )
            print(f'Lifecycle policies updated for repo "{repo.get("repositoryName")}".')

        except ecr_client.exceptions.ServerException:
            print('Server exception, policies not created.')
            sys.exit(1)
        except ecr_client.exceptions.InvalidParameterException:
            print('Invalid parameter passed into lifecycle policy creation.')
            sys.exit(1)
        except ecr_client.exceptions.RepositoryNotFoundException:
            print('The provided repository was not found, please provide a valid repository.')
            sys.exit(1)


if __name__ == '__main__':
    lambda_handler()
