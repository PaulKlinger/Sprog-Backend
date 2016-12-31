from wsgiref.handlers import format_date_time
from datetime import datetime, timedelta
from time import mktime
import boto3
import os.path


def datetime_to_http_date(dt):
    stamp = mktime(dt.timetuple())
    return format_date_time(stamp)


def upload_to_s3(tmpdir, passwords):
    cache_expire = datetime_to_http_date(datetime.now()+timedelta(hours=11))
    s3 = boto3.resource("s3", "eu-west-1",
                        aws_access_key_id=passwords["AWS_ACCESS_KEY"],
                        aws_secret_access_key=passwords["AWS_SECRET_KEY"],)
    bucket = s3.Bucket("almoturg.com")
    bucket.upload_file("sprog.pdf", "sprog.pdf",
                       ExtraArgs={'ContentType': 'application/pdf',
                                  'CacheControl': 'public',
                                  'Expires': cache_expire})
    bucket.upload_file("small_sprog.pdf", "sprog_small.pdf",
                       ExtraArgs={'ContentType': 'application/pdf',
                                  'CacheControl': 'public',
                                  'Expires': cache_expire})
    bucket.upload_file(os.path.join(tmpdir, "sprog.html"), "sprog",
                       ExtraArgs={'ContentType': 'text/html',
                                  'CacheControl': 'public',
                                  'Expires': cache_expire})
    now = datetime.now()
    if now.weekday() == 2:  # backup poems on wednesday
        bucket.upload_file("poems.json",
                           "poems_{}_{:02d}_{:02d}.json".format(now.year, now.month, now.day))
        bucket.upload_file("deleted_poems.json",
                           "deleted_poems_{}_{:02d}_{:02d}.json".format(now.year, now.month, now.day))
