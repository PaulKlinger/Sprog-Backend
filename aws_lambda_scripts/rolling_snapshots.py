import boto3
from datetime import timedelta, datetime


print('Loading function')

def lambda_handler(event, context):

    retention_days = 2

    print("AWS snapshot backups stated at %s...\n" % datetime.now())
    ec = boto3.client('ec2')
    snapshot = ec.create_snapshot(
            VolumeId="vol-0e3fe6bd947540db4",
        )
    if snapshot:
        delete_fmt = (datetime.today() + timedelta(days=retention_days)).strftime("%Y-%m-%d")
        ec.create_tags(
            Resources=[snapshot["SnapshotId"]],
            Tags=[
                {'Key': 'DeleteOn', 'Value': delete_fmt},
            ]
        )
        today = datetime.today().strftime('%Y-%m-%d')
        yest = (datetime.today()-timedelta(days=1)).strftime('%Y-%m-%d')
        yyest = (datetime.today()-timedelta(days=2)).strftime('%Y-%m-%d')
        filters = [
            {'Name': 'tag-key', 'Values': ['DeleteOn']},
            {'Name': 'tag-value', 'Values': [today, yest, yyest]},
        ]
        snapshot_response = ec.describe_snapshots(OwnerIds=["681414469766"], Filters=filters)
        for snap in snapshot_response['Snapshots']:
            print("Deleting snapshot %s" % snap['SnapshotId'])
            ec.delete_snapshot(SnapshotId=snap['SnapshotId'])
    else:
        raise Exception("Snapshot creation did not succeed:", str(snapshot))
