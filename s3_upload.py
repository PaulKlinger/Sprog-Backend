from wsgiref.handlers import format_date_time
from datetime import datetime, timedelta
from time import mktime
import boto3

AWS_ACCESS_KEY = "***REMOVED***"
AWS_SECRET_KEY = "***REMOVED***"


def datetime_to_http_date(dt):
    stamp = mktime(dt.timetuple())
    return format_date_time(stamp)


def upload_to_s3():
    cache_expire = datetime_to_http_date(datetime.now()+timedelta(hours=11))
    s3 = boto3.resource("s3", "eu-west-1",
                        aws_access_key_id=AWS_ACCESS_KEY,
                        aws_secret_access_key=AWS_SECRET_KEY,)
    bucket = s3.Bucket("almoturg.com")
    bucket.upload_file("sprog.pdf", "sprog.pdf",
                       ExtraArgs={'ContentType': 'application/pdf',
                                  'CacheControl': 'public',
                                  'Expires': cache_expire})
    bucket.upload_file("small_sprog.pdf", "sprog_small.pdf",
                       ExtraArgs={'ContentType': 'application/pdf',
                                  'CacheControl': 'public',
                                  'Expires': cache_expire})
    bucket.upload_file("tmp/sprog.html", "sprog",
                       ExtraArgs={'ContentType': 'text/html',
                                  'CacheControl': 'public',
                                  'Expires': cache_expire})