import boto3
from datetime import timedelta, datetime


print('Loading function')


def lambda_handler(event, context):
    retention_days = 2
    deletion_days = 14

    print("AWS snapshot backups started at %s...\n" % datetime.now())
    ec = boto3.client('ec2')
    snapshot = ec.create_snapshot(
            VolumeId="vol-0e3fe6bd947540db4",
        )
    print(snapshot)
    if snapshot['State'] != "error":
        print("Snapshot creation in progress, deleting old snapshots")
        delete_fmt = (datetime.today() + timedelta(days=retention_days)).strftime("%Y-%m-%d")
        ec.create_tags(
            Resources=[snapshot["SnapshotId"]],
            Tags=[
                {'Key': 'DeleteOn', 'Value': delete_fmt},
            ]
        )
        deletion_days = [(datetime.today()-timedelta(days=i)).strftime('%Y-%m-%d') for i in range(deletion_days)]
        filters = [
            {'Name': 'tag-key', 'Values': ['DeleteOn']},
            {'Name': 'tag-value', 'Values': deletion_days},
        ]
        snapshot_response = ec.describe_snapshots(OwnerIds=["681414469766"], Filters=filters)
        print("Found {} old snapshots to delete.".format(len(snapshot_response['Snapshots'])))
        for snap in snapshot_response['Snapshots']:
            print("Deleting snapshot %s" % snap['SnapshotId'])
            ec.delete_snapshot(SnapshotId=snap['SnapshotId'])
    else:
        raise Exception("Snapshot creation did not succeed:", str(snapshot))
