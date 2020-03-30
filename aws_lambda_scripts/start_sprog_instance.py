import boto3


def lambda_handler(event, context):
    ec = boto3.client('ec2')
    response = ec.start_instances(
        InstanceIds=[
            'i-00c8bff4207d0e201',
        ],
        DryRun=False
    )