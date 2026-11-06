import boto3


def lambda_handler(event, context):
    ec = boto3.client('ec2')
    response = ec.start_instances(
        InstanceIds=[
            'i-08ac4dc4d1a25b815',
        ],
        DryRun=False
    )