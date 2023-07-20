import os
import sys
import boto3


def lambda_handler(event, context):
    # Define the regions we're working with
    main_region = 'eu-west-1'
    secondary_regions = os.environ.get('replication_regions').split(',')

    if len(secondary_regions) < 1:
        print('Please update environment variable "replication_regions" with regions, comma separated.')
        sys.exit(1)

    # Initialize the client for the main region to read the parameter store
    main_ssm_client = boto3.client('ssm', region_name=main_region)
    try:
        main_response = main_ssm_client.get_parameter(
            Name='ecr-versions-eu-west-1'
        )
        print(f'Reading data from {main_region} Parameter Store..')
    except main_ssm_client.exceptions.InternalServerError as exc:
        print('There was an issue fulfilling your request')
        print(exc)
        sys.exit(1)
    except main_ssm_client.exceptions.InvalidKeyId as exc:
        print('Invalid KeyId has been provided for the getParameter operation')
        print(exc)
        sys.exit(1)
    except main_ssm_client.exceptions.ParameterNotFound as exc:
        print('Seems like the parameter was not found')
        print(exc)
        sys.exit(1)
    except main_ssm_client.exceptions.ParameterVersionNotFound as exc:
        print('The specified parameter version was not found')
        print(exc)
        sys.exit(1)

    # For each secondary region we need a separate client
    for region in secondary_regions:
        secondary_ssm_client = boto3.client('ssm', region_name=region)
        try:
            print(f'Updating Parameter Store in region {region}..')
            secondary_ssm_client.put_parameter(
                Name=f'ecr-versions-{region}',
                Value=main_response.get('Parameter').get('Value'),
                Type='StringList',
                Overwrite=True
            )
        except secondary_ssm_client.exceptions.ParameterAlreadyExists as exc:
            print('Parameter already exists, try to overwrite or create new one')
            print(exc)
            sys.exit(1)
        except secondary_ssm_client.exceptions.ParameterMaxVersionLimitExceeded as exc:
            print('Maximum version limit for the parameter reached')
            print(exc)
            sys.exit(1)
        except secondary_ssm_client.exceptions.TooManyUpdates as exc:
            print('Too many updates on the parameter')
            print(exc)
            sys.exit(1)

    print(f'Parameter Store has been updated for {len(secondary_regions)} regions')
